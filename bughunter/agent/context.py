"""Bug Hunter session context management — track pentest state across turns."""

from __future__ import annotations

import json
import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, PrivateAttr

from bughunter.agent.blackboard import Blackboard
from bughunter.agent.reasoning_state import ReasoningState


class PentestPhase(str, Enum):
    """Penetration test phases."""

    IDLE = "Ready"
    RECON = "Reconnaissance"
    VULN_DISCOVERY = "Vulnerability Discovery"
    EXPLOITATION = "Exploitation"
    POST_EXPLOITATION = "Post-Exploitation"
    REPORTING = "Report Generation"


class VulnerabilityFinding(BaseModel):
    """A single vulnerability finding."""

    title: str = Field(description="Vulnerability title")
    severity: str = Field(default="Medium", description="Critical/High/Medium/Low/Info")
    vuln_type: str = Field(default="", description="Vulnerability type (SQLi, XSS, RCE, etc.)")
    description: str = Field(default="", description="Detailed description")
    evidence: str = Field(default="", description="Proof/evidence of the finding")
    cve: Optional[str] = Field(default=None, description="Associated CVE ID")
    remediation: str = Field(default="", description="Fix recommendation")
    poc_script: Optional[str] = Field(default=None, description="Generated PoC script path")
    evidence_level: str = Field(default="L1", description="L1-L4 evidence strength")
    lifecycle_status: str = Field(
        default="candidate",
        description="candidate/pending_verification/verified/rejected/needs_manual_review",
    )

    # ★ VulnerabilityverifyStatustrack
    verified: bool = Field(default=False, description="Has it passed PoC verify")
    verification_status: str = Field(
        default="pending", description="verifyStatus: pending/verified/rejected"
    )
    verified_at: Optional[str] = Field(default=None, description="Verification time")
    verification_note: str = Field(default="", description="Verification remarks/Excludereason")

    # ★ VulnerabilityUnique identifier (for deduplication)
    finding_id: str = Field(default="", description="VulnerabilityUnique identifier:vuln_type + target + location")

    def model_post_init(self, *args, **kwargs) -> None:
        # ★ Vulnerability completeness validation
        # If severity is High/Critical but evidence, vuln_type, remediation are all empty,
        # this is a placeholder finding — warn but allow it.
        if self.severity in ("Critical", "High"):
            if not self.evidence and not self.vuln_type and not self.remediation:
                self.title = f"[Unverified] {self.title}"
                self.description = (
                    "(⚠️ thisVulnerabilitylack of verification evidence/vuln_type/Remediationthree fields,"
                    "LLM No actual facts were attached when reportingTest Results. Please add evidence before making it officialVulnerability.)"
                    + (f" {self.description}" if self.description else "")
                )

        # ★ Generate unique identifier
        if not self.finding_id:
            self.finding_id = self._generate_finding_id()
        self._sync_status_fields()

    def _sync_status_fields(self) -> None:
        """Keep lifecycle and evidence metadata consistent with verification state."""
        if self.verified or self.verification_status == "verified":
            self.verified = True
            self.verification_status = "verified"
            self.lifecycle_status = "verified"
            if self.evidence_level in ("", "L1", "L2", "L3"):
                self.evidence_level = "L4"
            return

        if self.verification_status == "rejected":
            self.verified = False
            self.lifecycle_status = "rejected"
            if self.evidence_level in ("", "L1", "L2"):
                self.evidence_level = "L3"
            return

        self.verified = False
        self.verification_status = "pending"
        if self.lifecycle_status == "needs_manual_review":
            if self.evidence_level in ("", "L1"):
                self.evidence_level = "L2"
            return
        if self.lifecycle_status == "candidate":
            self.evidence_level = self.evidence_level or "L1"
            return
        if self.evidence_level in ("", "L1"):
            self.lifecycle_status = "candidate"
            self.evidence_level = "L1"
        else:
            self.lifecycle_status = "pending_verification"

    def mark_manual_review(self, note: str = "", evidence_level: str = "L2") -> None:
        """Mark a finding as requiring manual review."""
        self.verified = False
        self.verification_status = "pending"
        self.lifecycle_status = "needs_manual_review"
        self.evidence_level = evidence_level
        if note:
            self.verification_note = note

    def _generate_finding_id(self) -> str:
        """Generate unique vulnerability identifier for deduplication.

        Key improvement: also checks the evidence field (populated by Layer 2
        auto-detection) in addition to description, since auto-detected findings
        put URLs/paths in evidence, not description.
        """
        location = ""
        # Try description first, then evidence (Layer 2 auto-findings put URLs there)
        for field in (self.description, self.evidence):
            if not field:
                continue
            url_match = re.search(r'https?://[^\s<>"\')\]]+', field)
            if url_match:
                location = url_match.group(0)
                break
            path_match = re.search(r'/[^\s<>"\')\]]+', field)
            if path_match:
                location = path_match.group(0)
                break

        # Use vuln_type as dedup key; location only if non-empty (avoids "SQLinjection_")
        if location:
            return f"{self.vuln_type}_{location}"[:50]
        return self.vuln_type[:50]

    def mark_verified(self, note: str = "", evidence_level: str = "L4") -> None:
        """markVulnerabilityis verified."""
        from datetime import datetime

        self.verified = True
        self.verification_status = "verified"
        self.lifecycle_status = "verified"
        self.evidence_level = evidence_level
        self.verified_at = datetime.now().isoformat()
        self.verification_note = note

    def mark_rejected(self, reason: str, evidence_level: str = "L3") -> None:
        """markVulnerabilityas rejected (False Positive)."""
        from datetime import datetime

        self.verified = False
        self.verification_status = "rejected"
        self.lifecycle_status = "rejected"
        self.evidence_level = evidence_level
        self.verified_at = datetime.now().isoformat()
        self.verification_note = reason


class StepStatus(str, Enum):
    """step executionStatus."""

    SUCCESS = "success"  # Success
    FAILURE = "failure"  # Failed
    SKIPPED = "skipped"  # Skipped
    INFO = "info"  # Reconnaissance


class StepRecord(BaseModel):
    """singlePentestStructured recording of steps.

    Used to generate readable attacksPathsummary.
    """

    phase: PentestPhase = Field(description="AffiliationPhase")
    round: int = Field(default=0, description="roundSecond-rate")
    action: str = Field(default="", description="executableAction(likePort Scan、Vulnerabilitydetection)")
    target: str = Field(default="", description="Target(IP/URL/Pathwait)")
    result: str = Field(default="", description="implementResultsummary")
    status: StepStatus = Field(default=StepStatus.INFO, description="implementStatus")
    detail: str = Field(default="", description="detailedInfo(optional)")

    def to_summary(self) -> str:
        """Convert to readable summary lines."""
        status_icon = {
            StepStatus.SUCCESS: "✅",
            StepStatus.FAILURE: "❌",
            StepStatus.SKIPPED: "⏭️",
            StepStatus.INFO: "ℹ️",
        }.get(self.status, "")

        result = self.result[:60] + ("..." if len(self.result) > 60 else "")
        return f"{status_icon} Round {self.round}: {self.action} → {result}"

    def to_brief(self) -> str:
        """Convert to short summary (for list display)."""
        return f"{self.action}: {self.result}"[:80]


class TaskConstraints(BaseModel):
    """Structured hard constraints for an autonomous pentest task."""

    allowed_ports: list[int] = Field(default_factory=list)
    blocked_ports: list[int] = Field(default_factory=list)
    allowed_hosts: list[str] = Field(default_factory=list)
    blocked_hosts: list[str] = Field(default_factory=list)
    allowed_paths: list[str] = Field(default_factory=list)
    blocked_paths: list[str] = Field(default_factory=list)
    allowed_actions: list[str] = Field(default_factory=list)
    blocked_actions: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    strict_mode: bool = Field(default=False)

    def is_empty(self) -> bool:
        return not any(
            [
                self.allowed_ports,
                self.blocked_ports,
                self.allowed_hosts,
                self.blocked_hosts,
                self.allowed_paths,
                self.blocked_paths,
                self.allowed_actions,
                self.blocked_actions,
                self.notes,
                self.strict_mode,
            ]
        )

    def to_prompt_block(self) -> str:
        """Render constraints into a stable prompt block for every round."""
        if self.is_empty():
            return ""

        lines = ["## Current task hard constraints"]
        if self.allowed_ports:
            lines.append(f"- onlyAllowtestPort: {', '.join(str(p) for p in self.allowed_ports)}")
        if self.blocked_ports:
            lines.append(f"- BlocktestPort: {', '.join(str(p) for p in self.blocked_ports)}")
        if self.allowed_hosts:
            lines.append(f"- onlyAllowtestHost: {', '.join(self.allowed_hosts)}")
        if self.blocked_hosts:
            lines.append(f"- BlocktestHost: {', '.join(self.blocked_hosts)}")
        if self.allowed_paths:
            lines.append(f"- onlyAllowtestPath: {', '.join(self.allowed_paths)}")
        if self.blocked_paths:
            lines.append(f"- BlocktestPath: {', '.join(self.blocked_paths)}")
        if self.allowed_actions:
            lines.append(f"- onlyAllowed Actions: {', '.join(self.allowed_actions)}")
        if self.blocked_actions:
            lines.append(f"- Blocked Actions: {', '.join(self.blocked_actions)}")
        if self.notes:
            lines.append(f"- Other restrictions: {'; '.join(self.notes)}")
        if self.strict_mode:
            lines.append("- strict mode: Only records when out of range, does not actively test, does not callToolimplement.")
        return "\n".join(lines)


class ConstraintViolationEvent(BaseModel):
    """Structured audit event for a blocked constraint violation."""

    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    kind: str = Field(default="constraint_violation")
    code: str = Field(default="", description="Stable violation code")
    severity: str = Field(default="medium", description="low | medium | high")
    source: str = Field(default="", description="command | phase | tool")
    action: str = Field(default="", description="Normalized action name")
    tool_name: str = Field(default="", description="Tool name when source=tool")
    phase: str = Field(default="", description="Current phase label")
    summary: str = Field(default="", description="Human-readable summary")
    detail: str = Field(default="", description="Detailed diagnostic message")


class SessionState(BaseModel):
    """Full session state for a pentest engagement."""

    target: Optional[str] = None
    phase: PentestPhase = PentestPhase.IDLE
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    resume_summary: str = Field(default="", description="Summary of historical results injected on restore")
    resume_meta: dict[str, Any] = Field(default_factory=dict, description="recovery dollarInfo")
    task_constraints: TaskConstraints = Field(default_factory=TaskConstraints)
    constraint_violations: list[str] = Field(default_factory=list)
    constraint_violation_events: list[ConstraintViolationEvent] = Field(default_factory=list)
    reasoning: ReasoningState = Field(default_factory=ReasoningState)
    # TargetdriveSolveengineBlackboardpicture(Fact/Intent), followSessionEndurance
    board: Blackboard = Field(default_factory=Blackboard)
    # Reflectionengine crosscyclememory snapshot (persistent mode), save as dict to avoid reflexion module loopImport
    reflexion_snapshot: dict[str, Any] = Field(default_factory=dict)
    findings: list[VulnerabilityFinding] = Field(default_factory=list)
    recon_data: dict[str, Any] = Field(default_factory=dict)
    # ★ OriginalStep log (backwards compatible)
    executed_steps: list[str] = Field(default_factory=list)
    # ★ Structured step record (used to generate readable summaries)
    step_records: list[StepRecord] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    # ★ Confirmed facts vs unverified assumptions — critical for CTF reasoning
    confirmed_facts: list[str] = Field(default_factory=list, description="PassedToolverifyConfirmofFact")
    unverified_assumptions: list[str] = Field(
        default_factory=list, description="ReasoningMediumbased on butUnverifiedhypothesis"
    )
    # ★ Recon dimension completion tracking — prevent premature [DONE] in info gathering
    recon_dimensions_completed: dict[str, bool] = Field(
        default_factory=lambda: {
            "server": False,  # Dimension 1: ServerInfo(Port/realityIP/OS/Mediummiddleware/database)
            "website": False,  # Dimension 2: WebsiteInfo(Architecture/Fingerprint/WAF/sensitive directory/Source code leaked/Stand by/Cpart)
            "domain": False,  # Dimension three: domain nameInfo(WHOIS/ICPFiling/subdomain/DNS/certificate transparency)
            "personnel": False,  # Dimension 4: PeopleInfo(Conditional trigger — Only activated when social work needs are clear)
        },
        description="Reconnaissance4D modelCompletedegree tracking",
    )
    recon_dimension4_active: bool = Field(default=False, description="Dimension four (peopleInfo) is activated")

    # ★ VulnerabilityDeduplication tracking (PrivateAttr Not subject to Pydantic Field naming restrictions)
    _finding_ids_cache: set[str] = PrivateAttr(default_factory=set)

    # Semantic deduplication similarity threshold (HighThis value is treated as the sameVulnerabilitydifferent expressions)
    semantic_dedup_threshold: float = Field(
        default=0.75, description="Similarity threshold for semantic deduplication (0-1)"
    )

    def add_finding(self, finding: VulnerabilityFinding) -> bool:
        """Add a vulnerability finding with deduplication.

        Deduplication is divided into two layers:
            1. finding_id accurate hash Match (fast)
            2. Semantic similarity matching (capturing"sameVulnerabilitydifferent expressions"),commandThe one with stronger evidence will be retained later.

        Returns:
            True if finding was added, False if duplicate (skipped).
        """
        # generate finding_id(if not already)
        if hasattr(finding, "_sync_status_fields"):
            finding._sync_status_fields()
        if not finding.finding_id:
            finding.finding_id = finding._generate_finding_id()

        # First layer:finding_id Accurate deduplication
        if finding.finding_id in self._finding_ids_cache:
            print(f"[DEDUP] SkippedrepeatVulnerability: {finding.title} (ID: {finding.finding_id})")
            return False

        # Second layer: Semantic similarity deduplication
        from bughunter.agent.finding_similarity import (
            _evidence_strength,
            finding_similarity,
        )

        for idx, existing in enumerate(self.findings):
            if finding_similarity(finding, existing) >= self.semantic_dedup_threshold:
                # commandSemantic repetition: retain the one with stronger evidence
                if _evidence_strength(finding) > _evidence_strength(existing):
                    print(
                        f"[DEDUP-SEM] Semantic repetition, replaced by one with stronger evidenceVulnerability: "
                        f"{finding.title} replace {existing.title}"
                    )
                    self._finding_ids_cache.discard(existing.finding_id)
                    self._finding_ids_cache.add(finding.finding_id)
                    self.findings[idx] = finding
                else:
                    print(f"[DEDUP-SEM] Skippedsemantic repetitionVulnerability: {finding.title}")
                return False

        # Add to tracking collections and lists
        self._finding_ids_cache.add(finding.finding_id)
        self.findings.append(finding)
        return True

    def get_verified_findings(self) -> list[VulnerabilityFinding]:
        """Get verifiedVulnerabilitylist.

        OnlyReturn verified=True ofVulnerability,UnverifiedMissing the markReturn.
        """
        return [f for f in self.findings if f.verified]

    def get_rejected_findings(self) -> list[VulnerabilityFinding]:
        """Get rejectedVulnerabilitylist(False Positive)."""
        return [f for f in self.findings if f.verification_status == "rejected"]

    def get_pending_findings(self) -> list[VulnerabilityFinding]:
        """Get the to-be-verifiedVulnerabilitylist."""
        return [f for f in self.findings if f.verification_status == "pending"]

    def get_candidate_findings(self) -> list[VulnerabilityFinding]:
        """Get findings that are still low-confidence candidates."""
        return [f for f in self.findings if f.lifecycle_status == "candidate"]

    def get_pending_verification_findings(self) -> list[VulnerabilityFinding]:
        """Get findings that have some evidence but still need verification."""
        return [f for f in self.findings if f.lifecycle_status == "pending_verification"]

    def get_manual_review_findings(self) -> list[VulnerabilityFinding]:
        """Get findings that require explicit or implicit manual review."""
        return [
            f
            for f in self.findings
            if (
                f.lifecycle_status == "needs_manual_review"
                or (
                    not f.verified
                    and f.verification_status != "rejected"
                    and f.severity in {"Critical", "High"}
                    and f.lifecycle_status in {"candidate", "pending_verification"}
                )
            )
        ]

    def add_recon_subdomain(self, subdomain: str) -> None:
        """Record a discovered subdomain into recon_data['subdomains'].

        The LLM can call this via python_execute when it discovers subdomains
        during the recon phase (Dimension three). Subdomains are displayed in the
        attack surface summary in reports.
        """
        if "subdomains" not in self.recon_data:
            self.recon_data["subdomains"] = []
        if subdomain and subdomain not in self.recon_data["subdomains"]:
            self.recon_data["subdomains"].append(subdomain)

    def add_constraint_violation(self, message: str) -> None:
        """Record a constraint violation audit event."""
        if not message:
            return
        if message not in self.constraint_violations:
            self.constraint_violations.append(message)
        elif self.constraint_violations and self.constraint_violations[-1] != message:
            self.constraint_violations.append(message)

        self.constraint_violations = self.constraint_violations[-20:]

    def add_constraint_violation_event(
        self,
        *,
        source: str,
        action: str = "",
        tool_name: str = "",
        code: str = "",
        severity: str = "medium",
        summary: str,
        detail: str = "",
    ) -> None:
        """Record a structured constraint violation audit event."""
        event = ConstraintViolationEvent(
            source=source,
            action=action,
            tool_name=tool_name,
            code=code,
            severity=severity,
            phase=self.phase.value if hasattr(self.phase, "value") else str(self.phase),
            summary=summary,
            detail=detail or summary,
        )
        self.constraint_violation_events.append(event)
        self.constraint_violation_events = self.constraint_violation_events[-20:]
        self.add_constraint_violation(summary)

    def add_step(
        self,
        step: str,
        action: str = "",
        target: str = "",
        result: str = "",
        status: StepStatus = StepStatus.INFO,
        detail: str = "",
    ) -> None:
        """Record an executed step.

        Args:
            step: Original step string (for backward compatibility).
            action: Short action description (e.g. "Port Scan", "Vulnerabilitydetection").
            target: Target of the action (e.g. "192.168.1.1:80", "/admin/login").
            result: Brief result summary (e.g. "Finding22openPort").
            status: Execution status.
            detail: Optional detailed information.
        """
        # reserveOriginalSteps (backwards compatible), continuous deduplication to avoid title swiping and contaminating reports
        if not self.executed_steps or self.executed_steps[-1] != step:
            self.executed_steps.append(step)
        # Note: step_records creation removed — it was dead code after the return above

        # CreateStructured records
        if action:
            record = StepRecord(
                phase=self.phase,
                round=len(self.executed_steps),
                action=action,
                target=target,
                result=result or step[:60],
                status=status,
                detail=detail,
            )
            self.step_records.append(record)

    def get_step_summary(self) -> dict[str, Any]:
        """Generate attackPathsummary.

        Returns:
            according toPhaseSummary of steps grouped, including keyFinding.
        """
        # ★ Prefer structured step_records
        if self.step_records:
            return self._build_step_summary_from_records()

        # ★ Fallback: fromOriginal executed_steps parse structuredInfo
        if self.executed_steps:
            return self._parse_raw_steps()

        return {"total_steps": 0, "phases": {}, "key_findings": []}

    def _build_step_summary_from_records(self) -> dict[str, Any]:
        """from structured step_records Build summary."""
        # according toPhaseGroup
        phases: dict[str, list[StepRecord]] = {}
        for record in self.step_records:
            phase_name = record.phase.value
            if phase_name not in phases:
                phases[phase_name] = []
            phases[phase_name].append(record)

        # Generate eachPhaseSummary of
        phase_summaries = {}
        for phase_name, records in phases.items():
            phase_summaries[phase_name] = {
                "count": len(records),
                "actions": list(set(r.action for r in records)),
                "success_count": len([r for r in records if r.status == StepStatus.SUCCESS]),
                "failure_count": len([r for r in records if r.status == StepStatus.FAILURE]),
                "key_results": [r.to_brief() for r in records if r.status == StepStatus.SUCCESS][
                    :5
                ],
            }

        # Extract keyFinding
        key_findings = [
            r.to_brief() for r in self.step_records if r.status == StepStatus.SUCCESS and r.result
        ][:10]

        return {
            "total_steps": len(self.step_records),
            "phases": phase_summaries,
            "key_findings": key_findings,
        }

    def _parse_raw_steps(self) -> dict[str, Any]:
        """fromOriginal executed_steps Parse out a human-readable summary of the steps.

        when step_records Used when empty (backward compatibility).
        """
        import re

        # keyword pattern
        DISCOVERY_KEYWORDS = [
            "Finding",
            "Vulnerability",
            "Port",
            "Serve",
            "Path",
            "leaked",
            "Confirm",
            "verify",
            "Success",
            "connect",
            "accessible",
            "CVE",
            "flag",
            "sensitive",
        ]
        FAILURE_KEYWORDS = [
            "Failed",
            "Error",
            "Timeout",
            "reject",
            "intercept",
            "Unable",
            "404",
            "502",
            "503",
            "not exist",
            "Failed",
            "connectFailed",
        ]

        phases: dict[str, dict] = {}
        key_findings: list[str] = []
        total_steps = len(self.executed_steps)

        for i, step in enumerate(self.executed_steps):
            # extract Round Number
            round_match = re.search(r"Round\s*(\d+)", step)
            int(round_match.group(1)) if round_match else i + 1

            # judgementSuccess/Failed
            has_failure = any(kw in step for kw in FAILURE_KEYWORDS)
            has_discovery = any(kw in step for kw in DISCOVERY_KEYWORDS)

            if has_discovery and not has_failure:
                status = StepStatus.SUCCESS
            elif has_failure:
                status = StepStatus.FAILURE
            else:
                status = StepStatus.INFO

            # extractAction(The first meaningful sentence)
            action = self._extract_action(step)

            # extractResult(FindingkeyInfo)
            result = self._extract_result(step)

            # assigned toPhase(Guess based on keywords)
            phase = self._guess_phase(step)

            if phase not in phases:
                phases[phase] = {
                    "count": 0,
                    "actions": set(),
                    "success_count": 0,
                    "failure_count": 0,
                    "key_results": [],
                }

            phases[phase]["count"] += 1
            if action:
                phases[phase]["actions"].add(action)
            if status == StepStatus.SUCCESS:
                phases[phase]["success_count"] += 1
                if result:
                    phases[phase]["key_results"].append(f"{action}: {result}" if action else result)
            elif status == StepStatus.FAILURE:
                phases[phase]["failure_count"] += 1

            # collect keyFinding
            if status == StepStatus.SUCCESS and result:
                key_findings.append(f"{action}: {result}" if action else result)

        # Convert phases Mediumof set for list(JSON serialization)
        phase_summaries = {}
        for phase_name, data in phases.items():
            phase_summaries[phase_name] = {
                "count": data["count"],
                "actions": list(data["actions"])[:5],
                "success_count": data["success_count"],
                "failure_count": data["failure_count"],
                "key_results": data["key_results"][:5],
            }

        return {
            "total_steps": total_steps,
            "phases": phase_summaries,
            "key_findings": key_findings[:10],
        }

    def get_constraints_prompt_block(self) -> str:
        """Return a stable prompt block for current task constraints."""
        return self.task_constraints.to_prompt_block()

    def _extract_action(self, step: str) -> str:
        """from step textMediumextract briefActionDescription."""
        import re

        # Extract clear ones firstActionword
        action_patterns = [
            r"try[^\s, .]+",
            r"test[^\s, .]+",
            r"scanning[^\s, .]+",
            r"detection[^\s, .]+",
            r"enumerate[^\s, .]+",
            r"verify[^\s, .]+",
            r"use[^\s, .]+",
            r"examine[^\s, .]+",
            r"Analysis[^\s, .]+",
            r"access[^\s, .]+",
            r"connect[^\s, .]+",
        ]
        for pattern in action_patterns:
            match = re.search(pattern, step)
            if match:
                action = match.group(0)[:20]
                return action

        # Fallback: Extract the first meaningful sentence (remove Round No. and thinking tags)
        clean = re.sub(r"Round\s*\d+:", "", step)
        clean = re.sub(r"<think>.*?</think>", "", clean)
        clean = clean.strip()[:40]
        return clean if clean else "Execution steps"

    def _extract_result(self, step: str) -> str:
        """from step textMediumextractResultsummary."""
        import re

        # extractFindingkindResult
        discovery_patterns = [
            r"Finding[^\s,。；]+",
            r"Confirm[^\s,。；]+",
            r"Vulnerability[^\s,。；]+",
            r"Port[^\s,。；]+",
            r"Path[^\s,。；]+",
            r"connect[^\s,。；]+",
            r"Return[^\s,。；]+",
            r"accessible[^\s,。；]+",
            r"Success[^\s,。；]+",
        ]
        for pattern in discovery_patterns:
            match = re.search(pattern, step)
            if match:
                result = match.group(0)[:50]
                # Remove content from thinking tags
                result = re.sub(r"<think>.*?</think>", "", result)
                return result.strip()

        # extractFailedreason
        failure_patterns = [
            r"Failed[^\s,。；]+",
            r"Error[^\s,。；]+",
            r"Timeout[^\s,。；]+",
            r"reject[^\s,。；]+",
            r"intercept[^\s,。；]+",
            r"Unable[^\s,。；]+",
            r"404[^\s,。；]+",
        ]
        for pattern in failure_patterns:
            match = re.search(pattern, step)
            if match:
                return match.group(0)[:50]

        return ""

    def _guess_phase(self, step: str) -> str:
        """Guess which one belongs based on the step contentPhase."""
        # Phasetoggle mark
        if "Phaseswitch" in step or "Enter" in step:
            if "Reconnaissance" in step or "Recon" in step:
                return "Reconnaissance"
            elif "Vulnerability Discovery" in step or "Vulnerabilitydetection" in step:
                return "Vulnerability Discovery"
            elif "Exploitation" in step or "use" in step:
                return "Exploitation"
            elif "Report" in step:
                return "Report Generation"

        # Keyword determination
        recon_keywords = ["Port", "Serve", "Fingerprint", "Architecture", "WAF", "Table of contents", "subdomain", "WHOIS"]
        vuln_keywords = ["Vulnerability", "injection", "XSS", "SQL", "CSRF", "SSTI", "detection"]
        exploit_keywords = ["use", "PoC", "verify", "exploit", "Verification Successful"]

        for kw in exploit_keywords:
            if kw in step:
                return "Exploitation"

        for kw in vuln_keywords:
            if kw in step:
                return "Vulnerability Discovery"

        for kw in recon_keywords:
            if kw in step:
                return "Reconnaissance"

        return self.phase.value  # Use currentPhase

    def add_note(self, note: str) -> None:
        """Add a session note, filtering out code/symbol-heavy noise."""
        import re as _re

        # Reject notes that are primarily code/symbols — these pollute evidence extraction
        # and create fake URLs/paths in findings.
        # Count Chinese characters vs code symbols
        chinese = _re.findall(r"[\u4e00-\u9fff]", note)
        code_symbols = _re.findall(
            r"[{}()=+*/<>\-\\[\\]|;|import |def |return |print\(|requests\.|socket\.|re\.|sys\.]",
            note,
        )
        if len(note) > 20 and len(code_symbols) > len(chinese) * 0.5:
            # Too much code, skip it
            return
        # Reject very short notes that are just code symbols or numbers
        if len(note) < 5 or note in ("---", "**", ">>>", "..."):
            return
        self.notes.append(note)

    def add_confirmed_fact(self, fact: str) -> None:
        """Add a confirmed fact (verified by tool output)."""
        if fact and fact not in self.confirmed_facts:
            self.confirmed_facts.append(fact)
        if fact:
            self.reasoning.add_fact(
                key=self._fact_key_from_text(fact),
                value=fact,
                source="confirmed_fact",
                confidence=0.9,
            )

    def _fact_key_from_text(self, fact: str) -> str:
        text = fact.lower()
        if "cve-" in text:
            return "cve"
        if "http://" in text or "https://" in text:
            return "url"
        if "port" in text or "Port" in fact:
            return "port"
        if "server" in text or "x-powered-by" in text:
            return "service"
        if "waf" in text:
            return "waf"
        return "confirmed_fact"

    def add_assumption(self, assumption: str) -> None:
        """Add an unverified assumption."""
        if assumption and assumption not in self.unverified_assumptions:
            self.unverified_assumptions.append(assumption)

    def mark_recon_dimension(self, dimension: str) -> None:
        """Mark a recon dimension as completed.

        Args:
            dimension: One of 'server', 'website', 'domain', 'personnel'
        """
        if dimension in self.recon_dimensions_completed:
            self.recon_dimensions_completed[dimension] = True

    def is_recon_complete(self) -> bool:
        """Check if all active recon dimensions have been completed at least once.

        Dimension 4 (personnel) is only checked if it's been activated.
        """
        for dim, completed in self.recon_dimensions_completed.items():
            if dim == "personnel" and not self.recon_dimension4_active:
                continue  # Skip inactive dimension 4
            if not completed:
                return False
        return True

    def get_recon_status_text(self) -> str:
        """Get a human-readable recon dimension completion status."""
        parts = []
        dim_names = {
            "server": "Dimension one(server)",
            "website": "Dimension two(website)",
            "domain": "Dimension three(domain name)",
            "personnel": "Dimension four(personnel)",
        }
        for dim, completed in self.recon_dimensions_completed.items():
            if dim == "personnel" and not self.recon_dimension4_active:
                continue  # Skip inactive dimension 4
            name = dim_names.get(dim, dim)
            parts.append(f"{'✅' if completed else '❌'} {name}")
        incomplete = [
            dim
            for dim, done in self.recon_dimensions_completed.items()
            if (dim != "personnel" or self.recon_dimension4_active) and not done
        ]
        status = " | ".join(parts)
        if incomplete:
            status += f"\n→ besides {len(incomplete)} dimensions have not been checked, continue to collect,Do notmark [DONE]"
        return status

    def advance_phase(self, phase: PentestPhase) -> None:
        """Move to a new phase."""
        old_phase = self.phase
        self.phase = phase
        # RecordPhaseswitch
        self.add_step(
            step=f"Phaseswitch → {phase.value}",
            action="Phaseswitch",
            target=f"{old_phase.value} → {phase.value}",
            result=f"Enter{phase.value}Phase",
            status=StepStatus.INFO,
        )

    def save(self, path: Optional[Path] = None) -> Path:
        """Save session state to JSON file."""
        if path is None:
            from bughunter.config.settings import SESSIONS_DIR

            safe_target = (self.target or "unknown").replace("/", "_").replace(":", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = SESSIONS_DIR / f"{timestamp}_{safe_target}.json"

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(mode="json"), f, ensure_ascii=False, indent=2)
        return path

    @classmethod
    def load(cls, path: Path) -> "SessionState":
        """Load session state from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)


class ContextManager:
    """Manages conversation context and session state."""

    def __init__(self, max_history: int = 200) -> None:
        self.max_history = max_history
        self.messages: list[dict[str, str]] = []
        self.state = SessionState()

    def add_user_message(self, content: str) -> None:
        """Add a user message to context."""
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to context."""
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def add_system_message(self, content: str) -> None:
        """Add a system message (inserted at beginning)."""
        # System messages are handled separately in the API call
        pass

    def get_messages(self) -> list[dict[str, str]]:
        """Get conversation messages for API call."""
        return self.messages.copy()

    def reset(self) -> None:
        """Reset context and session state."""
        self.messages = []
        self.state = SessionState()

    def _trim(self) -> None:
        """Trim old messages to stay within limit.

        Instead of blindly dropping old messages, we compress them
        into a summary to preserve key discoveries for multi-round loops.
        """
        if len(self.messages) <= self.max_history:
            return

        # Keep the most recent 70% of messages intact
        keep_count = int(self.max_history * 0.7)
        recent = self.messages[-keep_count:]
        old = self.messages[:-keep_count]

        # Compress old messages into a summary instead of discarding
        summary = self._compress_messages(old)

        self.messages = []
        if summary:
            self.messages.append(
                {
                    "role": "system",
                    "content": f"[previousSessionsummary]\n{summary}",
                }
            )
        self.messages.extend(recent)

    @staticmethod
    def _compress_messages(messages: list[dict[str, str]]) -> str:
        """Compress a list of messages into a concise summary.

        Extracts key findings, tool results, and discoveries from the
        conversation history so the LLM doesn't completely lose context.
        """
        key_parts = []

        for msg in messages:
            content = msg.get("content", "")
            # Extract tool call/result information — these contain actual findings
            if "callTool:" in content or "ToolResult:" in content:
                key_parts.append(content[:300])

            # Extract lines that look like findings/discoveries
            for line in content.split("\n"):
                stripped = line.strip()
                if any(
                    marker in stripped
                    for marker in [
                        "[+]",
                        "[!]",
                        "[-]",
                        "Finding",
                        "Vulnerability",
                        "flag",
                        "CVE",
                        "Port",
                        "open",
                        "Serve",
                        "Path",
                        "leaked",
                        "injection",
                        "Status:",
                        "Headers:",
                        "Body",
                        # ★ Negative/failure markers — critical for CTF to avoid repeating
                        "Failed",
                        "Invalid",
                        "none",
                        "Returnsame",
                        "intercepted",
                        "not yetSuccess",
                        "not exist",
                        "Error",
                        "404",
                        "timeout",
                        # ★ Confirmed fact markers — verified by actual tool output
                        "alreadyConfirm",
                        "Confirm",
                        "Verification Successful",
                        "verified",
                        "confirmed",
                        # ★ Assumption markers — things the LLM assumed but didn't verify
                        "hypothesis",
                        "should",
                        "possible",
                        "Speculate",
                        "guess",
                        "estimate",
                    ]
                ):
                    key_parts.append(stripped[:200])

        if not key_parts:
            return ""

        # Limit total summary size to avoid context bloat
        summary = "\n".join(key_parts)
        if len(summary) > 3000:
            summary = summary[:3000] + "\n...(More history has been omitted)"

        return summary

    def trim_messages(self, max_messages: int = 20) -> None:
        """Forcefully trim conversation history to a specific size.

        Used when context overflow causes repeated LLM errors.
        """
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]
