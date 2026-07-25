"""Bug Hunter Report Content Filter — clean raw LLM output into pure report text.

FilterTarget:
    - TOOL_CALL Markup and content
    - Python code block (print/open/import wait)
    - Round/Context mark
    - DebugOutput
    - think Label content

OnlyOutputpure Markdown Report text.
"""

from __future__ import annotations

import re
from typing import Optional


class ReportContentFilter:
    """Report contentFilterdevice — from LLM OriginalOutputMediumExtract pure report text."""

    # ── Filtermodel ──────────────────────────────────────────────────────────

    # TOOL_CALL Tags (various formats)
    TOOL_CALL_PATTERNS = [
        # standard format
        re.compile(r"\[TOOL_CALL\]\s*\{[^}]+\}", re.DOTALL),
        # bring tool => Format
        re.compile(r'\[TOOL_CALL\]\s*\{tool\s*=>\s*"[^"]+"\s*,\s*args\s*=>\s*\{[^}]+\}', re.DOTALL),
        # python_execute Format
        re.compile(r'\{tool\s*=>\s*"python_execute"\s*,\s*args\s*=>\s*\{[^}]+\}', re.DOTALL),
        # nmap_scan Format
        re.compile(r'\{tool\s*=>\s*"nmap_scan"\s*,\s*args\s*=>\s*\{[^}]+\}', re.DOTALL),
        # fetch Format
        re.compile(r"\[TOOL_CALL\]\s*```\s*\{[^}]+\}\s*```", re.DOTALL),
        # simplifiedToolcall
        re.compile(r"\[TOOL_CALL\]\s*[\s\S]+?\[/TOOL_CALL\]"),
        # tool_call Format
        re.compile(r"tool_call\s*\(\s*\{[^}]+\}\s*\)", re.DOTALL),
    ]

    # Round mark
    ROUND_PATTERNS = [
        re.compile(r"──\s*Cycle\s*\d+\s*\|\s*Round\s*\d+\s*──", re.DOTALL),
        re.compile(r"──\s*Round\s*\d+\s*──", re.DOTALL),
        re.compile(r"Cycle\s*\d+\s*\|\s*Round\s*\d+", re.IGNORECASE),
        re.compile(r"Round\s+\d+:", re.IGNORECASE),
        re.compile(r"No.\s*\d+\s*round", re.IGNORECASE),
    ]

    # think Label(LLM thought process)
    THINK_PATTERNS = [
        re.compile(
            r"</?(?:think|thinking|result_info)>?[\s\S]*?</?(?:think|thinking|result_info)>?",
            re.IGNORECASE,
        ),
        re.compile(r"</?(?:think|thinking|result_info)>?[\s\S]*", re.IGNORECASE),
        re.compile(r"<thinking>[\s\S]*?</thinking>?", re.IGNORECASE),
        re.compile(r"<thinking>[\s\S]*", re.IGNORECASE),
        re.compile(r"<reasoning>[\s\S]*?</reasoning>?", re.IGNORECASE),
        re.compile(r"<reasoning>?[\s\S]*", re.IGNORECASE),
        re.compile(r"\[think\]", re.IGNORECASE),
        re.compile(r"##\s*think\s*", re.IGNORECASE),
        re.compile(r"###\s*Reasoning\s*", re.IGNORECASE),
    ]

    # Python Code blocks (various formats)
    PYTHON_CODE_PATTERNS = [
        # standard ```python ``` Format
        re.compile(r"```python\s*[\s\S]*?```"),
        # ``` ``` Format (no language identifier)
        re.compile(r"```\s*[\s\S]*?```"),
        # single line print/import statement
        re.compile(r"^\s*print\s*\(", re.MULTILINE),
        re.compile(r"^\s*import\s+", re.MULTILINE),
        re.compile(r"^\s*from\s+\w+\s+import", re.MULTILINE),
        re.compile(r"^\s*with\s+open\s*\(", re.MULTILINE),
        # with statement
        re.compile(r"with\s+open\s*\([^)]+\)\s+as\s+\w+:", re.DOTALL),
        # if __name__ == "__main__"
        re.compile(r'if\s+__name__\s*==\s*["\']__main__["\']:', re.DOTALL),
    ]

    # DebugOutputmark
    DEBUG_PATTERNS = [
        re.compile(r"^\s*──.*──\s*$", re.MULTILINE),  # divider
        re.compile(r"^\s*\[=\]+\s*$", re.MULTILINE),  # ===== style
        re.compile(r"Toolcall|tool_call", re.IGNORECASE),
        re.compile(r"callTool|callResult", re.IGNORECASE),
        re.compile(r"\[LLM\s+[A-Z_]+\]", re.IGNORECASE),  # [LLM THINKING] wait
    ]

    # HTTP ask/response (optionalFilter)
    HTTP_PATTERNS = [
        re.compile(r"HTTP/\d\.\d\s+\d+\s+[^\n]+", re.IGNORECASE),
        re.compile(r"^(GET|POST|PUT|DELETE|HEAD|OPTIONS)\s+/[^\n]+", re.MULTILINE | re.IGNORECASE),
    ]

    # Phasetoggle mark
    PHASE_PATTERNS = [
        re.compile(r"Phaseswitch\s*[→\-]>\s*\w+", re.IGNORECASE),
        re.compile(r"Enter\s*\w+\s*Phase", re.IGNORECASE),
        re.compile(r"currentPhase:\s*\w+", re.IGNORECASE),
    ]

    @classmethod
    def filter(cls, content: str) -> str:
        """Filtercontent, keeping only pure report text.

        Args:
            content: LLM OriginalOutput

        Returns:
            Filterpure report text after
        """
        result = content

        # 1. Remove TOOL_CALL piece
        result = cls._remove_tool_calls(result)

        # 2. Remove Round mark
        result = cls._remove_round_markers(result)

        # 3. Remove think Label
        result = cls._remove_think_tags(result)

        # 4. Remove Python code block
        result = cls._remove_python_code(result)

        # 5. RemoveDebugOutput
        result = cls._remove_debug_output(result)

        # 6. RemovePhasetoggle mark
        result = cls._remove_phase_markers(result)

        # 7. Clean up extra blank lines
        result = cls._cleanup_whitespace(result)

        return result.strip()

    @classmethod
    def _remove_tool_calls(cls, content: str) -> str:
        """Remove TOOL_CALL Related content."""
        result = content

        for pattern in cls.TOOL_CALL_PATTERNS:
            result = pattern.sub("", result)

        # remove independent tool_call OK
        result = re.sub(r"^\s*tool_call\s*\(.*$", "", result, flags=re.MULTILINE)
        result = re.sub(r"^\s*\[TOOL_CALL\]\s*$", "", result, flags=re.MULTILINE)

        return result

    @classmethod
    def _remove_round_markers(cls, content: str) -> str:
        """Remove Round/ Cycle mark."""
        result = content

        for pattern in cls.ROUND_PATTERNS:
            result = pattern.sub("", result)

        return result

    @classmethod
    def _remove_think_tags(cls, content: str) -> str:
        """Remove think Labels and thought process."""
        result = content

        for pattern in cls.THINK_PATTERNS:
            result = pattern.sub("", result)

        return result

    @classmethod
    def _remove_python_code(cls, content: str) -> str:
        """Remove Python code block.

        Note: This isFilter LLM OutputofOriginalcode, not reportMediumcodeExample.
        ReportMediumcodeExample(PoC etc.) should be added via templates, not handled here.
        """
        result = content

        for pattern in cls.PYTHON_CODE_PATTERNS:
            result = pattern.sub("", result)

        # Remove individual chunks import/print statement
        lines = result.split("\n")
        filtered_lines = []
        in_code_block = False

        for line in lines:
            # Detect code block boundaries
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            # If inside a code block,Skipped
            if in_code_block:
                continue

            # FilterSuspicious lines of code
            stripped = line.strip()
            if any(
                stripped.startswith(prefix)
                for prefix in [
                    "import ",
                    "from ",
                    "print(",
                    "with open",
                    "if __name__",
                    "def ",
                    "class ",
                    "return ",
                    "try:",
                    "except:",
                    "requests.",
                    "socket.",
                    "subprocess.",
                ]
            ):
                continue

            filtered_lines.append(line)

        result = "\n".join(filtered_lines)
        return result

    @classmethod
    def _remove_debug_output(cls, content: str) -> str:
        """RemoveDebugOutput."""
        result = content

        for pattern in cls.DEBUG_PATTERNS:
            result = pattern.sub("", result)

        # RemoveToolResultmark
        result = re.sub(r"\[Result\]\s*:?\s*", "", result)
        result = re.sub(r"\[Output\]\s*:?\s*", "", result)

        return result

    @classmethod
    def _remove_phase_markers(cls, content: str) -> str:
        """RemovePhasetoggle mark."""
        result = content

        for pattern in cls.PHASE_PATTERNS:
            result = pattern.sub("", result)

        return result

    @classmethod
    def _cleanup_whitespace(cls, content: str) -> str:
        """Clean up extra blank lines and spaces."""
        # Remove consecutive blank lines (more than2indivual)
        result = re.sub(r"\n{3,}", "\n\n", content)

        # Remove leading and trailing spaces from line
        lines = result.split("\n")
        result = "\n".join(line.strip() for line in lines if line.strip())

        return result

    @classmethod
    def is_pure_markdown(cls, content: str) -> bool:
        """Check if the content is pure Markdown(no interference marks).

        for verificationFilterResultError 500 (Server Error)!!1500.That’s an error.There was an error. Please try again later.That’s all we know.
        """
        # Check if noise markers are included
        interference_patterns = [
            r"\[TOOL_CALL\]",
            r"\{tool\s*=>",
            r"──\s*Round",
            r"──\s*Cycle",
            r"<thinking>",
            r"```python",
            r"^\s*print\s*\(",
            r"^\s*import\s+",
        ]

        for pattern in interference_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return False

        return True


# ── Convenience function ────────────────────────────────────────────────────────────────


def filter_report_content(content: str) -> str:
    """FilterReport content, only keep pure Markdown text.

    This is ReportContentFilter.filter() Convenient packaging.
    """
    return ReportContentFilter.filter(content)


def deduplicate_report_findings(findings: list, threshold: float = 0.75) -> list:
    """Semantically deduplicate a list of VulnerabilityFinding before rendering.

    Semantic deduplication at the reporting layer: in SessionState In addition to precise deduplication, we also perform a layer of semantic merging.
    Make sure the same thing doesn't appear in the reportVulnerabilityof many different expressions. Preserve the party with greater evidence.

    Args:
        findings: VulnerabilityFinding list.
        threshold: Similarity threshold, default 0.75.

    Returns:
        The list after deduplication maintains the order of first appearance.
    """
    from bughunter.agent.finding_similarity import deduplicate_findings

    return deduplicate_findings(findings, threshold=threshold)


def extract_findings_section(content: str) -> Optional[str]:
    """from reportMediumextractVulnerabilitylist part.

    If you can't find a dedicatedVulnerabilitylist,Return None.
    """
    patterns = [
        r"(##\s*Vulnerabilitylist\s*\n[\s\S]*?)(?=##|\Z)",
        r"(##\s*Detailed Findings\s*\n[\s\S]*?)(?=##|\Z)",
        r"(##\s*Findings\s*\n[\s\S]*?)(?=##|\Z)",
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def remove_unverified_findings(content: str) -> str:
    """From the report contentMediumRemoveUnverifiedofVulnerability.

    marked as [Unverified] ofVulnerabilitywill be removed.
    """
    # Remove [Unverified] markedVulnerabilitychapter
    pattern = re.compile(
        r"(###\s*\[[^\]]*\]\s*[^\n]*Unverified[^\n]*\n[\s\S]*?)(?=###|\Z)",
        re.IGNORECASE,
    )
    result = pattern.sub("", content)

    # remove contains [Unverified] Target
    lines = result.split("\n")
    filtered_lines = []
    skip_section = False

    for line in lines:
        # DetectionUnverifiedchapterStart
        if "[Unverified]" in line and line.strip().startswith("###"):
            skip_section = True
            continue

        # Detection ChapterEnd
        if skip_section and line.startswith("##"):
            skip_section = False

        if not skip_section:
            filtered_lines.append(line)

    return "\n".join(filtered_lines)
