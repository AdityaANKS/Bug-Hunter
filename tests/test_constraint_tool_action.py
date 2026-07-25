"""Issue #45 Regress:recon/scan The mode should not mistakenly block normal reconnaissance/Scanning tool invocation."""

from __future__ import annotations

from bughunter.agent.constraint_policy import infer_tool_action, validate_tool_action
from bughunter.agent.context import TaskConstraints


def _scope_recon_scan() -> TaskConstraints:
    return TaskConstraints(allowed_actions=["recon", "scan"], blocked_actions=["post_exploitation"])


def test_options_and_post_are_not_exploit():
    # The method itself does not represent exploitation:OPTIONS Belong to reconnaissance、POST Attribute scanning
    assert infer_tool_action("fetch", {"url": "http://t/", "method": "OPTIONS"}) == "recon"
    assert infer_tool_action("fetch", {"url": "http://t/login", "method": "POST", "body": "a=1"}) == "scan"


def test_requests_in_python_is_scan_not_exploit():
    code = "import requests\nrequests.get('http://t/')"
    assert infer_tool_action("python_execute", {"code": code}) == "scan"


def test_local_meta_tools_are_exempt_from_scope():
    scope = _scope_recon_scan()
    # Load skill document / Codec does not touch the target, should not be blocked under any range
    assert validate_tool_action("load_skill_reference", {"skill_name": "x", "reference_name": "y"}, scope) is None
    assert validate_tool_action("crypto_decode", {"operation": "base64_decode", "input": "eA=="}, scope) is None


def test_recon_scan_scope_allows_normal_probing():
    scope = _scope_recon_scan()
    allowed_cases = [
        ("nmap_scan", {"target": "10.0.0.5", "scan_type": "top_ports"}),
        ("fetch", {"url": "http://t/robots.txt", "method": "GET"}),
        ("fetch", {"url": "http://t/", "method": "OPTIONS"}),
        ("fetch", {"url": "http://t/login", "method": "POST", "body": "u=a&p=b"}),
        ("python_execute", {"code": "import requests\nrequests.get('http://t/')"}),
    ]
    for name, args in allowed_cases:
        assert validate_tool_action(name, args, scope) is None, f"{name} should be allowed"


def test_actual_exploit_payloads_still_blocked():
    scope = _scope_recon_scan()
    blocked_cases = [
        ("fetch", {"url": "http://t/?id=1 union select 1,2,3", "method": "GET"}),
        ("fetch", {"url": "http://t/?file=../../etc/passwd", "method": "GET"}),
        ("python_execute", {"code": "import os; os.system('id')"}),
        ("python_execute", {"code": "requests.get('http://t/?cmd=whoami')"}),
    ]
    for name, args in blocked_cases:
        violation = validate_tool_action(name, args, scope)
        assert violation is not None and "exploit" in violation, f"{name} should be blocked as exploit"
