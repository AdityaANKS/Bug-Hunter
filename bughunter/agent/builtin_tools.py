"""Agent built-in tools and OpenAI tool schema helpers."""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import urlparse

from bughunter.agent.constraint_policy import validate_tool_action

BLOCKED_PATTERNS: list[str] = [
    r"os\.\s*system\s*\(",
    r"subprocess\.\s*Popen\s*\(",
    r"shutil\.\s*rmtree\s*\(",
    r"__import__\s*\(\s*['\"]os['\"]",
    r"open\s*\(\s*['\"].*bughunter.*config",
    r"open\s*\(\s*['\"].*\.bughunter",
]

RESERVED_IP_RANGES: list[tuple[str, str, str]] = [
    ("198.18.0.0", "198.19.255.255", "RFC 2544 Benchmark address"),
    ("10.0.0.0", "10.255.255.255", "RFC 1918 private address"),
    ("172.16.0.0", "172.31.255.255", "RFC 1918 private address"),
    ("192.168.0.0", "192.168.255.255", "RFC 1918 private address"),
    ("127.0.0.0", "127.255.255.255", "RFC 1122 loopback address"),
    ("169.254.0.0", "169.254.255.255", "RFC 3927 link local"),
    ("0.0.0.0", "0.255.255.255", "RFC 1122 current network"),
    ("224.0.0.0", "239.255.255.255", "RFC 5771 multicast address"),
    ("240.0.0.0", "255.255.255.255", "RFC 1112 reserved address"),
]

SAFE_MODE_PATTERNS: list[str] = [
    r"open\s*\(",
    r"with\s+open\s*\(",
    r"socket\.",
    r"urllib",
    r"http\.client",
    r"ftplib",
    r"smtplib",
    r"requests\.",
    r"import\s+os",
    r"from\s+os\s+import",
    r"import\s+subprocess",
    r"from\s+subprocess\s+import",
    r"import\s+shutil",
    r"from\s+shutil\s+import",
    r"import\s+pathlib",
    r"from\s+pathlib\s+import",
    r"__import__",
]

LAB_MODE_PATTERNS: list[str] = [
    r"import\s+subprocess",
    r"from\s+subprocess\s+import",
    r"os\.\s*system\s*\(",
    r"subprocess\.\s*Popen\s*\(",
    r"shutil\.\s*rmtree\s*\(",
]


async def execute_mcp_tool(agent: Any, tool_name: str, args: dict[str, Any]) -> str:
    """Execute a tool call via MCP manager or built-in tools."""
    session = getattr(agent, "session_state", None)
    constraints = getattr(session, "task_constraints", None)
    if constraints is not None:
        tool_violation = validate_tool_action(tool_name, args, constraints)
        if tool_violation is not None:
            if session is not None and hasattr(session, "add_constraint_violation_event"):
                from bughunter.agent.constraint_policy import infer_tool_action

                session.add_constraint_violation_event(
                    source="tool",
                    action=infer_tool_action(tool_name, args),
                    tool_name=tool_name,
                    code="tool_action_blocked",
                    severity="high",
                    summary=tool_violation,
                    detail=json.dumps(args, ensure_ascii=False)[:500],
                )
            return f"[constraint_violation] {tool_violation}"

    if tool_name == "python_execute":
        return await execute_python(agent, args)

    if tool_name == "load_skill_reference":
        try:
            from bughunter.skills.loader import load_skill_reference

            skill_name = args.get("skill_name", "")
            ref_name = args.get("reference_name", "")
            content = load_skill_reference(skill_name, ref_name)
            if content:
                return content
            return f"[!] Reference document not found: {skill_name}/{ref_name}"
        except Exception as e:
            return f"[!] Failed to load reference document: {e}"

    if tool_name == "nmap_scan":
        return await execute_nmap(agent, args)

    if tool_name == "crypto_decode":
        try:
            from bughunter.skills.crypto_tools import execute as crypto_execute

            operation = args.get("operation", "")
            input_str = args.get("input", "")
            kwargs: dict[str, Any] = {}
            for key in ("key", "iv", "shift", "secret", "header", "algorithm"):
                if key in args and args[key]:
                    kwargs[key] = args[key]
                    if key == "shift":
                        kwargs[key] = int(args[key])
            result = crypto_execute(operation=operation, input_str=input_str, **kwargs)
            if result.get("success"):
                return f"[✓] {operation} Result:\n{result['result']}"
            return f"[!] {operation} Failed: {result.get('error', 'unknown error')}"
        except Exception as e:
            return f"[!] Crypto tool execution error: {e}"

    if tool_name == "spawn_subagents":
        return await _execute_spawn_subagents(agent, args)

    if tool_name == "brute_force_login":
        return await execute_brute_force(agent, args)

    if tool_name == "kali_sandbox_execute":
        return await execute_kali_sandbox(agent, args)

    # ── 8 new first-class sandbox tools ──────────────────────────────────────
    _SANDBOX_TOOL_NAMES = {
        "nuclei_scan", "sqlmap_scan", "ffuf_fuzz", "xss_scan",
        "crawl_urls", "param_discover", "httpx_probe", "wpscan_scan",
    }
    if tool_name in _SANDBOX_TOOL_NAMES:
        _SANDBOX_TOOL_TIMEOUT = 180  # seconds
        handler = {
            "nuclei_scan": execute_nuclei,
            "sqlmap_scan": execute_sqlmap,
            "ffuf_fuzz": execute_ffuf,
            "xss_scan": execute_xss_scan,
            "crawl_urls": execute_crawl_urls,
            "param_discover": execute_param_discover,
            "httpx_probe": execute_httpx_probe,
            "wpscan_scan": execute_wpscan,
        }[tool_name]
        try:
            return await asyncio.wait_for(
                handler(agent, args),
                timeout=_SANDBOX_TOOL_TIMEOUT,
            )
        except asyncio.TimeoutError:
            return (
                f"[!] {tool_name} timed out after {_SANDBOX_TOOL_TIMEOUT}s. "
                f"Partial results may be available. Consider narrowing scope."
            )
        except Exception as e:
            return f"[!] Tool execution error ({tool_name}): {e}"

    if tool_name in {"space_search", "subdomain_enum", "js_recon", "dir_enum", "unauth_test"}:
        from bughunter.agent import recon_tools

        dispatch = {
            "space_search": recon_tools.execute_space_search,
            "subdomain_enum": recon_tools.execute_subdomain_enum,
            "js_recon": recon_tools.execute_js_recon,
            "dir_enum": recon_tools.execute_dir_enum,
            "unauth_test": recon_tools.execute_unauth_test,
        }
        # Hard timeout per recon tool — prevents hanging forever on large scans
        _RECON_TOOL_TIMEOUT = 120  # seconds
        try:
            return await asyncio.wait_for(
                dispatch[tool_name](agent, args),
                timeout=_RECON_TOOL_TIMEOUT,
            )
        except asyncio.TimeoutError:
            return (
                f"[!] {tool_name} timed out after {_RECON_TOOL_TIMEOUT}s. "
                f"Partial results may be available. Consider narrowing scope."
            )
        except Exception as e:
            return f"[!] Tool execution error ({tool_name}): {e}"

    # ── Guard against hallucinated / unknown tool names ──────────────────
    _ALL_BUILTIN_NAMES = {
        "python_execute", "load_skill_reference", "nmap_scan", "crypto_decode",
        "spawn_subagents", "brute_force_login", "kali_sandbox_execute",
        "nuclei_scan", "sqlmap_scan", "ffuf_fuzz", "xss_scan",
        "crawl_urls", "param_discover", "httpx_probe", "wpscan_scan",
        "space_search", "subdomain_enum", "js_recon", "dir_enum", "unauth_test",
    }
    if tool_name not in _ALL_BUILTIN_NAMES and not agent.mcp_manager:
        return (
            f"[!] Unknown tool '{tool_name}'. This tool does not exist. "
            f"Available tools: {', '.join(sorted(_ALL_BUILTIN_NAMES))}. "
            f"Do NOT invent tool names. If you need to continue a previous session, "
            f"just start scanning the target directly — there is no 'retrieve' or 'memory' tool."
        )

    if not agent.mcp_manager:
        return f"[!] MCP Manager is not initialized, cannot execute tool: {tool_name}"

    try:
        result = await agent.mcp_manager.call_tool(tool_name, args)
        if isinstance(result, dict):
            if result.get("ok", False):
                content = result.get("content")
                structured = result.get("structured_content")
                summary_parts: list[str] = []
                if content is not None:
                    summary_parts.append(str(content))
                if isinstance(structured, dict) and structured:
                    summary_parts.append(
                        f"[structured] {json.dumps(structured, ensure_ascii=False)}"
                    )
                if summary_parts:
                    return "\n".join(summary_parts)
                return f"[tool:{tool_name}] completed"

            message = str(result.get("message") or "")
            suggestion = str(result.get("suggestion") or "")
            error_type = str(result.get("error_type") or "error")
            if suggestion:
                return f"[{error_type}] {message}\n[suggestion] {suggestion}".strip()
            return f"[{error_type}] {message}".strip()

        text = str(result)
        if text.strip() in ("undefined", "null", "None"):
            return f"[!] Tool {tool_name} returned null result (undefined), the call may have failed"
        return text
    except Exception as e:
        return f"[!] Tool execution error ({tool_name}): {e}"


def enforce_port_constraints(agent: Any, ports: list[int], *, target: str = "") -> str | None:
    """Return a user-facing violation message when requested ports are out of scope."""
    session = getattr(agent, "session_state", None)
    constraints = getattr(session, "task_constraints", None)
    if constraints is None or constraints.is_empty():
        return None

    if constraints.allowed_ports:
        disallowed = [port for port in ports if port not in constraints.allowed_ports]
        if disallowed:
            allowed = ", ".join(str(p) for p in constraints.allowed_ports)
            denied = ", ".join(str(p) for p in disallowed)
            suffix = f" for target {target}" if target else ""
            return f"[constraint_violation] Port(s) {denied} are outside allowed scope [{allowed}]{suffix}."

    blocked = [port for port in ports if port in constraints.blocked_ports]
    if blocked:
        denied = ", ".join(str(p) for p in blocked)
        suffix = f" for target {target}" if target else ""
        return f"[constraint_violation] Port(s) {denied} are blocked by task constraints{suffix}."

    return None


def enforce_host_path_constraints(
    agent: Any, *, host: str = "", path: str = "", target: str = ""
) -> str | None:
    """Return a user-facing violation when host/path are out of scope."""
    session = getattr(agent, "session_state", None)
    constraints = getattr(session, "task_constraints", None)
    if constraints is None or constraints.is_empty():
        return None

    if constraints.allowed_hosts and host and host not in constraints.allowed_hosts:
        allowed = ", ".join(constraints.allowed_hosts)
        return f"[constraint_violation] Host {host} is outside allowed scope [{allowed}] for target {target or host}."

    if host and host in constraints.blocked_hosts:
        return f"[constraint_violation] Host {host} is blocked by task constraints for target {target or host}."

    if constraints.allowed_paths and path and path not in constraints.allowed_paths:
        allowed = ", ".join(constraints.allowed_paths)
        return f"[constraint_violation] Path {path} is outside allowed scope [{allowed}] for target {target or host}."

    if path and path in constraints.blocked_paths:
        return f"[constraint_violation] Path {path} is blocked by task constraints for target {target or host}."

    return None


def infer_ports_from_nmap_args(args: dict[str, Any]) -> list[int]:
    """Infer concrete target ports from nmap arguments for constraint checks."""
    custom_ports = str(args.get("ports", "") or "").strip()
    scan_type = str(args.get("scan_type", "top_ports") or "top_ports")

    if custom_ports:
        ports: list[int] = []
        for chunk in custom_ports.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            if "-" in chunk:
                start_text, end_text = chunk.split("-", 1)
                try:
                    start = int(start_text)
                    end = int(end_text)
                except ValueError:
                    continue
                if 0 < start <= end <= 65535:
                    ports.extend(range(start, end + 1))
                continue
            try:
                port = int(chunk)
            except ValueError:
                continue
            if 0 < port <= 65535:
                ports.append(port)
        return sorted(set(ports))

    if scan_type == "top_ports":
        return []
    return []


def infer_port_from_url(url: str) -> int | None:
    """Infer request port from URL."""
    try:
        parsed = urlparse(url)
    except Exception:
        return None
    if parsed.port:
        return parsed.port
    if parsed.scheme == "https":
        return 443
    if parsed.scheme == "http":
        return 80
    return None


def build_openai_tools(mcp_manager: Any) -> list[dict[str, Any]]:
    """Build OpenAI function calling schema from MCP tools + built-in tools."""
    tools: list[dict[str, Any]] = []

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "load_skill_reference",
                "description": "Load a named skill reference document to get detailed penetration testing methodology, workflow guides, or command references. Use this tool when the system prompt mentions 'available reference documents'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_name": {
                            "type": "string",
                            "description": "Skill name, e.g. client-reverse, web-security-advanced, ai-mcp-security, intranet-pentest-advanced, pentest-tools, rapid-checklist, crypto-toolkit, ctf-web, ctf-crypto, ctf-misc, osint-recon, secknowledge-skill",
                        },
                        "reference_name": {
                            "type": "string",
                            "description": "Reference document filename, e.g. 02-client-api-reverse-and-burp.md, web-injection.md, encoding-cheatsheet.md",
                        },
                    },
                    "required": ["skill_name", "reference_name"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "python_execute",
                "description": (
                    "Execute a Python code snippet. Use for: constructing complex HTTP requests and parsing responses, "
                    "encoding transformations and data processing, batch-testing different payloads, comparing response differences, "
                    "performing mathematical calculations, etc. Code runs in a restricted environment with a 30-second timeout. "
                    "Pre-installed libraries: requests, beautifulsoup4, pycryptodome, base64, json, re, etc. "
                    "IMPORTANT: Use this tool to construct HTTP requests instead of guessing what the response will be."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code to execute. Supports multiple lines, can import standard library and requests/bs4 etc.",
                        },
                        "purpose": {
                            "type": "string",
                            "description": "Brief description of the execution purpose (for audit logging), e.g. 'Construct HTTP request to test weak comparison bypass'",
                        },
                    },
                    "required": ["code"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "crypto_decode",
                "description": (
                    "Encoding/decoding and encryption/decryption tool. Use when encountering base64/hex/URL/HTML/Unicode encoded strings, "
                    "computing hashes, decrypting AES/DES, or parsing JWT tokens. "
                    "IMPORTANT: Do NOT guess decoding results — always use this tool to ensure accuracy. "
                    "Supported operations: base64_encode/decode, base32_encode/decode, base58_encode/decode, "
                    "hex_encode/decode, url_encode/decode, html_encode/decode, unicode_encode/decode, "
                    "rot13_encode/decode, caesar_encode/decode, morse_encode/decode, "
                    "md5_hash, sha1_hash, sha256_hash, sha512_hash, "
                    "aes_encrypt/decrypt, jwt_decode/encode, auto_decode"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "description": "Operation name (e.g. base64_decode, md5_hash, aes_decrypt)"},
                        "input": {
                            "type": "string",
                            "description": "Input string to encode/decode/hash/encrypt",
                        },
                        "key": {
                            "type": "string",
                            "description": "Encryption/decryption key (required for AES/DES, 16/24/32 bytes)",
                        },
                        "iv": {"type": "string", "description": "AES initialization vector (16 bytes, optional)"},
                        "shift": {
                            "type": "integer",
                            "description": "Caesar cipher shift offset (default 3; if not provided during decoding, brute-forces all shifts)",
                        },
                        "secret": {"type": "string", "description": "JWT signing secret key"},
                    },
                    "required": ["operation", "input"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "nmap_scan",
                "description": (
                    "Nmap network port scanning tool. Use during reconnaissance to discover open ports, service versions, and OS fingerprints.\n"
                    "Usage examples:\n"
                    "  Common ports: scan_type=top_ports, target=1.2.3.4\n"
                    "  SYN scan: scan_type=syn, target=1.2.3.4 (requires root)\n"
                    "  Service detection: scan_type=service, target=1.2.3.4\n"
                    "  Vulnerability scan: scan_type=vuln, target=1.2.3.4\n"
                    "  Full scan: scan_type=full, target=1.2.3.4\n"
                    "Prefer nmap_scan over python_execute for socket scanning — nmap is more professional and accurate."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "Target IP address or domain name (required), e.g. 192.168.1.1 or scanme.nmap.org",
                        },
                        "scan_type": {
                            "type": "string",
                            "description": "Scan type: top_ports/syn/tcp/service/os/vuln/full",
                        },
                        "ports": {
                            "type": "string",
                            "description": "Port specification or range (optional), e.g. 80,443,8080 or 1-1000",
                        },
                        "timing": {
                            "type": "integer",
                            "description": "Scan speed template 0-5 (default 4). Higher = faster but easier to detect.",
                        },
                    },
                    "required": ["target"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "brute_force_login",
                "description": (
                    "Password brute-force attack on login forms. Automatically manages session cookies, "
                    "extracts and refreshes CSRF tokens, and determines login success/failure. "
                    "Completes all password attempts within a single call and returns results for each password."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Login page URL",
                        },
                        "username_field": {
                            "type": "string",
                            "description": "Username field name, e.g. 'username'",
                        },
                        "password_field": {
                            "type": "string",
                            "description": "Password field name, e.g. 'password'",
                        },
                        "csrf_field": {
                            "type": "string",
                            "description": "CSRF token field name, e.g. 'user_token'",
                        },
                        "username": {
                            "type": "string",
                            "description": "Target username to brute-force",
                        },
                        "passwords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of passwords to try (up to 20)",
                        },
                        "success_keyword": {
                            "type": "string",
                            "description": "Keyword indicating successful login on the response page, e.g. 'Welcome', 'Dashboard'",
                        },
                        "failure_keyword": {
                            "type": "string",
                            "description": "Keyword indicating failed login on the response page, e.g. 'Login failed'",
                        },
                        "submit_action": {
                            "type": "string",
                            "description": "Form submission target URL (optional; if omitted, extracts from form action attribute)",
                        },
                        "extra_data": {
                            "type": "object",
                            "description": "Additional form fields, e.g. {\"Login\": \"Login\"}",
                        },
                    },
                    "required": ["url", "password_field", "passwords"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "space_search",
                "description": (
                    "Cyberspace asset search engine (FOFA/Hunter/Quake/Shodan/ZoomEye/0.zone). "
                    "Use during reconnaissance to passively discover target assets, IPs, ports, subdomains, titles, and component fingerprints without direct contact. "
                    "Provide a domain to auto-construct engine-specific queries, or supply raw query syntax. "
                    "Set engine=all to concurrently query all configured engines."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "engine": {
                            "type": "string",
                            "description": "fofa/hunter/quake/shodan/zoomeye/zerozone/all (default fofa)",
                        },
                        "query": {
                            "type": "string",
                            "description": "Engine-native query syntax, e.g. 'domain=\"x.com\"', 'app=\"Struts2\"' (optional)",
                        },
                        "domain": {
                            "type": "string",
                            "description": "Target primary domain name; auto-constructs engine-specific domain queries (use when query is not given)",
                        },
                        "size": {"type": "integer", "description": "Number of results to return (default 100)"},
                    },
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "subdomain_enum",
                "description": (
                    "Subdomain enumeration. First passively aggregates from configured cyberspace search engines, "
                    "then optionally brute-forces with a built-in DNS dictionary. "
                    "Returns a deduplicated list of live subdomains. Prefer this over writing custom DNS brute-force in python_execute."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "Primary domain name, e.g. example.com"},
                        "brute": {
                            "type": "boolean",
                            "description": "Enable built-in dictionary DNS brute-force (default true)",
                        },
                    },
                    "required": ["domain"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "js_recon",
                "description": (
                    "JS reconnaissance (inspired by URLFinder). Crawls the target page and all referenced .js files to extract: "
                    "API endpoints/paths, associated domain names, absolute URLs, and suspected hardcoded secrets (AK/SK, tokens, JWT, private keys, etc.). "
                    "Default auto_probe=true: automatically probes collected same-origin endpoints for unauthorized access (safe GET only, skips destructive operations). "
                    "Prioritize calling this during reconnaissance to feed real extracted endpoints into subsequent tests, rather than guessing interfaces."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target page URL"},
                        "max_js": {
                            "type": "integer",
                            "description": "Maximum number of JS files to crawl (default 30)",
                        },
                        "auto_probe": {
                            "type": "boolean",
                            "description": "Automatically probe collected endpoints for unauthorized access (default true)",
                        },
                        "auth_header": {
                            "type": "string",
                            "description": "Optional auth header for differential comparison, e.g. 'Authorization: Bearer xxx' — verifies whether data is accessible without token",
                        },
                    },
                    "required": ["url"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "unauth_test",
                "description": (
                    "Unauthorized access detection. Probes a batch of endpoints (typically from js_recon) without credentials, "
                    "classifying each by status code/body/content-type: ⚠ suspected unauthorized (returns data) / ✓ auth enforced / ↪ redirect to login / — not found. "
                    "When auth_header is supplied, performs differential comparison with/without token — if data is accessible without token, confirms 🔴 unauthorized. "
                    "Strictly read-only: only safe GET requests, automatically skips destructive endpoints (delete/update/sms etc.)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "base_url": {"type": "string", "description": "Target base URL (defines same-origin scope)"},
                        "endpoints": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of endpoint paths/URLs to test (from js_recon endpoint/path output)",
                        },
                        "auth_header": {
                            "type": "string",
                            "description": "Optional auth header for differential comparison, e.g. 'Authorization: Bearer xxx' or 'Cookie: session=...'",
                        },
                        "max_endpoints": {
                            "type": "integer",
                            "description": "Maximum number of endpoints to probe (default 60)",
                        },
                    },
                    "required": ["base_url", "endpoints"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "dir_enum",
                "description": (
                    "Directory/file enumeration (inspired by dirsearch). Concurrent dictionary brute-force with built-in 404 baseline and "
                    "global fake-response detection (random path returning 200 = WAF/custom 404 detected, stops automatically). "
                    "Filters by status code and response length. Only safe GET probes, never touches destructive paths."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target base URL, e.g. https://example.com/"},
                        "extensions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File extensions to append, e.g. ['php','jsp','bak','zip'] (optional)",
                        },
                        "wordlist": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Additional custom paths to test (optional, supplements built-in wordlist)",
                        },
                    },
                    "required": ["url"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "nuclei_scan",
                "description": (
                    "Nuclei vulnerability scanner — the single most impactful automated scanning tool for bug bounty. "
                    "Scans targets using community-maintained YAML templates covering: known CVEs, exposed panels, "
                    "misconfigurations, default credentials, info leaks, takeovers, and more. "
                    "Prefer this over manual testing when checking for known vulnerabilities.\n"
                    "Examples:\n"
                    "  Scan for critical CVEs: target=https://example.com, templates=cves, severity=critical\n"
                    "  Scan exposed panels: target=https://example.com, templates=exposed-panels\n"
                    "  Full default scan: target=https://example.com\n"
                    "  Scan with specific template: templates=http/cves/2021/CVE-2021-44228"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "Target URL or host to scan, e.g. https://example.com",
                        },
                        "templates": {
                            "type": "string",
                            "description": "Template category or path: cves, exposed-panels, misconfiguration, default-logins, takeovers, technologies, or a specific template path",
                        },
                        "severity": {
                            "type": "string",
                            "description": "Filter by severity: critical, high, medium, low, info (comma-separated for multiple)",
                        },
                        "rate_limit": {
                            "type": "integer",
                            "description": "Max requests per second (default 150, lower for stealth)",
                        },
                        "tags": {
                            "type": "string",
                            "description": "Filter templates by tags, e.g. 'rce,sqli,xss,lfi,ssrf,redirect'",
                        },
                    },
                    "required": ["target"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "sqlmap_scan",
                "description": (
                    "SQLMap — automated SQL injection detection and exploitation tool. "
                    "Detects and exploits SQL injection flaws across all major DBMS types. "
                    "Use when you suspect a parameter is vulnerable to SQL injection.\n"
                    "Examples:\n"
                    "  GET parameter: url=http://example.com/page?id=1\n"
                    "  POST data: url=http://example.com/login, data=user=admin&pass=test\n"
                    "  With cookie: url=http://example.com/api, cookie=session=abc123\n"
                    "  Specific param: url=http://example.com/page?id=1&name=test, param=id"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Target URL with injectable parameter, e.g. http://example.com/page?id=1",
                        },
                        "data": {
                            "type": "string",
                            "description": "POST request body data, e.g. 'user=admin&pass=test'",
                        },
                        "param": {
                            "type": "string",
                            "description": "Specific parameter to test (optional; tests all if omitted)",
                        },
                        "cookie": {
                            "type": "string",
                            "description": "HTTP cookie string, e.g. 'PHPSESSID=abc; security=low'",
                        },
                        "level": {
                            "type": "integer",
                            "description": "Test level 1-5 (default 1). Higher = more payloads tested (2+ tests cookies, 3+ tests User-Agent/Referer)",
                        },
                        "risk": {
                            "type": "integer",
                            "description": "Risk level 1-3 (default 1). Higher = more aggressive payloads (2+ heavy time-based, 3+ OR-based)",
                        },
                        "technique": {
                            "type": "string",
                            "description": "SQL injection techniques: B=Boolean, E=Error, U=Union, S=Stacked, T=Time, Q=Inline (default BEUSTQ)",
                        },
                        "tamper": {
                            "type": "string",
                            "description": "Tamper script(s) for WAF bypass, e.g. 'space2comment,between,randomcase'",
                        },
                        "dbms": {
                            "type": "string",
                            "description": "Force target DBMS type: MySQL, PostgreSQL, Oracle, MSSQL, SQLite",
                        },
                    },
                    "required": ["url"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "ffuf_fuzz",
                "description": (
                    "Ffuf — fast web fuzzer for directory/file discovery, parameter brute-forcing, and vhost enumeration. "
                    "More powerful than the built-in dir_enum. Place the keyword FUZZ in the URL/headers/data where you want substitution.\n"
                    "Examples:\n"
                    "  Directory discovery: url=https://example.com/FUZZ, wordlist=common\n"
                    "  Parameter fuzzing: url=https://example.com/api?FUZZ=test\n"
                    "  Vhost discovery: url=https://example.com, wordlist=subdomains (with Host header)\n"
                    "  POST data: url=https://example.com/login, method=POST, data=user=admin&pass=FUZZ"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Target URL with FUZZ keyword for substitution, e.g. https://example.com/FUZZ",
                        },
                        "wordlist": {
                            "type": "string",
                            "description": "Wordlist name or path. Built-in: 'common' (/usr/share/seclists/Discovery/Web-Content/common.txt), 'big', 'raft-large', 'api-endpoints', 'subdomains'. Or full path.",
                        },
                        "method": {
                            "type": "string",
                            "description": "HTTP method (default GET)",
                        },
                        "headers": {
                            "type": "string",
                            "description": "Custom headers, e.g. 'Host: FUZZ.example.com' or 'Cookie: session=abc'",
                        },
                        "data": {
                            "type": "string",
                            "description": "POST request body, e.g. 'user=admin&pass=FUZZ'",
                        },
                        "filter_code": {
                            "type": "string",
                            "description": "Filter OUT responses with these status codes, e.g. '404,403,500'",
                        },
                        "filter_size": {
                            "type": "string",
                            "description": "Filter OUT responses with this content length, e.g. '0,1234'",
                        },
                        "match_code": {
                            "type": "string",
                            "description": "Only SHOW responses with these status codes, e.g. '200,301,302'",
                        },
                        "rate": {
                            "type": "integer",
                            "description": "Requests per second rate limit (default 0 = unlimited)",
                        },
                    },
                    "required": ["url"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "xss_scan",
                "description": (
                    "Dalfox — advanced XSS (Cross-Site Scripting) scanner and parameter analyzer. "
                    "Detects reflected, stored, and blind XSS vulnerabilities with DOM-based analysis. "
                    "Use when you have a URL with user-controllable parameters to test for XSS.\n"
                    "Examples:\n"
                    "  URL with params: url=https://example.com/search?q=test\n"
                    "  Specific param: url=https://example.com/page, param=name\n"
                    "  Blind XSS: url=https://example.com/contact, blind_url=https://your.xss.ht\n"
                    "  With auth: url=https://example.com/profile?bio=test, cookie=session=abc123"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Target URL with parameters to test, e.g. https://example.com/search?q=test",
                        },
                        "param": {
                            "type": "string",
                            "description": "Specific parameter to test (optional; tests all params if omitted)",
                        },
                        "cookie": {
                            "type": "string",
                            "description": "HTTP cookie string for authenticated scanning",
                        },
                        "header": {
                            "type": "string",
                            "description": "Custom HTTP header, e.g. 'Authorization: Bearer xxx'",
                        },
                        "blind_url": {
                            "type": "string",
                            "description": "Blind XSS callback URL (e.g. from xss.ht, Burp Collaborator)",
                        },
                        "custom_payload": {
                            "type": "string",
                            "description": "Custom XSS payload to inject, e.g. '<script>alert(1)</script>'",
                        },
                    },
                    "required": ["url"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "crawl_urls",
                "description": (
                    "URL and endpoint collection combining Katana (active crawler) and Gau (passive archive fetcher). "
                    "Discovers all reachable URLs, JS files, API endpoints, and form actions from a target domain. "
                    "Essential first step before fuzzing, parameter testing, or vulnerability scanning — feeds discovered URLs to other tools.\n"
                    "Examples:\n"
                    "  Active crawl: target=https://example.com\n"
                    "  With Wayback/archive URLs: target=example.com, include_wayback=true\n"
                    "  Deep crawl with JS parsing: target=https://example.com, depth=5, js_crawl=true"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "Target URL or domain to crawl, e.g. https://example.com or example.com",
                        },
                        "depth": {
                            "type": "integer",
                            "description": "Maximum crawl depth (default 3)",
                        },
                        "scope": {
                            "type": "string",
                            "description": "Crawl scope: 'strict' (same host only) or 'fuzzy' (same domain including subdomains). Default 'strict'",
                        },
                        "include_wayback": {
                            "type": "boolean",
                            "description": "Also fetch historical URLs from Wayback Machine/Common Crawl/OTX via Gau (default false)",
                        },
                        "js_crawl": {
                            "type": "boolean",
                            "description": "Enable headless browser-based JS rendering for crawling (default false, slower but finds more)",
                        },
                    },
                    "required": ["target"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "param_discover",
                "description": (
                    "Hidden parameter discovery using Arjun. Finds undocumented GET/POST/JSON parameters "
                    "that the web application accepts but doesn't advertise. Hidden parameters are often "
                    "less protected and may lead to IDOR, privilege escalation, debug modes, or injection points.\n"
                    "Examples:\n"
                    "  GET params: url=https://example.com/api/user\n"
                    "  POST params: url=https://example.com/api/user, method=POST\n"
                    "  JSON body: url=https://example.com/api/user, method=JSON"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Target URL to discover parameters for",
                        },
                        "method": {
                            "type": "string",
                            "description": "HTTP method: GET, POST, JSON, or XML (default GET)",
                        },
                        "wordlist": {
                            "type": "string",
                            "description": "Custom parameter wordlist path (optional; uses Arjun built-in by default)",
                        },
                        "headers": {
                            "type": "string",
                            "description": "Custom headers as JSON string, e.g. '{\"Cookie\": \"session=abc\"}'",
                        },
                        "rate": {
                            "type": "integer",
                            "description": "Max requests per second (default 0 = no limit)",
                        },
                    },
                    "required": ["url"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "httpx_probe",
                "description": (
                    "Httpx — fast HTTP probing tool for live host detection and technology fingerprinting. "
                    "Takes a list of hosts/IPs/URLs and probes them to identify live web services, "
                    "extracting status codes, page titles, content lengths, tech stack, and more. "
                    "Essential for filtering subdomain lists down to live targets.\n"
                    "Examples:\n"
                    "  Probe subdomains: targets=['sub1.example.com','sub2.example.com']\n"
                    "  With tech detect: targets=['https://example.com'], tech_detect=true\n"
                    "  Custom ports: targets=['example.com'], ports='80,443,8080,8443'"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "targets": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of hosts/URLs to probe for live HTTP services",
                        },
                        "ports": {
                            "type": "string",
                            "description": "Ports to probe, e.g. '80,443,8080,8443' (default: 80,443)",
                        },
                        "title": {
                            "type": "boolean",
                            "description": "Extract page titles (default true)",
                        },
                        "status_code": {
                            "type": "boolean",
                            "description": "Show status codes (default true)",
                        },
                        "tech_detect": {
                            "type": "boolean",
                            "description": "Enable technology detection via Wappalyzer (default false)",
                        },
                        "content_length": {
                            "type": "boolean",
                            "description": "Show response content length (default false)",
                        },
                        "follow_redirects": {
                            "type": "boolean",
                            "description": "Follow HTTP redirects (default true)",
                        },
                    },
                    "required": ["targets"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "wpscan_scan",
                "description": (
                    "WPScan — WordPress security scanner. Detects vulnerable plugins, themes, and WordPress core versions, "
                    "enumerates users, finds exposed files, and checks for known CVEs. "
                    "Use when the target runs WordPress (detected via whatweb, Wappalyzer, or wp-content paths).\n"
                    "Examples:\n"
                    "  Basic scan: url=https://wordpress-site.com\n"
                    "  Enumerate users: url=https://wordpress-site.com, enumerate=u\n"
                    "  Enumerate plugins: url=https://wordpress-site.com, enumerate=ap\n"
                    "  Full enum: url=https://wordpress-site.com, enumerate=u,ap,at,tt,cb,dbe"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Target WordPress site URL, e.g. https://wordpress-site.com",
                        },
                        "enumerate": {
                            "type": "string",
                            "description": "What to enumerate: u=users, ap=all-plugins, vp=vulnerable-plugins, at=all-themes, vt=vulnerable-themes, tt=timthumbs, cb=config-backups, dbe=db-exports (comma-separated)",
                        },
                        "api_token": {
                            "type": "string",
                            "description": "WPScan API token for vulnerability data (optional but recommended for CVE lookup)",
                        },
                    },
                    "required": ["url"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "kali_sandbox_execute",
                "description": (
                    "Execute a bash command inside a dedicated Kali Linux sandbox container with 100+ pre-installed security tools. "
                    "Use this for ANY security tool not exposed as a dedicated agent tool above.\n"
                    "TOOL CATALOG (by category):\n"
                    "  [Recon] amass, subfinder, assetfinder, theharvester, recon-ng, spiderfoot, dnsenum, dnsrecon, fierce, sublist3r, massdns, whois, enum4linux, gospider, httprobe\n"
                    "  [Web Scan] nikto, whatweb, wafw00f, wapiti, commix, xsser\n"
                    "  [Fuzzing] gobuster, feroxbuster, dirb, wfuzz\n"
                    "  [Network] masscan, netcat, tcpdump, tshark, arp-scan, hping3, traceroute\n"
                    "  [Brute Force] hydra, medusa, ncrack, cewl, crunch, hash-identifier\n"
                    "  [Cracking] john, hashcat\n"
                    "  [Exploit] metasploit (msfconsole), exploitdb (searchsploit)\n"
                    "  [SSL/TLS] sslscan, sslyze, testssl.sh\n"
                    "  [Proxy] mitmproxy\n"
                    "  [Reverse Eng] apktool, dex2jar, jadx, radare2, binwalk\n"
                    "  [Post-Exploit] socat, proxychains4, chisel, responder, impacket-scripts, evil-winrm, netexec, smbclient, smbmap\n"
                    "  [Go Tools] katana, gau, dalfox, waybackurls, qsreplace, unfurl, anew, gf, hakrawler, kxss, airixss, cariddi, gowitness, cf-check\n"
                    "  [Python] paramspider, uro, SecretFinder (/opt/SecretFinder), LinkFinder (/opt/LinkFinder)\n"
                    "  [Wordlists] SecLists (/usr/share/seclists/), Kali wordlists (/usr/share/wordlists/)\n"
                    "  [VPN] openvpn (NET_ADMIN capability)\n"
                    "The sandbox runs as user 'agentuser'. Some tools may require sudo."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to execute inside the Kali sandbox.",
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Maximum execution time in seconds (default 60, max 300).",
                        },
                    },
                    "required": ["command"],
                },
            },
        }
    )

    # Sub-agent spawning tool
    tools.append(
        {
            "type": "function",
            "function": {
                "name": "spawn_subagents",
                "description": (
                    "Spawn one or more AI sub-agents to execute tasks in parallel using different AI models. "
                    "Each sub-agent has FULL access to all tools (Kali sandbox, fetch, python_execute, nmap, recon tools, etc). "
                    "Use this to parallelize INDEPENDENT tasks like: scanning different ports, testing different vulnerability types, "
                    "running recon on different subdomains, or probing different attack vectors simultaneously. "
                    "Each sub-agent runs autonomously with its own AI model and returns findings/facts when done. "
                    "DO NOT use for sequential dependent tasks where step 2 needs step 1's output."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tasks": {
                            "type": "array",
                            "description": "List of independent tasks to assign to sub-agents",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "task": {
                                        "type": "string",
                                        "description": "Clear, specific task description for the sub-agent. Include the target, what to test, and expected outcomes.",
                                    },
                                    "model_hint": {
                                        "type": "string",
                                        "description": "Optional: preferred AI model name/provider hint (e.g. 'deepseek', 'qwen'). If empty, auto-assigned from pool.",
                                    },
                                },
                                "required": ["task"],
                            },
                        },
                    },
                    "required": ["tasks"],
                },
            },
        }
    )

    if mcp_manager:
        for schema in mcp_manager.get_tool_schemas():
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": schema.get("name", ""),
                        "description": schema.get("description", ""),
                        "parameters": schema.get(
                            "inputSchema", {"type": "object", "properties": {}}
                        ),
                    },
                }
            )

    return tools


async def execute_nmap(agent: Any, args: dict[str, Any]) -> str:
    target = args.get("target", "").strip()
    if not target:
        return "[!] nmap_scan need target parameter(Target IP or domain name)"

    host_violation = enforce_host_path_constraints(agent, host=target.lower(), target=target)
    if host_violation:
        return host_violation

    violation = enforce_port_constraints(agent, infer_ports_from_nmap_args(args), target=target)
    if violation:
        return violation

    try:
        ips = socket.getaddrinfo(target, None, socket.AF_INET)
        if ips:
            ip = ips[0][4][0]
            is_reserved, reason = is_reserved_ip(ip)
            if is_reserved:
                return (
                    f"[SKIP] Target {target} parse to retain/Intranet address ({reason}, IP: {ip})\n"
                    f"Skipped nmap scanning.Recommendationpass directly Web Fingerprint、Directory EnumerationCollect by other methodsInfo,"
                    f"Do notWasted on reserved addressesroundSecond-rate."
                )
    except Exception:
        pass

    scan_type = args.get("scan_type", "top_ports")
    custom_ports = args.get("ports", "")
    timing = int(args.get("timing", 4))

    nmap_cmd = shutil.which("nmap")
    if not nmap_cmd:
        try:
            result = subprocess.run(
                ["where.exe", "nmap"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                nmap_cmd = result.stdout.strip().split("\n")[0]
        except Exception:
            pass

    cmd_exe = nmap_cmd or "nmap"
    cmd = [cmd_exe, "-v" if scan_type == "full" else "-q", f"-T{max(0, min(5, timing))}"]
    if scan_type == "top_ports":
        cmd.extend(["--top-ports", "100", "-oX", "-"])
    elif scan_type == "syn":
        cmd.extend(["-sS", "-oX", "-"])
    elif scan_type == "tcp":
        cmd.extend(["-sT", "-oX", "-"])
    elif scan_type == "service":
        cmd.extend(["-sV", "-oX", "-"])
    elif scan_type == "os":
        cmd.extend(["-O", "-oX", "-"])
    elif scan_type == "vuln":
        cmd.extend(["--script", "vuln", "-oX", "-"])
    elif scan_type == "full":
        cmd.extend(["-sS", "-O", "-sV", "--script", "default,safe", "-oX", "-"])
    else:
        cmd.extend(["-sV", "-oX", "-"])

    if custom_ports:
        cmd.extend(["-p", custom_ports])
    cmd.append(target)

    # Fallback to executing inside the Kali Linux sandbox if local nmap is missing
    if not nmap_cmd:
        try:
            import shlex
            manager = _get_sandbox_manager()
            session = await manager.start_sandbox(_SANDBOX_SESSION_ID)
            if session.status == "running":
                cmd_str = " ".join(shlex.quote(arg) for arg in cmd)
                result_sandbox = await manager.execute_command(_SANDBOX_SESSION_ID, cmd_str, timeout=120)
                if result_sandbox is None:
                    return "[!] nmap scanning failed inside sandbox."
                if result_sandbox.exit_code != 0 and not result_sandbox.stdout:
                    return f"[!] nmap scanningFailed({result_sandbox.exit_code}): {result_sandbox.stderr[:500]}"
                return parse_nmap_xml(result_sandbox.stdout or result_sandbox.stderr, target)
        except Exception as e:
            return f"[!] nmap sandbox fallback failed: {e}"
        return "[!] nmap Not installedor not PATH Medium. pleaseConfirm nmap Installedand join the system PATH."

    try:
        kwargs: dict[str, Any] = {
            "capture_output": True,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
            "timeout": 120,
        }
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = startupinfo
        result = subprocess.run(cmd, **kwargs)
    except subprocess.TimeoutExpired:
        return "[!] nmap scanningTimeout(120seconds), please reduce the scan range or use a faster timing"
    except PermissionError:
        return "[!] nmap Execution denied (insufficient permissions).Windows Please be an administratorrunterminal."
    except Exception as e:
        return f"[!] nmap execution error: {e}"

    if result.returncode != 0 and not result.stdout:
        return f"[!] nmap scanningFailed({result.returncode}): {result.stderr[:500]}"
    return parse_nmap_xml(result.stdout or result.stderr, target)


def is_reserved_ip(ip: str) -> tuple[bool, str]:
    try:
        import ipaddress

        addr = ipaddress.ip_address(ip)
        for start, end, desc in RESERVED_IP_RANGES:
            if ipaddress.ip_address(start) <= addr <= ipaddress.ip_address(end):
                return True, desc
        return False, ""
    except Exception:
        return False, ""


def validate_scan_target(target: str) -> str:
    try:
        ips = socket.getaddrinfo(target, None, socket.AF_INET)
        if not ips:
            return ""
        ip = ips[0][4][0]
        is_reserved, reason = is_reserved_ip(ip)
        if is_reserved:
            return (
                f"\n\n⚠️ **Warning:Target {target} parse to retain/Intranet address ({reason})\n"
                f"   IP: {ip}\n"
                f"   Scan this address to getResultDoes not represent the security of the real systemStatus.\n"
                f"   nmap scanningResultMediumofPortInfopossible and realTargetNothing to do.**"
            )
    except Exception:
        pass
    return ""


def parse_nmap_xml(xml_output: str, target: str) -> str:
    if not xml_output or "<nmaprun" not in xml_output:
        lines = xml_output.strip().splitlines()[:80]
        return "nmap OriginalOutput:\n" + "\n".join(lines)

    try:
        root = ET.fromstring(xml_output)
    except ET.ParseError:
        lines = xml_output.strip().splitlines()[:80]
        return "nmap OriginalOutput:\n" + "\n".join(lines)

    lines = [f"nmap scanningResult — {target}", "=" * 60]
    for host in root.findall(".//host"):
        hostname = host.find(".//hostname[@type='user']")
        addrs = [a.get("addr", "") for a in host.findall("address")]
        status = host.find("status")
        status_val = status.get("state", "unknown") if status is not None else "unknown"
        host_ip = addrs[0] if addrs else target
        reserved, reason = is_reserved_ip(host_ip)
        if reserved:
            host_str = (
                f"\n[Host] {host_ip} ⚠️ **reserved address ({reason}), test networkResultdoes not represent realityTargetSafetyStatus**"
            )
        else:
            host_str = f"\n[Host] {host_ip}"
        if hostname is not None:
            host_str += f" ({hostname.get('name', '')})"
        host_str += f" — {status_val}"
        lines.append(host_str)

        for port in host.findall(".//port"):
            port_id = port.get("portid", "")
            proto = port.get("protocol", "tcp")
            port_state = port.find("state")
            svc = port.find("service")
            state_val = port_state.get("state", "unknown") if port_state is not None else "unknown"
            svc_name = svc.get("name", "") if svc is not None else ""
            svc_product = svc.get("product", "") if svc is not None else ""
            svc_version = svc.get("version", "") if svc is not None else ""
            lines.append(
                f"  {proto.upper():5} {port_id}/{'s' if svc is not None and svc.get('tunnel') == 'ssl' else ''} "
                f"{state_val:8}{svc_name:15}{(svc_product + ' ' + svc_version).rstrip()}"
            )
            for script in port.findall("script"):
                lines.append(f"    | {script.get('id', '')}: {script.get('output', '')[:120]}")

    runstats = root.find(".//runstats")
    if runstats is not None:
        finished = runstats.find("finished")
        if finished is not None:
            elapsed = finished.get("elapsed", "")
            summary = finished.get("summary", "")
            lines.append(f"\nCompletetime: {elapsed}s | {summary}")
    return "\n".join(lines) or f"nmap scanningComplete(noneOutput): {target}"


def _resolve_python_execute_mode(agent: Any) -> str:
    safety = getattr(agent.config, "safety", None)
    if safety is None:
        return "trusted-local"

    mode = str(getattr(safety, "python_execute_mode", "") or "").strip().lower()
    if not mode and getattr(safety, "python_execute_restricted", False):
        return "safe"
    if mode in {"safe", "lab", "trusted-local"}:
        return mode
    return "trusted-local"


def _validate_python_execute_mode(mode: str, code: str) -> str | None:
    patterns = SAFE_MODE_PATTERNS if mode == "safe" else LAB_MODE_PATTERNS if mode == "lab" else []
    for pattern in patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return pattern
    return None


def _write_python_audit(
    agent: Any,
    *,
    purpose: str,
    code: str,
    mode: str,
    outcome: str,
    blocked_reason: str = "",
) -> None:
    safety = getattr(agent.config, "safety", None)
    if safety is None or not getattr(safety, "python_execute_audit_enabled", True):
        return

    try:
        from datetime import datetime

        from bughunter.config.settings import PYTHON_EXECUTE_AUDIT_FILE, ensure_dirs

        ensure_dirs()
        record = {
            "timestamp": datetime.now().isoformat(),
            "target": getattr(getattr(agent, "session_state", None), "target", None),
            "mode": mode,
            "purpose": purpose,
            "outcome": outcome,
            "blocked_reason": blocked_reason,
            "code_preview": code[:300],
            "code_lines": code.count("\n") + 1,
        }
        with open(PYTHON_EXECUTE_AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        return


async def execute_python(agent: Any, args: dict[str, Any]) -> str:
    code = args.get("code", "")
    purpose = args.get("purpose", "")
    if not code.strip():
        return "[!] Code is empty; nothing executed"

    url_matches = re.findall(r"https?://([a-zA-Z0-9._:-]+)(/[^\s'\"`]*)?", code)
    for raw_host, path in url_matches:
        # Strip the port before the scope check so an in-scope target referenced
        # with a port (e.g. localhost:3000) is not falsely flagged out of scope.
        # The fetch tool already compares against urlparse().hostname (no port);
        # this keeps python_execute consistent with that behavior.
        host = raw_host.split(":", 1)[0].lower()
        host_violation = enforce_host_path_constraints(
            agent,
            host=host,
            path=(path or "").rstrip("/"),
            target=host,
        )
        if host_violation:
            return host_violation

    safety = getattr(agent.config, "safety", None)
    if safety is None or not safety.enable_python_execute:
        return (
            "[!] python_execute is disabled. Set safety.enable_python_execute = true to enable it"
        )

    mode = _resolve_python_execute_mode(agent)
    max_lines = getattr(safety, "python_execute_max_lines", 50)
    if code.count("\n") + 1 > max_lines:
        _write_python_audit(
            agent,
            purpose=purpose,
            code=code,
            mode=mode,
            outcome="blocked",
            blocked_reason="max_lines",
        )
        return f"[!] Code exceeds the max line limit ({max_lines})"

    show_warning = getattr(safety, "python_execute_show_warning", True)
    warning_prefix = ""
    if show_warning:
        warning_prefix = (
            f"[!] Security warning: python_execute runs local Python code in {mode} mode.\n"
            "Review the code carefully before execution.\n"
            "---\n"
        )

    recon_keywords = ["recon", "crawl", "spider", "scan", "enum", "probe"]
    timeout_seconds = 60 if any(kw in purpose.lower() for kw in recon_keywords) else 30

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, code):
            _write_python_audit(
                agent,
                purpose=purpose,
                code=code,
                mode=mode,
                outcome="blocked",
                blocked_reason=pattern,
            )
            return f"[!] Code contains a blocked operation pattern: {pattern}"

    blocked_pattern = _validate_python_execute_mode(mode, code)
    if blocked_pattern:
        _write_python_audit(
            agent,
            purpose=purpose,
            code=code,
            mode=mode,
            outcome="blocked",
            blocked_reason=blocked_pattern,
        )
        if mode == "safe":
            return f"[!] safe mode blocked operation: {blocked_pattern}"
        return f"[!] lab mode blocked operation: {blocked_pattern}"

    max_output_chars = getattr(safety, "python_execute_max_output_chars", 8000)
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            preamble = (
                "import sys, json, re, os, base64, hashlib, itertools, collections, datetime, struct, binascii, textwrap\n"
                "try:\n    import requests\nexcept ImportError:\n    pass\n"
                "try:\n    from bs4 import BeautifulSoup\nexcept ImportError:\n    pass\n"
                "try:\n    from Crypto.Cipher import AES\nexcept ImportError:\n    pass\n\n"
            )
            f.write(preamble)
            f.write(code)
            tmp_path = f.name

        base_env = {"PYTHONIOENCODING": "utf-8"}
        env = {**os.environ, **base_env} if mode == "trusted-local" else base_env

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                cwd=tempfile.gettempdir(),
                env=env,
            ),
        )

        try:
            os.unlink(tmp_path)
        except OSError:
            pass

        output_parts: list[str] = []
        if result.stdout:
            output_parts.append(result.stdout)
        if result.stderr:
            stderr_lines = [
                line
                for line in result.stderr.splitlines()
                if "ImportError" not in line and "No module named" not in line
            ]
            if stderr_lines:
                output_parts.append("[stderr]\n" + "\n".join(stderr_lines))

        if not output_parts:
            _write_python_audit(agent, purpose=purpose, code=code, mode=mode, outcome="success")
            return f"{warning_prefix}[+] Python executed successfully with no output"

        output = "\n".join(output_parts)
        for sig in ["[DONE]", "[COMPLETE]"]:
            output = output.replace(sig, f"[BLOCKED_{sig[1:-1]}]")
        if len(output) > max_output_chars:
            clip = max_output_chars // 2
            output = output[:clip] + "\n...[truncated]...\n" + output[-clip:]
        _write_python_audit(agent, purpose=purpose, code=code, mode=mode, outcome="success")
        return f"{warning_prefix}[+] Python execution result ({mode}):\n{output}"
    except subprocess.TimeoutExpired:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        agent.runtime.python_timeout_rounds += 1
        _write_python_audit(agent, purpose=purpose, code=code, mode=mode, outcome="timeout")
        return f"[!] Python execution timed out after {timeout_seconds} seconds"
    except Exception as e:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        _write_python_audit(
            agent, purpose=purpose, code=code, mode=mode, outcome="error", blocked_reason=str(e)
        )
        return f"[!] Python execution error: {e}"


def _sync_cookies_to_shared_jar(
    agent: Any, cookies: list[tuple[str, str, str, str]]
) -> None:
    """Copy session cookies into the agent's shared _fetch_cookies jar.

    This allows the ``fetch`` tool (which uses ``_fetch_cookies``) to
    immediately use the authenticated session obtained by
    ``brute_force_login`` without requiring a separate re-login.
    """
    if not agent or not cookies:
        return
    mcp = getattr(agent, "mcp_manager", None)
    if not mcp:
        return
    try:
        import httpx

        jar = getattr(mcp, "_fetch_cookies", None)
        if jar is None:
            jar = httpx.Cookies()
            mcp._fetch_cookies = jar
        for name, value, domain, path in cookies:
            if name and value:
                jar.set(name, value, domain=domain or "", path=path or "/")
    except Exception:
        pass


async def execute_brute_force(agent: Any, args: dict[str, Any]) -> str:
    """Execute a login brute-force with automatic CSRF/session management.

    Handles the full flow in one call:
    GET login page → extract CSRF + session → POST passwords → detect result
    """
    import asyncio
    import re
    import time

    url = str(args.get("url", "") or "").strip()
    password_field = str(args.get("password_field", "") or "").strip()
    csrf_field = str(args.get("csrf_field", "") or "").strip()
    username_field = str(args.get("username_field", "") or "").strip()
    username = str(args.get("username", "") or "").strip()
    passwords = args.get("passwords", [])
    success_keyword = str(args.get("success_keyword", "") or "").strip()
    failure_keyword = str(args.get("failure_keyword", "") or "").strip()
    submit_action = str(args.get("submit_action", "") or "").strip()
    extra_data = args.get("extra_data", {}) or {}
    submit_url = submit_action or url

    if not url or not password_field or not passwords:
        return "[!] Missing required parameter: url, password_field, passwords"

    if not isinstance(passwords, list) or not passwords:
        return "[!] passwords MustIs a non-empty list"

    passwords = passwords[:20]
    total = len(passwords)

    try:
        import httpx
    except ImportError:
        return "[!] httpx Not installed, unable to perform blasting"

    def extract_csrf(html: str, field_name: str) -> str | None:
        """Extract CSRF token from HTML input field."""
        if not field_name:
            return None
        pattern = re.compile(
            rf'name=["\']{re.escape(field_name)}["\'][^>]*value=["\']([^"\']+)',
            re.IGNORECASE,
        )
        m = pattern.search(html)
        if m:
            return m.group(1)
        # Try alternative: value before name
        pattern2 = re.compile(
            rf'value=["\']([^"\']+)[^>]*name=["\']{re.escape(field_name)}',
            re.IGNORECASE,
        )
        m = pattern2.search(html)
        return m.group(1) if m else None

    results: list[str] = []
    start_time = time.time()
    attempts = 0
    found_password: str | None = None

    # Collect cookies from the internal client so we can sync them
    # back to the shared _fetch_cookies jar after a successful login.
    session_cookies: list[tuple[str, str, str, str]] = []  # name, value, domain, path

    async with httpx.AsyncClient(
        verify=False,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        # Step 1: Get login page for initial CSRF and session
        try:
            resp = await asyncio.wait_for(
                client.get(url),
                timeout=30.0,
            )
            html = resp.text
        except Exception as e:
            return f"[!] Get login pageFailed: {e}"

        csrf_token = extract_csrf(html, csrf_field)
        if csrf_token is None and csrf_field:
            results.append(f"[!] Warning: Not found on login page CSRF Field '{csrf_field}'")

        # Auto-detect submit button values from login page HTML.
        # Many forms (DVWA, etc.) check isset($_POST['SubmitButtonName'])
        # before processing authentication. Without the button's name=value,
        # the server skips auth and just re-renders the page.
        auto_fields: dict[str, str] = {}
        for input_match in re.finditer(
            r'<(?:input|button)\s[^>]*type=["\']submit["\'][^>]*>',
            html,
            re.IGNORECASE,
        ):
            tag = input_match.group()
            name_m = re.search(r'name\s*=\s*["\']([^"\']+)["\']', tag, re.IGNORECASE)
            val_m = re.search(r'value\s*=\s*["\']([^"\']*)["\']', tag, re.IGNORECASE)
            if name_m:
                auto_fields[name_m.group(1)] = val_m.group(1) if val_m else name_m.group(1)

        # Step 2: Try each password
        for i, password in enumerate(passwords, 1):
            form_data: dict[str, str] = {}
            if username_field and username:
                form_data[username_field] = username
            form_data[password_field] = password
            if csrf_token and csrf_field:
                form_data[csrf_field] = csrf_token
            # Auto-detected submit buttons come first so they can be
            # overridden by explicit extra_data if needed.
            form_data.update(auto_fields)
            form_data.update({k: str(v) for k, v in extra_data.items()})

            try:
                resp = await asyncio.wait_for(
                    client.post(submit_url, data=form_data),
                    timeout=30.0,
                )
                attempts += 1
                response_html = resp.text
                status = resp.status_code

                # Determine success or failure
                is_success = False
                reason = ""
                csrf_markers = ["csrf token is incorrect", "csrf token mismatch",
                                "token mismatch", "invalid token"]

                if success_keyword and success_keyword.lower() in response_html.lower():
                    is_success = True
                    reason = f"'{success_keyword}'"
                elif failure_keyword and failure_keyword.lower() in response_html.lower():
                    is_success = False
                    reason = f"'{failure_keyword}'"
                elif any(m in response_html.lower() for m in csrf_markers):
                    is_success = False
                    reason = "CSRF token Error(new ones automatically synced token)"
                elif status == 302:
                    is_success = True
                    reason = "Status 302 (redirect)"
                elif "logout" in response_html.lower() or "welcome" in response_html.lower():
                    is_success = True
                    reason = "DetectedLogged inStatus"
                else:
                    # Include a short snippet from the response so the model
                    # can diagnose what the server actually returned.
                    snippet = response_html.strip()[:200].replace("\n", " ")
                    is_success = False
                    reason = snippet

                prefix = "[✓]" if is_success else "[✗]"
                pw_preview = password[:40].replace("\n", "\\n")
                results.append(f"{prefix} {pw_preview} → {'Success' if is_success else 'Failed'} ({reason})")

                # Extract new CSRF from response for next attempt
                new_token = extract_csrf(response_html, csrf_field)
                if new_token:
                    csrf_token = new_token

                # Stop early on success if keyword matched
                if is_success and success_keyword:
                    found_password = password
                    break

            except Exception as e:
                pw_preview = password[:30].replace("\n", "\\n")
                results.append(f"[!] {pw_preview} → askFailed: {e}")
                continue

        # Save cookies from the internal client for potential sharing with
        # the fetch tool's cookie jar.
        try:
            for cookie in client.cookies.jar:
                session_cookies.append(
                    (cookie.name, cookie.value, cookie.domain, cookie.path)
                )
        except Exception:
            pass

    elapsed = time.time() - start_time

    # Sync session cookies to the shared _fetch_cookies jar so that
    # subsequent `fetch` calls from the agent are already authenticated.
    if found_password and session_cookies:
        _sync_cookies_to_shared_jar(agent, session_cookies)

    summary = [
        f"[+] blastingComplete — {url}",
        f"    user: {username or '(not specified)'}",
        "",
        "    Result:",
    ]
    for r in results:
        summary.append(f"    {r}")
    summary.append("")
    summary.append(f"    time consuming: {elapsed:.1f}s")
    summary.append(f"    try: {attempts}/{total}")

    return "\n".join(summary)


# ── Kali Sandbox Execution ─────────────────────────────────────────

# Module-level singleton so the sandbox container is reused across calls.
# ── Wordlist path resolution for ffuf ───────────────────────────────────────
_FFUF_WORDLISTS: dict[str, str] = {
    "common": "/usr/share/seclists/Discovery/Web-Content/common.txt",
    "big": "/usr/share/seclists/Discovery/Web-Content/big.txt",
    "raft-large": "/usr/share/seclists/Discovery/Web-Content/raft-large-words.txt",
    "api-endpoints": "/usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt",
    "subdomains": "/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt",
}


async def _run_sandbox_tool(agent: Any, command: str, timeout: int = 180) -> str:
    """Shared helper: run a command in the Kali sandbox and return formatted output."""
    return await execute_kali_sandbox(agent, {"command": command, "timeout": timeout})


async def execute_nuclei(agent: Any, args: dict[str, Any]) -> str:
    """Execute Nuclei vulnerability scanner in sandbox."""
    target = str(args.get("target", "")).strip()
    if not target:
        return "[!] nuclei_scan requires a 'target' parameter"

    cmd_parts = ["nuclei", "-u", target, "-silent", "-nc"]

    templates = args.get("templates", "")
    if templates:
        # Check if it's a category or specific template path
        if "/" in templates:
            cmd_parts.extend(["-t", templates])
        else:
            cmd_parts.extend(["-t", templates])

    severity = args.get("severity", "")
    if severity:
        cmd_parts.extend(["-severity", severity])

    rate_limit = args.get("rate_limit")
    if rate_limit:
        cmd_parts.extend(["-rl", str(int(rate_limit))])

    tags = args.get("tags", "")
    if tags:
        cmd_parts.extend(["-tags", tags])

    cmd = " ".join(cmd_parts)
    return await _run_sandbox_tool(agent, cmd, timeout=180)


async def execute_sqlmap(agent: Any, args: dict[str, Any]) -> str:
    """Execute SQLMap SQL injection scanner in sandbox."""
    url = str(args.get("url", "")).strip()
    if not url:
        return "[!] sqlmap_scan requires a 'url' parameter"

    cmd_parts = ["sqlmap", "-u", f'"{url}"', "--batch", "--smart", "--random-agent"]

    data = args.get("data", "")
    if data:
        cmd_parts.extend(["--data", f'"{data}"'])

    param = args.get("param", "")
    if param:
        cmd_parts.extend(["-p", param])

    cookie = args.get("cookie", "")
    if cookie:
        cmd_parts.extend(["--cookie", f'"{cookie}"'])

    level = args.get("level")
    if level:
        cmd_parts.extend(["--level", str(int(level))])

    risk = args.get("risk")
    if risk:
        cmd_parts.extend(["--risk", str(int(risk))])

    technique = args.get("technique", "")
    if technique:
        cmd_parts.extend(["--technique", technique])

    tamper = args.get("tamper", "")
    if tamper:
        cmd_parts.extend(["--tamper", f'"{tamper}"'])

    dbms = args.get("dbms", "")
    if dbms:
        cmd_parts.extend(["--dbms", dbms])

    cmd = " ".join(cmd_parts)
    return await _run_sandbox_tool(agent, cmd, timeout=180)


async def execute_ffuf(agent: Any, args: dict[str, Any]) -> str:
    """Execute ffuf web fuzzer in sandbox."""
    url = str(args.get("url", "")).strip()
    if not url:
        return "[!] ffuf_fuzz requires a 'url' parameter"

    # Resolve wordlist name to path
    wordlist = args.get("wordlist", "common")
    wordlist_path = _FFUF_WORDLISTS.get(wordlist, wordlist)
    if not wordlist_path.startswith("/"):
        wordlist_path = _FFUF_WORDLISTS.get("common", "/usr/share/seclists/Discovery/Web-Content/common.txt")

    cmd_parts = ["ffuf", "-u", f'"{url}"', "-w", wordlist_path, "-mc", "all", "-ac"]

    method = args.get("method", "")
    if method:
        cmd_parts.extend(["-X", method.upper()])

    headers = args.get("headers", "")
    if headers:
        for h in headers.split(";"):
            h = h.strip()
            if h:
                cmd_parts.extend(["-H", f'"{h}"'])

    data = args.get("data", "")
    if data:
        cmd_parts.extend(["-d", f'"{data}"'])

    filter_code = args.get("filter_code", "")
    if filter_code:
        cmd_parts.extend(["-fc", filter_code])

    filter_size = args.get("filter_size", "")
    if filter_size:
        cmd_parts.extend(["-fs", filter_size])

    match_code = args.get("match_code", "")
    if match_code:
        cmd_parts.extend(["-mc", match_code])

    rate = args.get("rate")
    if rate:
        cmd_parts.extend(["-rate", str(int(rate))])

    cmd = " ".join(cmd_parts)
    return await _run_sandbox_tool(agent, cmd, timeout=180)


async def execute_xss_scan(agent: Any, args: dict[str, Any]) -> str:
    """Execute Dalfox XSS scanner in sandbox."""
    url = str(args.get("url", "")).strip()
    if not url:
        return "[!] xss_scan requires a 'url' parameter"

    cmd_parts = ["dalfox", "url", f'"{url}"']

    param = args.get("param", "")
    if param:
        cmd_parts.extend(["-p", param])

    cookie = args.get("cookie", "")
    if cookie:
        cmd_parts.extend(["-C", f'"{cookie}"'])

    header = args.get("header", "")
    if header:
        cmd_parts.extend(["-H", f'"{header}"'])

    blind_url = args.get("blind_url", "")
    if blind_url:
        cmd_parts.extend(["--blind", blind_url])

    custom_payload = args.get("custom_payload", "")
    if custom_payload:
        cmd_parts.extend(["--custom-payload", f'"{custom_payload}"'])

    cmd = " ".join(cmd_parts)
    return await _run_sandbox_tool(agent, cmd, timeout=180)


async def execute_crawl_urls(agent: Any, args: dict[str, Any]) -> str:
    """Execute URL crawling via Katana (active) and optionally Gau (passive)."""
    target = str(args.get("target", "")).strip()
    if not target:
        return "[!] crawl_urls requires a 'target' parameter"

    results: list[str] = []

    # Active crawl with Katana
    katana_parts = ["katana", "-u", f'"{target}"', "-silent", "-nc"]
    depth = args.get("depth", 3)
    katana_parts.extend(["-d", str(int(depth))])

    scope = args.get("scope", "strict")
    if scope == "strict":
        katana_parts.append("-fs=sdn")

    js_crawl = args.get("js_crawl", False)
    if js_crawl:
        katana_parts.append("-jc")

    katana_cmd = " ".join(katana_parts)
    katana_result = await _run_sandbox_tool(agent, katana_cmd, timeout=120)
    results.append("[katana active crawl]\n" + katana_result)

    # Passive URL fetch with Gau if requested
    include_wayback = args.get("include_wayback", False)
    if include_wayback:
        # Extract domain for gau
        domain = target.replace("https://", "").replace("http://", "").split("/")[0]
        gau_cmd = f'echo "{domain}" | gau --subs --o /dev/stdout 2>/dev/null | head -500'
        gau_result = await _run_sandbox_tool(agent, gau_cmd, timeout=60)
        results.append("\n[gau passive URLs]\n" + gau_result)

    return "\n".join(results)


async def execute_param_discover(agent: Any, args: dict[str, Any]) -> str:
    """Execute Arjun hidden parameter discovery in sandbox."""
    url = str(args.get("url", "")).strip()
    if not url:
        return "[!] param_discover requires a 'url' parameter"

    cmd_parts = ["arjun", "-u", f'"{url}"']

    method = args.get("method", "GET")
    cmd_parts.extend(["-m", method.upper()])

    wordlist = args.get("wordlist", "")
    if wordlist:
        cmd_parts.extend(["-w", wordlist])

    headers = args.get("headers", "")
    if headers:
        cmd_parts.extend(["--headers", f"'{headers}'"])

    rate = args.get("rate")
    if rate:
        cmd_parts.extend(["--rate", str(int(rate))])

    cmd = " ".join(cmd_parts)
    return await _run_sandbox_tool(agent, cmd, timeout=120)


async def execute_httpx_probe(agent: Any, args: dict[str, Any]) -> str:
    """Execute httpx HTTP probing in sandbox."""
    targets = args.get("targets", [])
    if not targets:
        return "[!] httpx_probe requires a 'targets' parameter (list of hosts)"

    if isinstance(targets, str):
        targets = [targets]

    # Write targets to a temp file for httpx stdin
    target_list = "\\n".join(targets)
    cmd_parts = [f'echo -e "{target_list}"', "|", "httpx-toolkit", "-silent"]

    ports = args.get("ports", "")
    if ports:
        cmd_parts.extend(["-p", ports])

    title = args.get("title", True)
    if title:
        cmd_parts.append("-title")

    status_code = args.get("status_code", True)
    if status_code:
        cmd_parts.append("-sc")

    tech_detect = args.get("tech_detect", False)
    if tech_detect:
        cmd_parts.append("-td")

    content_length = args.get("content_length", False)
    if content_length:
        cmd_parts.append("-cl")

    follow_redirects = args.get("follow_redirects", True)
    if follow_redirects:
        cmd_parts.append("-fr")

    cmd = " ".join(cmd_parts)
    return await _run_sandbox_tool(agent, cmd, timeout=120)


async def execute_wpscan(agent: Any, args: dict[str, Any]) -> str:
    """Execute WPScan WordPress scanner in sandbox."""
    url = str(args.get("url", "")).strip()
    if not url:
        return "[!] wpscan_scan requires a 'url' parameter"

    cmd_parts = ["wpscan", "--url", f'"{url}"', "--no-banner", "--random-user-agent"]

    enumerate = args.get("enumerate", "")
    if enumerate:
        cmd_parts.extend(["-e", enumerate])

    api_token = args.get("api_token", "")
    if api_token:
        cmd_parts.extend(["--api-token", api_token])

    cmd = " ".join(cmd_parts)
    return await _run_sandbox_tool(agent, cmd, timeout=180)


_sandbox_manager: Any = None
_SANDBOX_SESSION_ID = "agent_shared_sandbox"


def _get_sandbox_manager() -> Any:
    """Lazily initialize and return the SandboxManager singleton."""
    global _sandbox_manager
    if _sandbox_manager is None:
        from bughunter.web.services.sandbox_service import SandboxManager

        _sandbox_manager = SandboxManager()
    return _sandbox_manager


async def execute_kali_sandbox(agent: Any, args: dict[str, Any]) -> str:
    """Execute a command inside the Kali Linux sandbox container."""
    command = str(args.get("command", "") or "").strip()
    if not command:
        return "[!] kali_sandbox_execute requires a 'command' parameter"

    timeout = int(args.get("timeout", 60) or 60)
    timeout = max(5, min(timeout, 300))  # clamp to 5-300s

    # Enforce scan budget phase timeout if active
    scan_budget = getattr(getattr(agent, "runtime", None), "scan_budget", None)
    if scan_budget is not None and not scan_budget.is_unlimited:
        budget_timeout = scan_budget.get_tool_timeout(timeout)
        if budget_timeout < timeout:
            timeout = budget_timeout

    try:
        manager = _get_sandbox_manager()

        # Ensure the sandbox container is running
        session = await manager.start_sandbox(_SANDBOX_SESSION_ID)
        if session.status != "running":
            return (
                f"[!] Kali sandbox failed to start (status: {session.status}). "
                "Ensure Docker is running and the bughunter-kali-sandbox image is built."
            )

        # Execute the command
        result = await manager.execute_command(_SANDBOX_SESSION_ID, command, timeout)
        if result is None:
            return "[!] Kali sandbox command execution failed — session not found or not running."

        # Format output for the LLM
        parts: list[str] = []
        parts.append(f"[sandbox] $ {command}")
        parts.append(f"[exit_code: {result.exit_code}] [duration: {result.duration_ms}ms]")

        if result.stdout:
            stdout = result.stdout
            if result.truncated:
                stdout += "\n... (output truncated)"
            parts.append(stdout)

        if result.stderr:
            parts.append(f"[stderr]\n{result.stderr}")

        if not result.stdout and not result.stderr:
            parts.append("(no output)")

        return "\n".join(parts)

    except Exception as e:
        return f"[!] Kali sandbox execution error: {e}"


async def _execute_spawn_subagents(agent: Any, args: dict[str, Any]) -> str:
    """Execute the spawn_subagents tool: dispatch tasks to sub-agents and return results."""
    tasks = args.get("tasks", [])
    if not tasks:
        return "[!] spawn_subagents requires at least one task in the 'tasks' array."

    if not isinstance(tasks, list):
        return "[!] 'tasks' must be an array of task objects."

    # Validate tasks
    valid_tasks = []
    for t in tasks:
        if isinstance(t, dict) and t.get("task"):
            valid_tasks.append(t)
        elif isinstance(t, str):
            valid_tasks.append({"task": t})
    if not valid_tasks:
        return "[!] No valid tasks found. Each task must have a 'task' field with a description."

    # Get the SubAgentManager from the agent
    sub_manager = getattr(agent, "sub_agent_manager", None)
    if sub_manager is None:
        return (
            "[!] Sub-agent manager not initialized. "
            "Ensure model_pool is configured in config.yaml with enabled models."
        )

    # Update target
    target = getattr(getattr(agent, "context", None), "state", None)
    if target is not None:
        sub_manager.set_target(getattr(target, "target", ""))

    # Spawn sub-agents
    try:
        results = await sub_manager.spawn(valid_tasks)
    except Exception as e:
        return f"[!] Sub-agent spawn error: {e}"

    # Merge findings back into main agent's session
    session = getattr(agent, "session_state", None)
    if session is not None and hasattr(session, "findings"):
        for r in results:
            for finding in r.findings:
                # Avoid duplicates by checking finding_id
                existing_ids = {
                    getattr(f, "finding_id", "") for f in session.findings
                }
                fid = getattr(finding, "finding_id", "")
                if fid and fid not in existing_ids:
                    session.findings.append(finding)

    # Merge facts into main blackboard
    board = getattr(getattr(agent, "context", None), "state", None)
    if board is not None:
        main_board = getattr(board, "board", None)
        if main_board is not None and hasattr(main_board, "add_fact"):
            for r in results:
                if r.facts:
                    # Add a summary fact for each sub-agent's work
                    summary_facts = r.facts[-5:]  # Last 5 most relevant facts
                    for fact in summary_facts:
                        if fact and len(fact) > 10:
                            main_board.add_fact(
                                f"[{r.agent_id} {r.model_name}] {fact[:300]}",
                                source=f"subagent:{r.agent_id}",
                            )

    # Format results for the main agent
    return sub_manager.format_results_for_agent(results)

