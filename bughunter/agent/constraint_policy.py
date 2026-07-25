"""Constraint policy helpers for task, phase, and tool enforcement."""

from __future__ import annotations

from bughunter.agent.context import PentestPhase, TaskConstraints

PHASE_TO_ACTION: dict[PentestPhase, str] = {
    PentestPhase.RECON: "recon",
    PentestPhase.VULN_DISCOVERY: "scan",
    PentestPhase.EXPLOITATION: "exploit",
    PentestPhase.POST_EXPLOITATION: "post_exploitation",
    PentestPhase.REPORTING: "report",
}


def normalize_action_name(action: str) -> str:
    """Normalize action aliases into a shared policy namespace."""
    lowered = (action or "").strip().lower()
    aliases = {
        "run": "run",
        "recon": "recon",
        "scan": "scan",
        "exploit": "exploit",
        "post": "post_exploitation",
        "post_exploitation": "post_exploitation",
        "report": "report",
        "reporting": "report",
        "persistent": "persistent",
    }
    return aliases.get(lowered, lowered)


def validate_action_constraints(action: str, constraints: TaskConstraints) -> str | None:
    """Return a constraint violation message when a task action is out of scope."""
    if constraints.is_empty():
        return None

    normalized = normalize_action_name(action)
    allowed = [normalize_action_name(item) for item in constraints.allowed_actions]
    blocked = [normalize_action_name(item) for item in constraints.blocked_actions]

    # Composite commands (run, persistent) include all phases;
    # fine-grained enforcement happens inside the loop via phase/tool checks.
    if normalized in ("run", "persistent"):
        if normalized in blocked:
            return f"constraint_violation: command '{normalized}' is blocked by task constraints"
        return None

    if allowed and normalized not in allowed:
        return f"constraint_violation: command '{normalized}' is outside allowed actions [{', '.join(allowed)}]"

    if normalized in blocked:
        return f"constraint_violation: command '{normalized}' is blocked by task constraints"

    return None


def validate_phase_transition(
    next_phase: PentestPhase,
    constraints: TaskConstraints,
) -> str | None:
    """Return a constraint violation message when a phase transition is out of scope."""
    action = PHASE_TO_ACTION.get(next_phase)
    if action is None:
        return None
    violation = validate_action_constraints(action, constraints)
    if violation is None:
        return None
    return f"{violation} (phase transition to {next_phase.value})"


# purely local/KnowledgeTool: Disagree withTargetinteractive, not included「Actionscope」constraint
LOCAL_META_TOOLS = {"load_skill_reference", "crypto_decode"}

# truly represent「use」IntentAttack payload characteristics——and transmission method (HTTP method/network library) has nothing to do with
EXPLOIT_PAYLOAD_MARKERS = [
    "union select",
    " or 1=1",
    "'or'",
    "../",
    "..\\",
    "<script",
    "cmd=",
    "php://",
    "data://",
    "extractvalue(",
    "updatexml(",
    "load_file(",
    "into outfile",
    "{{",  # SSTI
    "${",  # SSTI/EL
    "%00",
    "/etc/passwd",
    "/bin/sh",
    "bash -i",
    "nc -e",
    "powershell -e",
]

# python_execute MediumRepresents local command execution/rebound shell Characteristics
PYTHON_EXPLOIT_MARKERS = [
    "os.system",
    "subprocess",
    "pty.spawn",
    "/bin/sh",
    "bash -i",
    "nc -e",
    "reverse_shell",
]


def infer_tool_action(tool_name: str, args: dict[str, object]) -> str:
    """Infer the effective action class of a tool invocation.

    Key Principle: Only「Actual attack payload」It is inferred that exploit;HTTP method、Whether to use requests/urllib
    Waiting for transmission details does not constitute useIntent(recon/scan PhaseIt needs to be sent POST/OPTIONS、use requests detection).
    """
    normalized_tool = (tool_name or "").strip().lower()

    if normalized_tool in LOCAL_META_TOOLS:
        return "recon"  # local onlyOperation,Cooperate validate_tool_action exemption

    if normalized_tool == "nmap_scan":
        return "recon"

    if normalized_tool == "fetch":
        url = str(args.get("url", "") or "").lower()
        method = str(args.get("method", "GET") or "GET").upper()
        body = str(args.get("body", "") or "").lower()
        if any(marker in url or marker in body for marker in EXPLOIT_PAYLOAD_MARKERS):
            return "exploit"
        # The method itself does not represent utilization:GET/HEAD/OPTIONS Belongs to reconnaissance, other (POST (test form, etc.) is a scan
        if method in ("GET", "HEAD", "OPTIONS"):
            return "recon"
        return "scan"

    if normalized_tool == "python_execute":
        code = str(args.get("code", "") or "").lower()
        if any(marker in code for marker in EXPLOIT_PAYLOAD_MARKERS + PYTHON_EXPLOIT_MARKERS):
            return "exploit"
        # use requests/httpx/urllib/socket Do HTTP Detection is scanning, not exploitation
        if any(m in code for m in ("requests.", "httpx.", "urllib", "http.client", "socket")):
            return "scan"
        return "recon"

    if normalized_tool == "brute_force_login":
        return "scan"

    if normalized_tool == "kali_sandbox_execute":
        cmd = str(args.get("command", "") or "").lower()
        # Exploitation tools / payloads
        exploit_tools = [
            "msfconsole", "msfvenom", "metasploit", "exploit",
            "sqlmap", "commix", "beef-xss", "set ",
            "reverse_shell", "meterpreter", "payload",
        ]
        if any(marker in cmd for marker in exploit_tools):
            return "exploit"
        # Scanning / active enumeration tools
        scan_tools = [
            "nmap", "masscan", "nikto", "nuclei", "wpscan",
            "ffuf", "gobuster", "dirb", "dirbuster",
            "hydra", "medusa", "ncrack", "john", "hashcat",
            "wapiti", "arachni", "skipfish", "arjun",
        ]
        if any(marker in cmd for marker in scan_tools):
            return "scan"
        # Default to recon for passive commands (ls, cat, which, etc.)
        return "recon"

    return "scan"


def validate_tool_action(
    tool_name: str, args: dict[str, object], constraints: TaskConstraints
) -> str | None:
    """Return a constraint violation when a tool invocation implies a blocked action."""
    # purely local/KnowledgeToolNot subject toActionrange constraints (LoadDocumentation、compileDecodingdon't touchTarget)
    if (tool_name or "").strip().lower() in LOCAL_META_TOOLS:
        return None
    inferred = infer_tool_action(tool_name, args)
    violation = validate_action_constraints(inferred, constraints)
    if violation is None:
        return None
    return f"{violation} (tool '{tool_name}' inferred action '{inferred}')"
