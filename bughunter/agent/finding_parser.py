"""Bug Hunter Finding Parser - three-layer vulnerability detection from LLM responses."""

from __future__ import annotations

import re

from bughunter.agent.context import ContextManager, VulnerabilityFinding
from bughunter.agent.runtime_state import RuntimeState
from bughunter.agent.think_filter import strip_think_tags

PROOF_PATTERNS: list[str] = [
    r"difference[:: ]*\d+",
    r"\d+\s*bytes|\d+\s*byte",
    r"(?:Statuscode|response code)?[:: ]*5\d{2}",
    r"SQL.*Error|mysql.*error|sql.*error",
    r"SLEEP\(|BENCHMARK\(|EXTRACTVALUE\(|UPDATEXML\(",
    r"command executionSuccess|whoami|id\s+",
    r"root[:\s]|administrator",
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
    r"CVE-\d{4}-\d{4,}",
    r"Successextract|SuccessGet|Get",
]

NATURAL_LANG_PATTERNS: list[tuple[str, str, str]] = [
    (r"SQLinjection|SQLi|injectionVulnerability", "High", "SQLinjection"),
    (r"RCE|remoteCode execution|command injection|command execution", "Critical", "remoteCode execution"),
    (r"Unauthorized|Not certified|No certification required|Authentication bypass|Certification.*bypass", "High", "Authentication bypass"),
    (r"SSRF|Server request forgery", "High", "SSRF"),
    (r"XSS|cross-site scripting|storage typeXSS|ReflectiveXSS", "Medium", "XSScross-site scripting"),
    (r"CSRF|Cross-site request forgery", "Medium", "CSRF"),
    (r"File contains|PathTraverse|LFI|RFI", "Medium", "File contains/Traverse"),
    (r"weak password|default password|default password|Brute force cracking|blasting", "Medium", "weak password/Brute force cracking"),
    (r"ConfigurationError|Configuration Flaw|Give way.*Configuration", "Medium", "ConfigurationError"),
    (r"sensitive directory|Sensitive documents.*Finding|Table of contents.*Finding", "Info", "sensitive directory/documentFinding"),
    (r"Version.*Too old|MediummiddlewareVersion|Fingerprint.*identify", "Info", "VersionInfo"),
    (r"CVE-\d{4}-\d{4,}", "High", "knownCVEVulnerability"),
]

ELEVATION_KEYWORDS: list[tuple[str, str, str]] = [
    (r"Give way|sensitiveInfo|data breach|personalInfo|\d+piece of data", "High", "data breach"),
    (r"Unauthorized|Not certified|Authentication bypass|No certification required", "High", "Unauthorized access"),
    (r"RCE|command execution|remote code", "Critical", "remoteCode execution"),
    (r"SQLinjection|SQLi|injection", "High", "injectionVulnerability"),
    (r"CVE-\d{4}-\d{4,}", "High", "knownCVEVulnerability"),
    (r"weak password|default password|Violence", "High", "weak password/Brute force cracking"),
    (r"XSS|cross-site scripting", "Medium", "XSS"),
    (r"File contains|PathTraverse", "High", "File contains/Traverse"),
    (r"Return200.*does not exist|200.*Empty content|Empty response.*Bit", "Medium", "Potential authorization bypass"),
    (r"403.*interface|interface exists.*403", "Medium", "403Authentication interception"),
]

URL_PATTERN = re.compile(r'https?://[^\s<>"\')\]]+')
PATH_PATTERN = re.compile(r"(?:/[\w%&=?\-]+)+")


def _collect_location_summary(text: str, max_items: int = 4) -> str:
    seen: set[str] = set()
    items: list[str] = []

    for value in re.findall(URL_PATTERN, text):
        if value not in seen:
            seen.add(value)
            items.append(value)
        if len(items) >= max_items:
            return " | ".join(items)

    for value in re.findall(PATH_PATTERN, text):
        if value not in seen:
            seen.add(value)
            items.append(value)
        if len(items) >= max_items:
            break

    return " | ".join(items)


class FindingParser:
    """Parses LLM responses to extract vulnerability findings and discoveries."""

    def __init__(self, context: ContextManager, runtime: RuntimeState) -> None:
        self.context = context
        self.runtime = runtime

    def parse(self, response: str) -> None:
        """Three-layer detection:
        1. Explicit [Severity] tags
        2. Natural-language vulnerability descriptions
        3. confirmed_facts elevation
        """
        existing_titles = {f.title for f in self.context.state.findings}

        severity_patterns = [
            (r"\[Critical\]\s*(.+?)(?:\n|$)", "Critical"),
            (r"\[High\]\s*(.+?)(?:\n|$)", "High"),
            (r"\[Medium\]\s*(.+?)(?:\n|$)", "Medium"),
            (r"\[Low\]\s*(.+?)(?:\n|$)", "Low"),
        ]
        for pattern, severity in severity_patterns:
            for match in re.findall(pattern, response):
                title = match.strip()
                title = re.sub(r"\*+", "", title).strip(" -—–")
                if title and title not in existing_titles:
                    self.context.state.add_finding(
                        VulnerabilityFinding(
                            title=title,
                            severity=severity,
                            evidence_level="L1",
                            lifecycle_status="candidate",
                        )
                    )
                    existing_titles.add(title)

        clean_response = strip_think_tags(response)
        notes = self.context.state.notes
        if notes:
            clean_notes = [strip_think_tags(n) for n in notes[-5:]]
            evidence_pool = clean_response + " " + " ".join(clean_notes)
        else:
            evidence_pool = clean_response

        for pattern, severity, vuln_type in NATURAL_LANG_PATTERNS:
            canonical_title = f"[automatic] {vuln_type}"
            if canonical_title in existing_titles:
                continue

            vuln_matches = re.findall(pattern, clean_response, re.IGNORECASE)
            if not vuln_matches:
                continue

            has_proof = any(
                re.search(p, clean_response + " " + " ".join(notes[-3:]), re.IGNORECASE)
                for p in PROOF_PATTERNS
            )
            has_confirmed_fact = any(
                re.search(
                    p, " ".join(getattr(self.context.state, "confirmed_facts", [])), re.IGNORECASE
                )
                for p in PROOF_PATTERNS
            )
            if not has_proof and not has_confirmed_fact:
                continue

            proof_snippets: list[str] = []
            for pattern_text in PROOF_PATTERNS:
                for match in re.finditer(pattern_text, evidence_pool, re.IGNORECASE):
                    snippet = match.group(0).strip()[:80]
                    if snippet and snippet not in proof_snippets:
                        proof_snippets.append(snippet)
                    if len(proof_snippets) >= 3:
                        break

            location = _collect_location_summary(evidence_pool)
            proof_text = " | ".join(proof_snippets) if proof_snippets else ""
            evidence = (
                f"{location} | {proof_text}" if location and proof_text else location or proof_text
            )

            self.context.state.add_finding(
                VulnerabilityFinding(
                    title=canonical_title,
                    severity=severity,
                    vuln_type=vuln_type,
                    description=f"Automatic detection:{vuln_matches[0].strip()[:100]}"
                    if vuln_matches
                    else "Automatic detection through natural language patterns",
                    evidence=evidence[:300],
                    evidence_level="L2",
                    lifecycle_status="needs_manual_review"
                    if severity in ("Critical", "High")
                    else "pending_verification",
                )
            )
            existing_titles.add(canonical_title)

        confirmed_facts = getattr(self.context.state, "confirmed_facts", [])
        for fact in confirmed_facts:
            for pattern, severity, vuln_type in ELEVATION_KEYWORDS:
                if re.search(pattern, fact, re.IGNORECASE):
                    title = f"[alreadyConfirm] {fact.strip()[:120]}"
                    if title not in existing_titles:
                        location = _collect_location_summary(evidence_pool)
                        evidence = (
                            f"{location} | passToolverifyConfirm:{fact}"
                            if location
                            else f"passToolverifyConfirm:{fact}"
                        )
                        finding = VulnerabilityFinding(
                            title=title,
                            severity=severity,
                            vuln_type=vuln_type,
                            description=f"passToolverifyConfirm:{fact}",
                            evidence=evidence[:300],
                            evidence_level="L4",
                            lifecycle_status="verified",
                        )
                        finding.mark_verified(note=fact[:200], evidence_level="L4")
                        added = self.context.state.add_finding(finding)
                        if not added:
                            for existing in self.context.state.findings:
                                if existing.finding_id == finding.finding_id or (
                                    existing.vuln_type == finding.vuln_type
                                    and existing.verification_status != "verified"
                                ):
                                    existing.title = finding.title
                                    existing.severity = finding.severity
                                    existing.vuln_type = finding.vuln_type
                                    existing.description = finding.description
                                    existing.evidence = finding.evidence
                                    existing.verified = True
                                    existing.verification_status = "verified"
                                    existing.lifecycle_status = "verified"
                                    existing.evidence_level = "L4"
                                    existing.verified_at = finding.verified_at
                                    existing.verification_note = finding.verification_note
                                    break
                        existing_titles.add(title)
                    break

        clean_response = strip_think_tags(response)
        discovery_markers = [
            r"\[\+\]\s*(.+?)(?:\n|$)",
            r"Finding[:: ]\s*(.+?)(?:\n|$)",
            r"(flag\{[^}]+\})",
            r"(NSSCTF\{[^}]+\})",
            r"(CTF\{[^}]+\})",
        ]
        for pattern in discovery_markers:
            for match in re.findall(pattern, clean_response, re.IGNORECASE):
                note = match.strip()[:200]
                if note and note not in self.context.state.notes:
                    self.context.state.add_note(note)

        confirmed_markers = [
            r"alreadyConfirm[:: ]\s*(.+?)(?:\n|$)",
            r"Confirm[:: ]\s*(.+?)(?:\n|$)",
            r"Verification Successful[:: ]\s*(.+?)(?:\n|$)",
            r"\[✅\]\s*(.+?)(?:\n|$)",
            r"Confirm.*exist",
            r"Vulnerability.*alreadyConfirm",
            r"already.*verify.*Success",
            r"payload.*difference[:: ]*\s*\d+",
            r"difference[:: ]*\s*\d+.*Success",
            r"SLEEP\([^)]+\).*time consuming",
            r"Successextract[:: ]*\s*\S+",
            r"Extract to[:: ]*\s*\S+",
            r"command executionSuccess",
            r"Can be extracted to[:: ]*\s*\S+",
            r"Boolean.*Success|Boolean.*efficient",
            r"Report an error.*Success|Report an error.*efficient",
            r"UNION.*Success|UNION.*efficient",
            r"VulnerabilityConfirm",
        ]
        for pattern in confirmed_markers:
            for match in re.findall(pattern, response, re.IGNORECASE):
                fact = match.strip()[:200]
                if fact and hasattr(self.context.state, "add_confirmed_fact"):
                    self.context.state.add_confirmed_fact(fact)

        assumption_markers = [
            r"hypothesis[:: ]\s*(.+?)(?:\n|$)",
            r"Speculate[:: ]\s*(.+?)(?:\n|$)",
        ]
        for pattern in assumption_markers:
            for match in re.findall(pattern, response, re.IGNORECASE):
                assumption = match.strip()[:200]
                if assumption and assumption not in self.runtime.unverified_assumptions:
                    self.runtime.unverified_assumptions.append(assumption)
