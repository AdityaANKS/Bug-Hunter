"""Time-budgeted scan phase tracker.

Manages a global time budget across four scan phases (quick, standard, deep, report),
enforcing per-phase tool timeouts and providing deadline-aware context for the agent.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ScanPhase(Enum):
    """Ordered scan phases with increasing depth."""
    QUICK = "quick"        # Fast passive recon (dig, whois, curl, headers)
    STANDARD = "standard"  # Active scans (nmap, nikto, ffuf, gobuster)
    DEEP = "deep"          # Exploitation (sqlmap, nuclei, hydra, msf)
    REPORT = "report"      # Compile findings, generate report


# Default phase time allocation weights (must sum to 1.0)
DEFAULT_PHASE_WEIGHTS = [0.20, 0.40, 0.30, 0.10]

# Default per-phase tool timeout caps (seconds)
DEFAULT_TOOL_TIMEOUTS = {
    ScanPhase.QUICK: 30,
    ScanPhase.STANDARD: 120,
    ScanPhase.DEEP: 180,
    ScanPhase.REPORT: 30,
}

# Phase descriptions for the agent prompt
PHASE_DIRECTIVES = {
    ScanPhase.QUICK: (
        "QUICK RECON — Run fast, low-cost checks only. "
        "Use: dig, whois, curl, whatweb, wafw00f, robots.txt, HTTP headers. "
        "Do NOT run nmap full scans or heavy enumeration yet."
    ),
    ScanPhase.STANDARD: (
        "STANDARD SCAN — Run active scanning and enumeration. "
        "Use: nmap -sV, nikto, ffuf, gobuster, wpscan, nuclei (quick templates). "
        "Focus on discovering services, directories, and common vulnerabilities."
    ),
    ScanPhase.DEEP: (
        "DEEP PROBE — Exploit confirmed vulnerabilities and run thorough checks. "
        "Use: sqlmap --batch, hydra, metasploit, manual exploitation, nuclei (full). "
        "Only target services/endpoints discovered in earlier phases."
    ),
    ScanPhase.REPORT: (
        "REPORT PHASE — STOP all scanning immediately. "
        "Compile all findings into a structured penetration test report. "
        "Include: severity, evidence, affected endpoints, and remediation advice."
    ),
}


@dataclass
class ScanBudget:
    """Tracks time budget across scan phases.

    Usage:
        budget = ScanBudget(total_minutes=30)
        budget.start()

        # In the agent loop:
        if budget.is_expired():
            break
        tool_timeout = budget.get_tool_timeout()
        context = budget.to_prompt_context()
    """

    total_minutes: int = 30
    phase_weights: list[float] = field(default_factory=lambda: list(DEFAULT_PHASE_WEIGHTS))
    tool_timeout_quick: int = 30
    tool_timeout_standard: int = 120
    tool_timeout_deep: int = 180

    # Internal state
    _start_time: float = 0.0
    _current_phase: ScanPhase = ScanPhase.QUICK
    _phase_start_time: float = 0.0
    _started: bool = False
    _forced_report: bool = False

    def start(self) -> None:
        """Begin the scan timer."""
        self._start_time = time.monotonic()
        self._phase_start_time = self._start_time
        self._current_phase = ScanPhase.QUICK
        self._started = True

    @property
    def phase(self) -> ScanPhase:
        """Current scan phase."""
        return self._current_phase

    @property
    def total_seconds(self) -> float:
        """Total budget in seconds."""
        return self.total_minutes * 60.0

    @property
    def elapsed_seconds(self) -> float:
        """Seconds elapsed since start."""
        if not self._started:
            return 0.0
        return time.monotonic() - self._start_time

    @property
    def remaining_seconds(self) -> float:
        """Seconds remaining in total budget."""
        return max(0.0, self.total_seconds - self.elapsed_seconds)

    @property
    def remaining_minutes(self) -> float:
        """Minutes remaining (rounded to 1 decimal)."""
        return round(self.remaining_seconds / 60.0, 1)

    @property
    def is_unlimited(self) -> bool:
        """True if no time budget was set."""
        return self.total_minutes <= 0

    def _phase_budget_seconds(self, phase: ScanPhase) -> float:
        """Total seconds allocated to a given phase."""
        phases = list(ScanPhase)
        idx = phases.index(phase)
        if idx < len(self.phase_weights):
            return self.total_seconds * self.phase_weights[idx]
        return 0.0

    def _phase_elapsed(self) -> float:
        """Seconds elapsed in the current phase."""
        return time.monotonic() - self._phase_start_time

    def check_phase_advance(self) -> bool:
        """Check if the current phase's time allocation is exhausted and advance.

        Returns True if phase was advanced.
        """
        if not self._started or self.is_unlimited:
            return False

        # Force report phase if total budget nearly exhausted
        if (
            self._current_phase != ScanPhase.REPORT
            and self.remaining_seconds <= self._phase_budget_seconds(ScanPhase.REPORT)
        ):
            self._current_phase = ScanPhase.REPORT
            self._phase_start_time = time.monotonic()
            self._forced_report = True
            return True

        # Check if current phase time is exhausted
        phase_budget = self._phase_budget_seconds(self._current_phase)
        if self._phase_elapsed() >= phase_budget:
            return self._advance_phase()

        return False

    def _advance_phase(self) -> bool:
        """Move to the next phase."""
        phases = list(ScanPhase)
        idx = phases.index(self._current_phase)
        if idx < len(phases) - 1:
            self._current_phase = phases[idx + 1]
            self._phase_start_time = time.monotonic()
            return True
        return False

    def force_report_phase(self) -> None:
        """Force transition to report phase."""
        self._current_phase = ScanPhase.REPORT
        self._phase_start_time = time.monotonic()
        self._forced_report = True

    def is_expired(self) -> bool:
        """True if the total time budget is exhausted."""
        if self.is_unlimited:
            return False
        return self.elapsed_seconds >= self.total_seconds

    def get_tool_timeout(self, requested_timeout: int = 60) -> int:
        """Get the effective timeout for a tool call.

        Returns the minimum of:
        - The requested timeout
        - The phase-specific max timeout
        - The remaining total budget
        """
        if self.is_unlimited or not self._started:
            return requested_timeout

        phase_max = {
            ScanPhase.QUICK: self.tool_timeout_quick,
            ScanPhase.STANDARD: self.tool_timeout_standard,
            ScanPhase.DEEP: self.tool_timeout_deep,
            ScanPhase.REPORT: 30,
        }.get(self._current_phase, requested_timeout)

        remaining = int(self.remaining_seconds)
        return max(5, min(requested_timeout, phase_max, remaining))

    def to_prompt_context(self) -> str:
        """Generate a context string for the agent prompt.

        Tells the agent what phase it's in, how much time remains,
        and what tools/behavior is appropriate.
        """
        if self.is_unlimited or not self._started:
            return ""

        phase = self._current_phase
        remaining = self.remaining_minutes
        tool_timeout = self.get_tool_timeout()
        directive = PHASE_DIRECTIVES.get(phase, "")

        phase_remaining_sec = max(
            0, self._phase_budget_seconds(phase) - self._phase_elapsed()
        )
        phase_remaining_min = round(phase_remaining_sec / 60.0, 1)

        elapsed_min = round(self.elapsed_seconds / 60.0, 1)

        lines = [
            f"\n{'=' * 60}",
            f"⏱️  SCAN BUDGET: {remaining} min remaining "
            f"(elapsed: {elapsed_min}/{self.total_minutes} min)",
            f"📍 PHASE: {phase.value.upper()} "
            f"({phase_remaining_min} min left in this phase)",
            f"⚡ MAX TOOL TIMEOUT: {tool_timeout}s per command",
            f"📋 DIRECTIVE: {directive}",
            f"{'=' * 60}",
        ]
        return "\n".join(lines)

    def to_status_string(self) -> str:
        """Short status for the REPL status display."""
        if self.is_unlimited:
            return "unlimited"
        if not self._started:
            return f"{self.total_minutes}m (not started)"
        return f"{self.remaining_minutes}m left | Phase: {self._current_phase.value}"
