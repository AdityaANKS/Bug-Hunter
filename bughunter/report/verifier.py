"""Bug Hunter Vulnerability Verifier — validate findings before they enter the report.

core principles: unverifiedVulnerability = False Positive = Do not write report

Workflow:
    1. take overVulnerabilityAssume (pending finding)
    2. generate PoC code
    3. pass python_execute implement PoC
    4. judgementResult: verified / rejected
    5. only verified ofVulnerabilityto enter the report
"""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from bughunter.agent.context import VulnerabilityFinding


class VerificationStatus(str, Enum):
    """VulnerabilityverifyStatus."""

    PENDING = "pending"  # To be verified
    VERIFIED = "verified"  # Verification passed
    REJECTED = "rejected"  # verifyFailed/False Positive
    SKIPPED = "skipped"  # SkippedVerify (if alreadyConfirmofFact)


class VerificationResult(str, Enum):
    """verifyResultDetails."""

    # Verified outcomes
    VULN_CONFIRMED = "vuln_confirmed"  # VulnerabilityConfirm
    SENSITIVE_DATA_EXPOSED = "sensitive_data"  # Sensitive data leaked
    SECURITY_BYPASS = "security_bypass"  # Security restriction bypass

    # Rejected outcomes
    FALSE_POSITIVE = "false_positive"  # False Positive
    NO_RESPONSE_DIFF = "no_response_diff"  # No difference in response
    PARAM_INVALID = "param_invalid"  # parameterInvalid
    NORMAL_RESPONSE = "normal_response"  # normal response
    TIMEOUT = "timeout"  # Timeout
    ERROR_403_404 = "error_403_404"  # 403/404 Normal rejection


@dataclass
class VerifiedFinding:
    """verifiedVulnerability Discovery."""

    # fromOriginal finding ofInfo
    original_finding: VulnerabilityFinding

    # verifyStatus
    status: VerificationStatus = VerificationStatus.PENDING
    result: Optional[VerificationResult] = None

    # PoC Info
    poc_code: Optional[str] = None
    poc_output: Optional[str] = None
    poc_executed_at: Optional[str] = None

    # verifyConclusion
    verified_description: str = ""
    verified_evidence: str = ""
    verified_severity: str = ""  # Possibly based on verificationResultAdjustmentCriticaldegree

    # Excludereason (if verifiedFailed)
    rejection_reason: str = ""

    # Validator (yuanInfo)
    verified_by: str = "verifier_module"
    verified_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ── PoC generator ────────────────────────────────────────────────────────────────


class PoCGenerator:
    """according toVulnerabilityhypothesis generation PoC code."""

    # VulnerabilityType → PoC Template mapping
    POC_TEMPLATES: dict[str, str] = {
        "sql_injection": """
import requests

target = "{target}"
params = {{
    "id": "{payload}",
}}

try:
    r = requests.get(target, params=params, timeout=10, verify=False)
    text = r.text.lower()

    # SQL Errorfeature
    sql_errors = [
        "sql syntax", "mysql", "sqlite", "postgres", "oracle",
        "sqlstate", "microsoft sql", "odbc", "syntax error",
        "you have an error in your sql", "warning: mysql",
    ]

    for err in sql_errors:
        if err in text:
            print(f"[CONFIRMED] SQLinjectionVulnerability: DetectedSQLErrorfeature '{err}'")
            print(f"[INFO] responseStatuscode: {{r.status_code}}")
            exit(0)

    # Check for response differences (if provided ok baseline)
    baseline_len = {baseline_len}
    if len(r.content) != baseline_len and baseline_len > 0:
        print(f"[POSSIBLE] Response length exception: {{len(r.content)}} vs baseline {{baseline_len}}")

    print("[REJECTED] not yetDetectedSQLInject features")
except requests.Timeout:
    print("[REJECTED] askTimeout")
except Exception as e:
    print(f"[ERROR] {{e}}")
""",
        "xss": """
import requests
import sys

target = "{target}"
payload = "{payload}"

try:
    r = requests.get(target, params={{"q": payload}}, timeout=10, verify=False)

    if payload in r.text:
        print(f"[CONFIRMED] XSSVulnerability: payloadappear in responseMedium")
        print(f"[INFO] responseMediumInclude: {{payload}}")
        exit(0)

    print("[REJECTED] XSS payloaddoes not appear in responseMedium")
except Exception as e:
    print(f"[ERROR] {{e}}")
""",
        "command_injection": """
import requests

target = "{target}"
params = {{
    "cmd": "{payload}",
}}

try:
    r = requests.get(target, params=params, timeout=10, verify=False)
    text = r.text

    # Command injection features
    cmd_indicators = ["uid=", "gid=", "root:", "/bin/bash", "whoami", "linux"]

    for indicator in cmd_indicators:
        if indicator in text:
            print(f"[CONFIRMED] command injectionVulnerability: Detected '{{indicator}}'")
            exit(0)

    print("[REJECTED] not yetDetectedCommand injection features")
except Exception as e:
    print(f"[ERROR] {{e}}")
""",
        "debug_mode": """
import requests

target = "{target}"

try:
    # Normal request
    r_normal = requests.get(target, timeout=10, verify=False)
    len_normal = len(r_normal.content)

    # DebugMode request
    r_debug = requests.get(target + "/?debug=1", timeout=10, verify=False)
    len_debug = len(r_debug.content)

    print(f"[INFO] Normal response length: {{len_normal}}")
    print(f"[INFO] debug=1 response length: {{len_debug}}")

    # examineDebugInfoGive way
    if len_debug != len_normal:
        diff = len_debug - len_normal
        print(f"[POSSIBLE] DebugThe pattern response is different from the normal response, the difference: {{diff}} byte")

        # Check if sensitivity is really leakedInfo
        debug_content = r_debug.text.replace(r_normal.text, "")
        if debug_content:
            sensitive_keywords = ["password", "secret", "api_key", "token", "db_", "connection"]
            for kw in sensitive_keywords:
                if kw.lower() in debug_content.lower():
                    print(f"[CONFIRMED] DebugPattern leak sensitiveInfo: Detected '{kw}'")
                    exit(0)

        # If only the response length is different but there is no sensitivityInfo, downgraded to Info
        print("[INFO] DebugMode responses differ but notFindingsensitiveInfoleaked, downgraded toInfo")

    # examine debug Related keywords
    if "debug" in r_debug.text.lower() and r_debug.text.lower().count("debug") > r_normal.text.lower().count("debug"):
        print("[POSSIBLE] debugThe pattern contains additionaldebugInfo")

    print("[REJECTED] DebugMode is notFindingobviously sensitiveInfoGive way")

except Exception as e:
    print(f"[ERROR] {{e}}")
""",
        "lfi": """
import requests

target = "{target}"
payload = "{payload}"

try:
    r = requests.get(target, params={{"file": payload}}, timeout=10, verify=False)
    text = r.text.lower()

    # LFI feature
    lfi_indicators = ["root:", "/bin/bash", "/bin/sh", "[boot loader]", "windows"]

    for indicator in lfi_indicators:
        if indicator in text:
            print(f"[CONFIRMED] LFIVulnerability: Detected '{{indicator}}'")
            exit(0)

    print("[REJECTED] not yetDetectedLFIfeature")
except Exception as e:
    print(f"[ERROR] {{e}}")
""",
        "sensitive_file": """
import requests

target = "{target}"
path = "{path}"

try:
    r = requests.get(target + path, timeout=10, verify=False)

    if r.status_code == 200 and len(r.content) > 10:
        print(f"[CONFIRMED] Sensitive files are accessible: {{path}}")
        print(f"[INFO] Statuscode: {{r.status_code}}, length: {{len(r.content)}}")

        # Check contentType
        ct = r.headers.get("content-type", "")
        print(f"[INFO] Content-Type: {{ct}}")

        exit(0)

    print(f"[REJECTED] File is inaccessible or empty: {{r.status_code}}")
except Exception as e:
    print(f"[ERROR] {{e}}")
""",
        "info_disclosure": """
import requests

target = "{target}"

try:
    r = requests.get(target, timeout=10, verify=False)
    headers = {{k.lower(): v.lower() for k, v in r.headers.items()}}

    # check sensitive header
    sensitive_headers = {
        "x-powered-by": "technology stackInfo",
        "server": "serverInfo",
        "x-aspnet-version": "ASP.NETVersion",
        "x-generator": "generatorInfo",
    }

    found = []
    for header, desc in sensitive_headers.items():
        if header in headers:
            found.append(f"{{header}}: {{headers[header][:50]}}")

    if found:
        print(f"[CONFIRMED] InfoGive way: {{len(found)}}a sensitiveheader")
        for f in found:
            print(f"  - {{f}}")
        exit(0)

    print("[INFO] not yetFindingobviousInfoLeak, this is normal securityConfigurationquestion")
    print("[REJECTED] response headerInfoGive way - This isConfigurationProblem, noVulnerability")
except Exception as e:
    print(f"[ERROR] {{e}}")
""",
    }

    @classmethod
    def generate_poc(
        cls,
        finding: VulnerabilityFinding,
        target: str,
        baseline_len: int = 0,
    ) -> str:
        """according toVulnerabilityTypegenerate PoC code.

        Args:
            finding: Vulnerability Discovery
            target: Target URL
            baseline_len: Normal response length (for comparison)

        Returns:
            PoC Python code string
        """
        vuln_type = (finding.vuln_type or "").lower().replace(" ", "_")
        template = cls.POC_TEMPLATES.get(vuln_type)

        if not template:
            # Universal PoC template
            template = cls._generic_template()

        payload = cls._guess_payload(finding)
        replacements = {
            "{target}": target,
            "{payload}": payload,
            "{baseline_len}": str(baseline_len),
            "{path}": payload,
        }
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, value)
        return template

    @classmethod
    def _generic_template(cls) -> str:
        """generate generic PoC template."""
        return """
import requests

target = "{target}"

try:
    print(f"[*] testTarget: {{target}}")

    # CustomValidation logic
    r = requests.get(target, timeout=10, verify=False)
    print(f"[*] responseStatus: {{r.status_code}}")
    print(f"[*] response length: {{len(r.content)}}")

    # TODO: According to specificVulnerabilityTypeAdd validation logic
    print("[INFO] Use a general template, please follow the specificVulnerabilitySupplementary verification logic")

except Exception as e:
    print(f"[ERROR] {{e}}")
"""

    @classmethod
    def _guess_payload(cls, finding: VulnerabilityFinding) -> str:
        """according toVulnerabilityTypeguess payload."""
        vuln_type = (finding.vuln_type or "").lower()

        payloads = {
            "sql": "1' OR '1'='1",
            "xss": "<script>alert(1)</script>",
            "command": ";id",
            "lfi": "../../../etc/passwd",
        }

        for key, payload in payloads.items():
            if key in vuln_type:
                return payload

        return "test"


# ── Validate executor ───────────────────────────────────────────────────────────────


class VerifierExecutor:
    """implement PoC Verify and judgeResult."""

    # Python interpreterPath
    PYTHON_CMD = "python"

    @classmethod
    def execute_poc(cls, poc_code: str, timeout: int = 30) -> tuple[int, str]:
        """implement PoC code.

        Args:
            poc_code: PoC Python code
            timeout: Timeoutnumber of seconds

        Returns:
            (Returncode, Outputcontent)
        """
        # Write to temporary file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(poc_code)
            temp_path = f.name

        try:
            # implement PoC
            result = subprocess.run(
                [cls.PYTHON_CMD, temp_path],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            output = result.stdout + result.stderr
            return result.returncode, output

        except subprocess.TimeoutExpired:
            return -1, "[TIMEOUT] PoC implementTimeout"
        except FileNotFoundError:
            return -2, f"[ERROR] Python Interpreter not found: {cls.PYTHON_CMD}"
        except Exception as e:
            return -3, f"[ERROR] implementFailed: {e}"
        finally:
            # Clean temporary files
            try:
                Path(temp_path).unlink()
            except Exception:
                pass

    @classmethod
    def parse_result(cls, output: str, returncode: int) -> VerificationResult:
        """parse PoC Output, judgment verificationResult.

        Args:
            output: PoC Outputcontent
            returncode: Returncode

        Returns:
            verifyResult
        """
        output_lower = output.lower()

        # implementFailed
        if returncode == -1:
            return VerificationResult.TIMEOUT
        if returncode == -2:
            return VerificationResult.ERROR_403_404
        if returncode != 0:
            return VerificationResult.FALSE_POSITIVE

        # examineConfirmmark
        if "[CONFIRMED]" in output or "[VERIFIED]" in output:
            if "sensitiveInfo" in output or "sensitive" in output_lower:
                return VerificationResult.SENSITIVE_DATA_EXPOSED
            if "bypass" in output or "bypass" in output_lower:
                return VerificationResult.SECURITY_BYPASS
            return VerificationResult.VULN_CONFIRMED

        # Check for rejection flags
        if "[REJECTED]" in output or "[FALSE]" in output:
            return VerificationResult.FALSE_POSITIVE

        # Check response differences
        if "[POSSIBLE]" in output:
            return VerificationResult.NO_RESPONSE_DIFF

        # Check for normal response
        if returncode == 0 and "[CONFIRMED]" not in output:
            return VerificationResult.NORMAL_RESPONSE

        return VerificationResult.FALSE_POSITIVE


# ── hostVerifier ────────────────────────────────────────────────────────────────


class VulnerabilityVerifier:
    """VulnerabilityVerifier — Core verification process."""

    def __init__(self, target: str, baseline_len: int = 0) -> None:
        """initializationVerifier.

        Args:
            target: Target URL
            baseline_len: Normal response length
        """
        self.target = target
        self.baseline_len = baseline_len
        self.verified_findings: list[VerifiedFinding] = []
        self.rejected_findings: list[VerifiedFinding] = []

    def verify(self, finding: VulnerabilityFinding) -> VerifiedFinding:
        """Verify aVulnerability Discovery.

        Args:
            finding: Vulnerability Discovery

        Returns:
            verifiedFinding(IncludingStatusand evidence)
        """
        vf = VerifiedFinding(original_finding=finding)

        # generate PoC
        poc_code = PoCGenerator.generate_poc(
            finding=finding,
            target=self.target,
            baseline_len=self.baseline_len,
        )
        vf.poc_code = poc_code

        # implement PoC
        returncode, output = VerifierExecutor.execute_poc(poc_code)
        vf.poc_output = output
        vf.poc_executed_at = datetime.now().isoformat()

        # parseResult
        result = VerifierExecutor.parse_result(output, returncode)
        vf.result = result

        # according toResultjudgementStatus
        if result in (
            VerificationResult.VULN_CONFIRMED,
            VerificationResult.SENSITIVE_DATA_EXPOSED,
            VerificationResult.SECURITY_BYPASS,
        ):
            vf.status = VerificationStatus.VERIFIED
            vf._build_verified_finding(output)
        else:
            vf.status = VerificationStatus.REJECTED
            vf._build_rejected_finding(result, output)

        # Classified storage
        if vf.status == VerificationStatus.VERIFIED:
            self.verified_findings.append(vf)
        else:
            self.rejected_findings.append(vf)

        return vf

    def verify_batch(self, findings: list[VulnerabilityFinding]) -> list[VerifiedFinding]:
        """Batch verificationVulnerability Discovery.

        Args:
            findings: Vulnerability Discoverylist

        Returns:
            verifiedFindingList (contains only verified)
        """
        verified = []

        for finding in findings:
            vf = self.verify(finding)
            if vf.status == VerificationStatus.VERIFIED:
                verified.append(vf)

        return verified

    def _build_verified_finding(self, output: str) -> None:
        """Build verification passedFindingDetails."""
        vf = self.verified_findings[-1] if self.verified_findings else None
        if not vf:
            return

        original = vf.original_finding

        # fromOutputMediumextractConfirmInfo
        confirmed_lines = [
            line.strip()
            for line in output.split("\n")
            if "[CONFIRMED]" in line or "[VERIFIED]" in line
        ]

        vf.verified_description = (
            f"PoC Verification passed.OriginalDescription: {original.description}"
            if original.description
            else "PoC verifyConfirmVulnerabilityexist"
        )
        vf.verified_evidence = "\n".join(confirmed_lines) if confirmed_lines else output[:500]
        vf.verified_severity = original.severity  # Keep the originalCriticaldegree, can be based onResultAdjustment

    def _build_rejected_finding(
        self,
        result: VerificationResult,
        output: str,
    ) -> None:
        """Build verificationFailedofFindingDetails."""
        vf = self.rejected_findings[-1] if self.rejected_findings else None
        if not vf:
            return

        original = vf.original_finding

        # ExcludeCause mapping
        rejection_reasons = {
            VerificationResult.FALSE_POSITIVE: "PoC Not after executionDetectedVulnerabilitycharacteristics, judged asFalse Positive",
            VerificationResult.NO_RESPONSE_DIFF: "No difference in response, parametersInvalidor not triggeredVulnerability",
            VerificationResult.PARAM_INVALID: "parameterInvalid, unable to verifyVulnerabilityhypothesis",
            VerificationResult.NORMAL_RESPONSE: "Returnnormal response,Vulnerabilitydoes not exist",
            VerificationResult.TIMEOUT: "PoC implementTimeout",
            VerificationResult.ERROR_403_404: "Request denied (403/404),TargetNot available",
        }

        vf.rejection_reason = rejection_reasons.get(
            result,
            f"verifyFailed, reasons: {result.value}",
        )

        # RecordExcludeReason, but not included in the report.
        print(f"[VERIFIER] ExcludeVulnerability: {original.title} | Reason: {vf.rejection_reason}")

    def get_verified_report_findings(self) -> list[VulnerabilityFinding]:
        """Obtain writable reportVulnerabilityList.

        OnlyReturnValidation passedVulnerability, verificationFailedNotReturn.
        """
        result = []

        for vf in self.verified_findings:
            if vf.status == VerificationStatus.VERIFIED:
                # Clone finding AndUpdateverificationInfo
                finding = vf.original_finding.model_copy()
                finding.evidence = vf.verified_evidence
                finding.description = vf.verified_description
                finding.severity = vf.verified_severity
                result.append(finding)

        return result

    def get_summary(self) -> dict[str, Any]:
        """Obtain verification summary."""
        return {
            "total": len(self.verified_findings) + len(self.rejected_findings),
            "verified": len(self.verified_findings),
            "rejected": len(self.rejected_findings),
            "target": self.target,
            "verified_findings": [
                {
                    "title": vf.original_finding.title,
                    "severity": vf.verified_severity,
                    "result": vf.result.value if vf.result else None,
                }
                for vf in self.verified_findings
            ],
            "rejected_findings": [
                {
                    "title": vf.original_finding.title,
                    "reason": vf.rejection_reason,
                }
                for vf in self.rejected_findings
            ],
        }
