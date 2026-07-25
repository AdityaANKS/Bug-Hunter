"""Dynamic system prompt assembly for AgentCore."""

from __future__ import annotations

from typing import Optional

from bughunter.agent.prompts import AUTO_PENTEST_INSTRUCTION, RECON_INSTRUCTION, build_system_prompt


def build_dynamic_system_prompt(
    *,
    target: Optional[str],
    phase: Optional[str],
    skill_context: Optional[str],
    mcp_tools: list[dict],
    enable_personnel_dim: bool,
    auto_mode: bool,
    user_input: Optional[str],
    kb_context: str,
) -> str:
    """Build the dynamic system prompt for one turn."""
    prompt = build_system_prompt(
        target=target,
        phase=phase,
        skill_context=skill_context,
        mcp_tools=mcp_tools,
        enable_personnel_dim=enable_personnel_dim,
    )

    if auto_mode:
        prompt += "\n\n" + AUTO_PENTEST_INSTRUCTION

    if user_input:
        recon_triggers = [
            "gather",
            "collect",
            "Reconnaissance",
            "reconnaissance",
            "recon",
            "osint",
            "social engineering",
            "social eng",
            "investigate",
            "Author",
            "personnel",
            "intelligence",
            "AnalysisTarget",
            "TargetAnalysis",
            "asset discovery",
            "subdomain",
        ]
        if any(trigger in user_input.lower() for trigger in recon_triggers):
            if enable_personnel_dim:
                prompt += "\n\n" + RECON_INSTRUCTION
            else:
                recon_no_personnel = RECON_INSTRUCTION.replace(
                    "### Dimension 4: Personnel Info ⚡ Conditional",
                    "### Dimension 4: Personnel Info ⚡ Conditional (not activated — user did not mention social engineering/personnel tracking)",
                )
                recon_no_personnel = (
                    recon_no_personnel.replace(
                        "- [ ] Name & Title",
                        "- [x] Name & Title (not activated, skipped)",
                    )
                    .replace(
                        "- [ ] Birthday & Phone",
                        "- [x] Birthday & Phone (not activated, skipped)",
                    )
                    .replace(
                        "- [ ] Email Address",
                        "- [x] Email Address (not activated, skipped)",
                    )
                    .replace(
                        "- [ ] Social Media Accounts (Bilibili, Weibo, Zhihu, Twitter, LinkedIn, GitHub)",
                        "- [x] Social Media Accounts (not activated, skipped)",
                    )
                    .replace(
                        "- [ ] Cross-platform Correlation (search other platforms using username/email, check emails in historical commits)",
                        "- [x] Cross-platform Correlation (not activated, skipped)",
                    )
                )
                prompt += "\n\n" + recon_no_personnel

    if kb_context:
        prompt += "\n\n" + kb_context

    return prompt
