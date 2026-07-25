"""Prompt/round-context helpers for AgentCore."""

from __future__ import annotations

from typing import Any


def build_round_context(agent: Any, round_num: int, max_rounds: int) -> str:
    """Build context string for the current round in auto loop."""
    state = agent.context.state
    constraints_summary = ""
    constraints_block = (
        state.get_constraints_prompt_block()
        if hasattr(state, "get_constraints_prompt_block")
        else ""
    )
    if constraints_block:
        constraints_summary = f"\n\n{constraints_block}"

    reasoning_summary = ""
    session_config = getattr(agent.config, "session", None)
    reasoning_enabled = getattr(session_config, "reasoning_state_enabled", True)
    if reasoning_enabled:
        reasoning = getattr(state, "reasoning", None)
        reasoning_block = (
            reasoning.to_prompt_block()
            if hasattr(reasoning, "to_prompt_block")
            else ""
        )
        if reasoning_block:
            reasoning_summary = f"\n\n{reasoning_block}"

    reflexion_summary = ""
    reflexion_enabled = getattr(session_config, "reflexion_enabled", True)
    reflexion = getattr(agent.runtime, "reflexion", None)
    if reflexion_enabled and hasattr(reflexion, "to_prompt_block"):
        reflexion_block = reflexion.to_prompt_block()
        if reflexion_block:
            reflexion_summary = f"\n\n{reflexion_block}"
        if hasattr(reflexion, "to_reflection_prompt"):
            reflection_block = reflexion.to_reflection_prompt()
            if reflection_block:
                reflexion_summary += f"\n\n{reflection_block}"

    findings_summary = ""
    if state.findings:
        findings_summary = f"\nalreadyFindingVulnerability: {len(state.findings)} indivual"
        for finding in state.findings[-5:]:
            findings_summary += (
                f"\n  - [{finding.severity}] {finding.title}: {finding.evidence[:100]}"
            )

    user_hint_directive = ""
    if round_num <= agent.runtime.user_vuln_hint_rounds and agent.runtime.user_vuln_hint:
        user_hint_directive = (
            f"\n\n{'=' * 50}\n"
            f"[User clearHint — Step {round_num}/{agent.runtime.user_vuln_hint_rounds} round]\n"
            f"{agent.runtime.user_vuln_hint}\n"
            f"{'=' * 50}\n"
        )
        agent.runtime.user_vuln_hint_rounds -= 1

    steps_summary = ""
    if state.executed_steps:
        recent_steps = state.executed_steps[-8:]
        steps_summary = f"\nRecent steps: {len(state.executed_steps)} total"
        for step in recent_steps:
            steps_summary += f"\n  - {step[:150]}"

    failed_summary = ""
    if state.executed_steps:
        failed_attempts = []
        failure_markers = [
            "Failed",
            "none",
            "Returnsame",
            "intercepted",
            "404",
            "no",
            "not yetSuccess",
            "Invalid",
            "error",
            "failed",
            "still",
            "not found",
            "noneResult",
            "timeout",
            "Block",
            "denied",
            "not exist",
            "Unable",
            "cannot",
            "wrong",
        ]
        for step in state.executed_steps:
            if any(marker in step.lower() for marker in failure_markers):
                failed_attempts.append(step[:150])
        if failed_attempts:
            failed_summary = "\nFailedhistory(Do notrepeat theseOperation):"
            for failure in failed_attempts[-10:]:
                failed_summary += f"\n  ❌ {failure}"

    recon_summary = ""
    if state.recon_data:
        recon_summary = f"\nreconnaissance data: {list(state.recon_data.keys())}"

    resume_summary = ""
    if getattr(state, "resume_summary", ""):
        resume_summary = f"\n\n{state.resume_summary}"

    notes_summary = ""
    if state.notes:
        notes_summary = f"\nImportantnotes: {'; '.join(state.notes[-5:])}"

    facts_summary = ""
    if hasattr(state, "confirmed_facts") and state.confirmed_facts:
        facts_summary = "\nConfirmed fact(ToolVerified, trusted):"
        for fact in state.confirmed_facts[-8:]:
            facts_summary += f"\n  ✅ {fact[:150]}"

    assumptions_summary = ""
    if hasattr(state, "unverified_assumptions") and state.unverified_assumptions:
        assumptions_summary = "\n⚠️ UnverifiedAssume (ReasoningBasic but not yetConfirm,possibleError):"
        for assumption in state.unverified_assumptions[-5:]:
            assumptions_summary += f"\n  ❓ {assumption[:150]}"
        assumptions_summary += "\n→ If an assumption is wrong, the assumptions based on itReasoningAll void! Prioritize validating key assumptions."

    path_warning = ""
    same_path_fails = agent.runtime.same_path_fail_count

    if state.executed_steps:
        recent = state.executed_steps[-8:]
        if len(recent) >= 5:
            recent_text = " ".join(recent).lower()
            stuck_indicators = ["get=", "post=", "payload", "parameter", "try"]
            stuck_count = sum(
                1 for indicator in stuck_indicators if recent_text.count(indicator) >= 3
            )
            if stuck_count >= 1:
                path_warning = (
                    "\n\n⚠️ you are already in the currentPathTried a lotroundBut there was no breakthrough."
                    "\nPlease review the source code again/Info, are there other simpler uses?Path?"
                    "\nlist all possiblePath,ThenSwitch toThe simplest one."
                )

    path_switch_warning = ""
    if not reflexion_enabled and same_path_fails >= 3:
        path_switch_warning = (
            f"\n\n🔴 PathSwitch mandatory command: you are already in the same attackPathsuperiorFailedGot it {same_path_fails} Second-rate!"
            f"\nyouMustFollow these steps now:"
            f"\n1. Stop and list at least 3 strip**completely different**alternative attackPath"
            f"\n   (not replace payload value, but change the attack method: such as from'Bypass the regular'Replace with'Pseudo protocol reading file'or'Array bypass')"
            f"\n2. According to difficulty fromLowarriveHighSortThese alternativesPath"
            f"\n3. Choose the simplest alternativePathStarttry"
            f"\n4. Trying newPathBefore, spend first 1 roundTest your new hypothesis"
            f"\n\n⚠️ Blockcontinue in the samePathChange up payload Worth trying!"
        )
        agent.runtime.same_path_fail_count = 0
        agent.runtime.path_switch_forced = True

    assumption_reminder = ""
    if round_num > 2 and round_num % 3 == 0:
        assumption_reminder = (
            "\n\n🧠 Assumption verification checkpoint:"
            "\nBefore taking the next step, spend 10 Ask yourself in seconds:"
            "\n1. my currentReasoningOn what assumption?"
            "\n2. Have I verified these assumptions? Or are you just taking it for granted?"
            "\n3. If a hypothesis is wrong, my entireReasoningWill the chain collapse?"
            "\n4. i can spend 1 roundSend a request to verify the most critical assumptions?"
            "\n\n❌ Common fatal assumptions:preg_replace Only replace the first match / Python simulation = server behavior / The parameter name is a certain value"
        )

    python_timeout_warning = ""
    python_timeout_rounds = agent.runtime.python_timeout_rounds
    if python_timeout_rounds >= 1:
        python_timeout_warning = (
            "\n\n⚠️ **Code executionWarning**:superiorround Python ScriptTimeout."
            "\nBlockwrite more than 10 lines of complex scripts."
            "\nPrioritize existing onesTool(fetch/python_execute) instead of writing your own crawler/Parse the code."
            "\nBlockExecute the same large script over and over again."
        )

    dead_loop_warning = ""
    rounds_no_progress = agent.runtime.rounds_without_progress
    stale_threshold = agent.config.session.stale_rounds_threshold

    blocked_targets_warning = ""
    blocked_targets = agent.runtime.blocked_targets
    if blocked_targets:
        blocked_targets_warning = (
            f"\n\n🚨 **TargetNot accessibleWarning**:belowTargetVisited multiple times in a rowFailed,BlockTry again:"
            f"\n{chr(10).join(f'  ❌ {target} — alreadyConfirmNot reachable' for target in blocked_targets)}"
            f"\n\nyouMust:"
            f"\n1. Immediately stop accessing the aboveTarget"
            f"\n2. Focus on other survivorsTarget"
            f"\n3. if nothing elseTarget,Switch toalreadyConfirmVulnerabilityin-depth utilization of"
            f"\n4. Do notWaste moreroundUnreachable connection attemptsTarget"
        )

    if rounds_no_progress >= stale_threshold:
        dead_loop_warning = (
            f"\n\n🔴 CriticalWarning: You have been consecutive {rounds_no_progress} roundnothing newFinding!"
            f"\nThis means you are stuck in an endless loop. youMustTake one of the following actions immediately:"
            f"\n1. 🔥 Re-obtain the complete source code (use python_execute + strip_tags)"
            f"\n2. 🔥 Try a completely different attackPath(Change parameter name、Change method、ChangeTool)"
            f"\n3. 🔥 If currentlyInsufficient information, acknowledge and try otherReconnaissancemethod"
            f"\n4. 🔥 Stop repeating the sameOperation! reviewFailedHistory, choosing a new direction"
            f"\n\n⚠️ Repeat the same againOperationwill not make a differenceResult!"
        )
    elif rounds_no_progress >= max(stale_threshold // 2, 2):
        dead_loop_warning = (
            f"\n\n⚠️ Warning: You have been consecutive {rounds_no_progress} roundnothing newFinding."
            f"\nPlease check: Are you repeating the sameOperation? Are there any others that haven’t been tried yet?Path?"
            f"\nIf the current method is notwork,immediatelySwitch toother methods."
        )

    flag_warning = ""
    claimed_flag = agent.runtime.claimed_flag
    flag_verified = agent.runtime.flag_verified
    if claimed_flag and flag_verified:
        flag_warning = (
            f"\n\n✅ FLAG Verified: {claimed_flag}"
            f"\nyour taskCompleted! Please summarize brieflysolve challengeprocess, then label [DONE] End."
            f"\n⚠️ Do notRepeat the verification or send the request again! Summarize immediately andEnd."
        )
    elif claimed_flag and not flag_verified:
        flag_warning = (
            f"\n\n⚠️ You claimed to have found it before flag: {claimed_flag}"
            f"\nBut this flag Not independently verified! youMust:"
            f"\n1. useToolResend payload ConfirmResultReproducible"
            f"\n2. Or use different methods to cross-validate (such as changing a function/Pathread the same content)"
            f"\n3. If verifiedFailed,Mustadmit previous flag yesErrorYes, continuesolve challenge"
            f"\nVerifyingCompleteforward,Do notmark [DONE]"
        )

    ctf_mode_warning = ""
    is_ctf = agent.runtime.is_ctf_mode
    if is_ctf and not claimed_flag:
        ctf_mode_warning = (
            "\n\n🔴 CTF solve challengemodel — Your task is to find flag and verify."
            "\nYou haven't found any yet flag,Blockmark [DONE]."
            "\npleaseAnalysisAlreadyInfo, select the most likely attackPathKeep pushing."
            "\nIf currentlyPathblocked, trySwitch tootherPath."
        )
    elif is_ctf and claimed_flag and not flag_verified:
        ctf_mode_warning = (
            "\n\n🔴 CTF solve challengemodel — you claim to have found flag butUnverified."
            "\nMustuseToolverify flag can only be marked after the authenticity of [DONE]."
            "\nIf verifiedFailed,MustKeep looking for the right flag."
        )

    recon_dim_status = ""
    if agent.runtime.is_recon_phase:
        dim_status_text = state.get_recon_status_text()
        is_complete = state.is_recon_complete()
        rounds_no_progress = agent.runtime.rounds_without_progress

        recon_dim_status = f"\n\n📊 ReconnaissanceDimensionsCompletedegree:\n{dim_status_text}"
        if not is_complete:
            recon_dim_status += (
                "\n\n🔴 Reconnaissancenot yetComplete! There are still dimensions that have not been checked,Blockmark [DONE]."
                "\nPlease continue toCompletePerform checks on the dimensions to ensure that at least oneround."
            )
        elif (is_complete and rounds_no_progress >= 3) or (rounds_no_progress >= 8 + 5):
            output_dir = str(agent.config.session.output_dir.resolve())
            if is_complete:
                trigger_reason = f"All dimensions areCompleted ✅,continuous {rounds_no_progress} roundNo new progress"
            else:
                trigger_reason = f"continuous {rounds_no_progress} roundNo new developments (8+5 safety valve)"
            recon_dim_status += (
                f"\n\n🔴 ★★★ reconnaissance→usePhaseForce switching ★★★\n"
                f"{trigger_reason}.\n"
                f"youMustimmediatelySwitch to[ExploitationPhase], instead of continuing to collectInfoorSaveReport.\n\n"
                f"★ Immediately execute the followingOperation:\n"
                f"1. In replyMediumOutput「Switch toVulnerability Discovery」or「Phase: vuln_discovery」\n"
                f"2. Based on collected reconnaissanceResult(Targetimage/Stand by/APIleakage, etc.),\n"
                f"   to the mostHighThe value of attack surface implementation is practicalExploitation\n"
                f"3. [Block]continueSaveScouting report or callReconnaissancekindTool\n"
                f"4. [Block]Duplicate existingFinding,MustThere are new actual verification steps\n\n"
                f"★ OutputDirectory (reconnaissance reports are automatically generated by the frameworkSave, no need for you to manuallySave):\n"
                f"   {output_dir}\n"
                f"⚠️ This timePentestofTargetis [actualExploitationSuccess], not a reconnaissance report!"
            )
        if round_num < 8:
            recon_dim_status += (
                f"\n\n🔴 ReconnaissancemostLowroundData protection: currentStep {round_num} round,"
                f"mostLowneed 8 round. Even if you think enough is enough, keep going deeper."
            )

    return (
        f"\n\n[spontaneous circulation Round {round_num}/{max_rounds}]"
        f"\ncurrentTarget: {state.target or 'Not configured'}"
        f"\ncurrentPhase: {state.phase.value}"
        f"\nOutputTable of contents: {agent.config.session.output_dir.resolve()}"
        f"{constraints_summary}"
        f"{reasoning_summary}"
        f"{reflexion_summary}"
        f"{user_hint_directive}"
        f"{findings_summary}"
        f"{facts_summary}"
        f"{assumptions_summary}"
        f"{steps_summary}"
        f"{failed_summary}"
        f"{recon_summary}"
        f"{resume_summary}"
        f"{notes_summary}"
        f"{path_warning}"
        f"{path_switch_warning}"
        f"{assumption_reminder}"
        f"{python_timeout_warning}"
        f"{blocked_targets_warning}"
        f"{dead_loop_warning}"
        f"{flag_warning}"
        f"{ctf_mode_warning}"
        f"{recon_dim_status}"
        f"\n\nPlease base on currentStatusand all previousFindingdecide next stepOperation, continue to advancePenetration Testing."
        f"\nNote:Do notrepeat what has been done beforeOperation, focus on advancing to the next step."
        f"\nifFindingImportantclue orCompleteTest, add at the end of reply [DONE] mark."
    )


async def generate_attack_summary(agent: Any) -> str:
    """Generate a detailed attack path summary for the cycle report."""
    state = agent.context.state

    steps = state.executed_steps[-30:] if state.executed_steps else []
    steps_text = (
        "\n".join(f"{i + 1}. {step}" for i, step in enumerate(steps)) if steps else "(No steps recorded)"
    )

    notes = state.notes[-20:] if state.notes else []
    notes_text = "\n".join(f"- {note}" for note in notes) if notes else "(No observation records)"

    findings = state.findings
    if findings:
        lines = []
        for finding in findings:
            evidence = (finding.evidence or "")[:150].strip()
            lines.append(f"[{finding.severity}] {finding.title} | evidence: {evidence or 'none'}")
        findings_text = "\n".join(lines)
    else:
        findings_text = "none"

    prompt = (
        f"Target:{state.target or '?'}  |  currentPhase:{state.phase.value}\n"
        f"\n=== Steps performed ===\n{steps_text}\n"
        f"\n=== Key observations/Result ===\n{notes_text}\n"
        f"\n=== Vulnerability Discovery ===\n{findings_text}\n\n"
        f"pleaseOutputa detailedMediumtext attackPathNarrative, including the following elements:\n"
        f"1. specifically tested URL/Path(like https://target.com/admin/login)\n"
        f"2. Specific techniques used at each step/Tool(like SQLMap blind note、Directory Enumeration、nmap Port Scan)\n"
        f"3. Key response characteristics (such as difference length155byte、HTTP 500Error(Return)\n"
        f"4. VulnerabilityError 500 (Server Error)!!1500.That’s an error.There was an error. Please try again later.That’s all we know.Directory EnumerationFinding /manager/html,command CVE-2023-44487)\n"
        f"5. subdomainFindingsituation (such asFinding api.target.com、cms.target.com wait)\n"
        f"Format requirements: Use natural paragraphs to narrate, no lists, length 200-400 word, pureMediumText, excluding <thinking> Label."
    )

    try:
        client = agent._get_client()
        messages = [{"role": "user", "content": prompt}]
        from bughunter.agent.llm_client import build_chat_completion_kwargs

        response = client.chat.completions.create(
            **build_chat_completion_kwargs(
                agent,
                messages,
                max_tokens=800,
                temperature=0.3,
            )
        )
        if response and response.choices:
            raw = response.choices[0].message.content or ""
            from bughunter.agent.think_filter import strip_think_tags

            return strip_think_tags(raw).strip()
    except Exception:
        pass
    return ""
