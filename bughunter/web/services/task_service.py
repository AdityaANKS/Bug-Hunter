"""Task orchestration service for the Web UI backend."""

from __future__ import annotations

import asyncio

from bughunter.agent.constraint_policy import validate_action_constraints
from bughunter.agent.context import TaskConstraints
from bughunter.agent.core import AgentCore
from bughunter.agent.input_analysis import extract_task_constraints
from bughunter.config.settings import load_config
from bughunter.mcp.lifecycle import MCPLifecycleManager
from bughunter.orchestrator import run_agent_task
from bughunter.web.schemas import TaskCreateRequest
from bughunter.web.task_manager import WebTaskManager


def start_task(manager: WebTaskManager, request: TaskCreateRequest) -> str:
    """Create and schedule a new task."""
    record = manager.create_task(request)
    task = asyncio.create_task(_run_task(manager, record.task_id, request))
    manager.bind_runtime_task(record.task_id, task)
    return record.task_id


async def _run_task(manager: WebTaskManager, task_id: str, request: TaskCreateRequest) -> None:
    config = load_config()
    task_constraints = _build_task_constraints(request)
    violation = validate_action_constraints(request.command, task_constraints)
    if violation is not None:
        manager.set_failed(task_id, violation)
        return
    if request.options.only_path and request.command == "persistent":
        manager.set_failed(
            task_id,
            "constraint_violation: persistent tasks are not allowed with only_path scope yet",
        )
        return

    mcp_manager = MCPLifecycleManager(config)
    mcp_manager.start_enabled_servers()
    agent = AgentCore(config, mcp_manager)

    try:

        def before_restore(_restore_result) -> None:
            if request.resume:
                manager.set_restoring(task_id, snapshot_id=request.snapshot_id)

        def on_restored(restore_result) -> None:
            manager.publish(
                task_id,
                "task_state_changed",
                {
                    "resume": True,
                    "snapshot_id": restore_result.snapshot_id,
                    "phase": restore_result.phase,
                    "resume_strategy": restore_result.resume_strategy,
                    "resume_reason": restore_result.resume_reason,
                },
            )

        async def runner_fn(shared_agent: AgentCore) -> None:
            manager.set_running(task_id)
            if request.command == "persistent":
                await _run_persistent_task(manager, task_id, shared_agent, request)
            else:
                await _run_single_task(manager, task_id, shared_agent, request)

        run_result = await run_agent_task(
            agent=agent,
            command=request.command,
            target=request.target,
            resume=request.resume,
            snapshot_id=request.snapshot_id,
            before_restore=before_restore,
            on_restored=on_restored,
            runner=runner_fn,
        )
        manager.set_completed(task_id, latest_message="Task finished", summary=run_result.summary)
    except asyncio.CancelledError:
        manager.set_stopped(task_id)
        raise
    except Exception as exc:
        manager.set_failed(task_id, str(exc))
    finally:
        mcp_manager.stop_all()


async def _run_single_task(
    manager: WebTaskManager, task_id: str, agent: AgentCore, request: TaskCreateRequest
) -> None:
    prompt = _build_prompt_v2(request)

    if request.command == "run":
        max_rounds = request.options.max_rounds or agent.config.session.max_rounds
        results = await agent.auto_pentest(
            prompt,
            target=request.target,
            max_rounds=max_rounds,
            on_step=_build_step_callback(manager, task_id),
        )
        if results:
            last = results[-1]
            manager.update_progress(
                task_id, phase=last.phase, message=last.output[:200] if last.output else None
            )
        return

    result = await agent.chat(prompt, target=request.target)
    if result.output:
        manager.publish(
            task_id,
            "round_output",
            {
                "phase": result.phase or agent.session_state.phase.value,
                "text": result.output,
            },
        )
        manager.update_progress(task_id, phase=result.phase, message=result.output[:200])


async def _run_persistent_task(
    manager: WebTaskManager, task_id: str, agent: AgentCore, request: TaskCreateRequest
) -> None:
    rounds_per_cycle = (
        request.options.rounds_per_cycle or agent.config.session.persistent_rounds_per_cycle
    )
    max_cycles = request.options.max_cycles or agent.config.session.persistent_max_cycles
    prompt = _build_prompt_v2(request)

    def on_cycle_step(round_num: int, cycle_num: int, result) -> None:
        manager.publish(
            task_id,
            "round_output",
            {
                "cycle": cycle_num,
                "round": round_num,
                "phase": result.phase,
                "text": result.output,
            },
        )
        manager.update_progress(task_id, phase=result.phase, message=(result.output or "")[:200])

    def on_cycle_complete(cycle_num: int, cycle_result) -> None:
        manager.publish(
            task_id,
            "cycle_completed",
            {
                "cycle": cycle_num,
                "new_findings": cycle_result.new_findings,
                "report_path": cycle_result.report_path,
            },
        )

    await agent.persistent_pentest(
        user_input=prompt,
        target=request.target,
        rounds_per_cycle=rounds_per_cycle,
        max_cycles=max_cycles,
        auto_report=True,
        on_cycle_step=on_cycle_step,
        on_cycle_complete=on_cycle_complete,
    )


def _build_step_callback(manager: WebTaskManager, task_id: str):
    def _callback(round_num: int, result) -> None:
        manager.publish(
            task_id,
            "round_output",
            {
                "round": round_num,
                "phase": result.phase,
                "text": result.output,
            },
        )
        manager.update_progress(task_id, phase=result.phase, message=(result.output or "")[:200])

    return _callback


def _build_task_constraints(request: TaskCreateRequest) -> TaskConstraints:
    """Build hard constraints from structured Web task options and prompt text."""
    constraints = extract_task_constraints(_build_prompt_v2(request))
    options = request.options

    if options.only_port is not None and options.only_port not in constraints.allowed_ports:
        constraints.allowed_ports.append(options.only_port)
    if options.only_host and options.only_host not in constraints.allowed_hosts:
        constraints.allowed_hosts.append(options.only_host)
    if options.only_path and options.only_path not in constraints.allowed_paths:
        constraints.allowed_paths.append(options.only_path)
    if options.blocked_host and options.blocked_host not in constraints.blocked_hosts:
        constraints.blocked_hosts.append(options.blocked_host)
    if options.blocked_path and options.blocked_path not in constraints.blocked_paths:
        constraints.blocked_paths.append(options.blocked_path)
    if options.allow_actions:
        constraints.allowed_actions = list(
            dict.fromkeys([*constraints.allowed_actions, *options.allow_actions])
        )
    if options.block_actions:
        constraints.blocked_actions = list(
            dict.fromkeys([*constraints.blocked_actions, *options.block_actions])
        )

    if options.only_port is not None and request.command == "exploit" and not options.allow_actions:
        constraints.blocked_actions = list(dict.fromkeys([*constraints.blocked_actions, "exploit"]))

    if not constraints.is_empty():
        constraints.strict_mode = True
    return constraints


def _build_prompt_v2(request: TaskCreateRequest) -> str:
    """Build a clean prompt string for Web-triggered tasks."""
    constraints = []
    if request.options.only_port is not None:
        constraints.append(f"Only test port {request.options.only_port}")
    if request.options.only_host:
        constraints.append(f"Only test host {request.options.only_host}")
    if request.options.only_path:
        constraints.append(f"Only test path {request.options.only_path}")
    if request.options.blocked_host:
        constraints.append(f"Blocked host {request.options.blocked_host}")
    if request.options.blocked_path:
        constraints.append(f"Blocked path {request.options.blocked_path}")
    if request.options.allow_actions:
        constraints.append(f"Only allowed actions: {', '.join(request.options.allow_actions)}")
    if request.options.block_actions:
        constraints.append(f"Blocked actions: {', '.join(request.options.block_actions)}")
    constraint_suffix = f" {' '.join(constraints)}." if constraints else ""

    # If user provided a custom prompt, use it as the primary instruction
    if request.options.prompt and request.options.prompt.strip():
        base = (
            f"Target: {request.target}\n\n"
            f"User Instructions:\n{request.options.prompt.strip()}"
        )
    else:
        base = _auto_prompt(request)

    tool_guidance = _build_tool_guidance(request.command)
    return f"{base}{constraint_suffix}\n\n{tool_guidance}"


def _auto_prompt(request: TaskCreateRequest) -> str:
    """Generate an auto prompt when the user didn't provide custom instructions."""
    if request.command == "recon":
        return f"Perform authorized reconnaissance and information gathering against {request.target}."
    if request.command == "scan":
        return f"Perform authorized vulnerability scanning and verification against {request.target}."
    if request.command == "exploit":
        cve_hint = f" using {request.options.cve}" if request.options.cve else ""
        cmd_hint = f", verifying with command {request.options.cmd}" if request.options.cmd else ""
        return f"Attempt authorized exploitation against {request.target}{cve_hint}{cmd_hint}."
    if request.command == "persistent":
        return f"Perform an authorized persistent penetration test against {request.target}."
    return f"Perform a full authorized penetration test against {request.target}."


def _build_tool_guidance(command: str) -> str:
    """Return comprehensive tool guidance so the AI knows what's available."""
    return """\
## Available Tools & Usage Guide

### Built-in Agent Tools (use directly by name)
| Tool | Purpose | When to Use |
|------|---------|------------|
| `nmap_scan` | Port scanning & service detection | First step recon — discover open ports & services |
| `python_execute` | Run Python code snippets | Custom HTTP requests, data processing, encoding |
| `crypto_decode` | Encoding/decoding/hashing | Base64, hex, URL, AES, JWT, MD5, auto-decode |
| `brute_force_login` | Login form brute-force | Test weak credentials with CSRF/session management |
| `space_search` | Asset search (FOFA/Shodan/etc.) | Passive recon — find IPs, subdomains, tech stack |
| `subdomain_enum` | Subdomain enumeration | Find subdomains via passive + DNS brute-force |
| `js_recon` | JS file analysis | Extract API endpoints, keys, tokens from JS files |
| `dir_enum` | Directory/file enumeration | Discover hidden paths, admin panels, backup files |
| `unauth_test` | Unauthorized access detection | Test endpoints for missing authentication |
| `kali_sandbox_execute` | Run any command in Kali Linux | Use 80+ native security tools in isolated sandbox |

### Kali Sandbox Tools (via `kali_sandbox_execute`)

**Reconnaissance:**
- `whois <target>` — Domain registration info
- `dig <target> ANY` / `dnsrecon -d <target>` — DNS enumeration
- `theHarvester -d <target> -b all` — Email/subdomain harvesting
- `amass enum -passive -d <target>` — Passive subdomain enumeration
- `subfinder -d <target>` — Fast subdomain discovery
- `whatweb <url>` — Web technology fingerprinting
- `wafw00f <url>` — WAF detection

**Web Vulnerability Scanning:**
- `nikto -h <url>` — Web server scanner (misconfigs, outdated software)
- `nuclei -u <url> -t cves/` — Template-based vulnerability scanner
- `wpscan --url <url>` — WordPress security scanner
- `sqlmap -u "<url>?id=1" --batch` — SQL injection detection & exploitation
- `commix --url="<url>?cmd=test"` — Command injection testing

**Directory & Fuzzing:**
- `ffuf -u <url>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt` — Fast web fuzzer
- `gobuster dir -u <url> -w /usr/share/wordlists/dirb/common.txt` — Directory brute-force
- `dirb <url>` — Classic directory scanner

**Exploitation:**
- `msfconsole -q -x "use exploit/...; set RHOSTS <target>; run"` — Metasploit Framework
- `msfvenom -p <payload> LHOST=<ip> LPORT=<port> -f <format>` — Payload generation
- `searchsploit <service_version>` — Exploit database search

**Brute Force & Password:**
- `hydra -l admin -P /usr/share/seclists/Passwords/common-credentials/10k-most-common.txt <target> http-post-form` — Network brute-force
- `john --wordlist=/usr/share/wordlists/rockyou.txt <hashfile>` — Password cracking
- `hashcat -m <mode> <hash> /usr/share/wordlists/rockyou.txt` — GPU password cracking

**Network:**
- `nmap -sV -sC <target>` — Service version + default scripts
- `masscan -p1-65535 <target> --rate=1000` — Ultra-fast port scanner
- `netcat -nv <target> <port>` — Banner grabbing / raw connections
- `tcpdump -i any -w capture.pcap` — Packet capture

**VPN (for lab networks):**
- `openvpn <config.ovpn>` — Connect to HackTheBox/TryHackMe VPN

### Tool Selection Priority
1. **Port scanning** → `nmap_scan` (built-in, parsed output)
2. **Subdomain discovery** → `subdomain_enum` (built-in, multi-engine)
3. **Directory enumeration** → `dir_enum` (built-in) or `kali_sandbox_execute` with `ffuf`/`gobuster` for advanced options
4. **Web vulnerability scanning** → `kali_sandbox_execute` with `nikto`/`nuclei`/`wpscan`
5. **SQL injection** → `kali_sandbox_execute` with `sqlmap`
6. **Custom HTTP requests** → `python_execute`
7. **Everything else** → `kali_sandbox_execute` with the appropriate tool
"""
