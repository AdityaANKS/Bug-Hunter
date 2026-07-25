"""Bug Hunter MCP Router — route natural language intents to MCP tool calls."""

from __future__ import annotations

import re
from typing import Any, Optional

# ── Intent → Tool mapping ───────────────────────────────────────────

INTENT_TOOL_MAP: dict[str, list[dict[str, Any]]] = {
    # Browser automation
    "Open web page|accessurl|Visit page|navigate": [
        {"tool": "new_page", "server": "chrome-devtools"},
        {"tool": "navigate", "server": "chrome-devtools"},
    ],
    "screenshot|screenshot|screenshot": [
        {"tool": "screenshot", "server": "chrome-devtools"},
    ],
    "implementjs|eval js|runjavascript": [
        {"tool": "evaluate_js", "server": "chrome-devtools"},
    ],
    # HTTP requests
    "send request|httpask|fetch|Access interface|callapi": [
        {"tool": "fetch", "server": "fetch"},
        {"tool": "send_http1_request", "server": "burp"},
    ],
    # Burp Suite
    "Capture packets|View request|intercept request|proxy": [
        {"tool": "get_proxy_http_history", "server": "burp"},
    ],
    "Modify data packet|replay|replay|tamper": [
        {"tool": "send_http1_request", "server": "burp"},
    ],
    # Memory
    "remember|Record|save memory": [
        {"tool": "save", "server": "memory"},
    ],
    "remember|Query records|retrieve memory": [
        {"tool": "retrieve", "server": "memory"},
    ],
}


class MCPRouter:
    """Routes natural language intents to MCP tool calls."""

    def route(self, user_input: str) -> list[dict[str, Any]]:
        """Analyze user input and return suggested tool calls.

        Returns a list of dicts with keys: tool, server, confidence.
        """
        input_lower = user_input.lower()
        results = []

        for pattern, tools in INTENT_TOOL_MAP.items():
            keywords = pattern.split("|")
            if any(kw in input_lower for kw in keywords):
                for tool_entry in tools:
                    results.append(
                        {
                            "tool": tool_entry["tool"],
                            "server": tool_entry["server"],
                            "confidence": 0.8,
                        }
                    )

        return results

    def extract_url(self, text: str) -> Optional[str]:
        """Extract URL from text."""
        url_match = re.search(r"(https?://\S+)", text)
        return url_match.group(1) if url_match else None

    def extract_ip(self, text: str) -> Optional[str]:
        """Extract IP address from text."""
        ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", text)
        return ip_match.group(1) if ip_match else None

    def suggest_tools_for_phase(self, phase: str) -> list[dict[str, Any]]:
        """Suggest tools based on pentest phase."""
        phase_tools = {
            "Reconnaissance": [
                {"tool": "fetch", "server": "fetch", "reason": "HTTP Request probeTarget"},
                {"tool": "new_page", "server": "chrome-devtools", "reason": "Browser accessTarget"},
                {"tool": "screenshot", "server": "chrome-devtools", "reason": "Screenshot recordTargetpage"},
            ],
            "Vulnerability Discovery": [
                {"tool": "fetch", "server": "fetch", "reason": "sendVulnerabilityprobe request"},
                {"tool": "send_http1_request", "server": "burp", "reason": "Detection requests via proxy constructs"},
            ],
            "Exploitation": [
                {"tool": "send_http1_request", "server": "burp", "reason": "Construct utilization request"},
                {"tool": "fetch", "server": "fetch", "reason": "send exploit payload"},
                {"tool": "evaluate_js", "server": "chrome-devtools", "reason": "In-browser use"},
            ],
        }

        return phase_tools.get(phase, [])
