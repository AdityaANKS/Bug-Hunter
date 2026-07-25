"""Targetdriven OODA Solvecycle — useBlackboardFigure replacement fixedroundnumber workflow.

Loop structure (no fixedroundnumber):
  1. use origin/goal Sowing initial Fact.
  2. REASON:Read the whole picture → judgmentTargetIs it achieved? / propose newExplore Intent / Not proposed.
  3. EXPLORE: Get one Intent,useToolactual implementation, putConfirmofConclusionwrite back as a new Fact.
  4. Termination conditions:Goal achieved / Exploration frontier exhausted(none Intent and Reason not proposed again)/ reachSafety budget.

Safety budget(max_steps) is just an upper limit to prevent loss of control, not a workflowPhasecount;
Normally the loop will be in「Goal achieved」or「Front exhaustion」time in advanceEnd.
"""

from __future__ import annotations

import asyncio
import contextvars
import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from bughunter.agent.blackboard import Blackboard, BoardIntent, IntentStatus
from bughunter.agent.llm_client import build_chat_completion_kwargs, call_llm_auto
from bughunter.agent.think_filter import strip_think_tags

# Markers indicating exploration has advanced / confirmed a conclusion (broad matching)
_ADVANCE_MARKERS = [
    "Confirm",
    "Success",
    "obtained",
    "retrieved",
    "extracted",
    "flag{",
    "flag ",
    "bypass successful",
    "reflection",
    "vulnerability exists",
    "Finding",
    "Return200",
    "Return 200",
    "status: 200",
    "unauthorized",
    "no auth required",
    "endpoint accessible",
    "info disclosure",
    "critical finding",
    "major finding",
    "exposed",
    "leaked",
    "200 ok",
    "cors",
    "writable",
    "uploadable",
    "downloadable",
    "weak password",
    "Injection Point",
    "xss",
    "sql inject",
]
# Markers indicating a dead-end direction
_DEAD_END_MARKERS = [
    "not exist",
    "Unable",
    "Failed",
    "dead end",
    "no finding",
    "no injection",
    "no reflection",
    "Exclude",
]
# Negation markers in completion reason — used to detect when model claims non-achievement in the complete field
_NEGATION_MARKERS = [
    "not reached",
    "not achieved",
    "not recorded",
    "not found",
    "not completed",
    "unable to",
    "not yet",
    "none",
    "insufficient",
    "cannot prove",
    "cannot confirm",
    "cannot demonstrate",
    "not satisfied",
]


def _has_negation(text: str) -> bool:
    """Check if completion reason contains negation markers (indicating non-achievement)."""
    return any(m in (text or "") for m in _NEGATION_MARKERS)


_current_worker: contextvars.ContextVar["ExploreWorker | None"] = contextvars.ContextVar(
    "_current_worker", default=None
)


@dataclass
class ExploreWorker:
    intent_id: str
    evidence_buffer: list[str] = field(default_factory=list)
    tc_start: int = 0


class BoardGuard:
    """Serialise mutating Blackboard operations with an asyncio.Lock."""

    def __init__(self, board: Blackboard) -> None:
        self._board = board
        self._lock = asyncio.Lock()

    async def add_fact(self, description: str, source: str = "") -> Any:
        async with self._lock:
            return self._board.add_fact(description, source)

    async def conclude_intent(self, intent_id: str, fact_desc: str, source: str = "") -> Any:
        async with self._lock:
            return self._board.conclude_intent(intent_id, fact_desc, source)

    async def abandon_intent(self, intent_id: str, note: str = "") -> Any:
        async with self._lock:
            return self._board.abandon_intent(intent_id, note)

    async def record_tool_call(self, **kwargs: Any) -> None:
        async with self._lock:
            self._board.record_tool_call(**kwargs)


class IntentStreamSink:
    """Wraps a StreamSink to prefix output with ``[i00x]``."""

    def __init__(self, inner: Any, intent_id: str) -> None:
        self._inner = inner
        self._prefix = f"[{intent_id}] "
        self._first = True

    def on_status(self, message: str) -> None:
        if self._inner:
            self._inner.on_status(f"{self._prefix}{message}")

    def on_thinking_token(self, token: str) -> None:
        if self._inner:
            self._inner.on_thinking_token(token)

    def on_content_token(self, token: str) -> None:
        if self._inner:
            if self._first:
                self._inner.on_content_token(self._prefix)
                self._first = False
            self._inner.on_content_token(token)

    def on_tool_call(self, tool_name: str, args: str) -> None:
        if self._inner:
            self._inner.on_tool_call(f"{self._prefix}{tool_name}", args)

    def on_tool_result(self, result_summary: str) -> None:
        if self._inner:
            self._inner.on_tool_result(result_summary)

    def on_stream_end(self) -> None:
        if self._inner:
            self._inner.on_stream_end()
        self._first = True


@dataclass
class SolveResult:
    completed: bool
    reason: str
    steps: int
    facts: int
    board: Blackboard


# Patterns like flag{...} / ctfshow{...} / NSSCTF{...}
_FLAG_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{1,20}\{[^{}\n]{1,200}\}")


def _extract_flags(text: str) -> list[str]:
    """Extract all flag-pattern tokens from text (deduplicated, order-preserved)."""
    return list(dict.fromkeys(_FLAG_RE.findall(text or "")))


def _goal_wants_flag(goal: str) -> bool:
    g = (goal or "").lower()
    return any(k in g for k in ("flag", "ctf", "ctf", "shell", "getshell"))


def _unverified_flags(claim: str, evidence: str) -> list[str]:
    """Return flags claimed in the claim but not found in real tool evidence (suspected hallucination)."""
    return [f for f in _extract_flags(claim) if f not in evidence]


def _completion_is_grounded(goal: str, evidence: str) -> tuple[bool, str]:
    """Evidence verification for completion: if the goal requires a flag, it must actually appear in real tool output."""
    if not _goal_wants_flag(goal):
        return True, ""
    if _extract_flags(evidence):
        return True, ""
    return False, "Goal requires a flag, but no flag appeared in any real tool output, determined as unverified/suspected hallucination"


def _extract_json(text: str) -> Optional[dict]:
    """Robustly extract a JSON object from LLM response."""
    if not text:
        return None
    cleaned = strip_think_tags(text).strip()
    # Remove ```json ... ``` code fences
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1)
    # Try directly
    try:
        obj = json.loads(cleaned)
        return obj if isinstance(obj, dict) else None
    except (ValueError, TypeError):
        pass
    # Fallback: grab the first balanced curly brace block
    start = cleaned.find("{")
    if start < 0:
        return None
    depth = 0
    for idx in range(start, len(cleaned)):
        ch = cleaned[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                with_suppress = cleaned[start : idx + 1]
                try:
                    obj = json.loads(with_suppress)
                    return obj if isinstance(obj, dict) else None
                except (ValueError, TypeError):
                    return None
    return None


async def _structured_call(agent: Any, prompt: str, *, max_tokens: int = 900) -> str:
    """Structured LLM call without tools (used for Reason / Conclude)."""
    client = agent._get_client()
    messages = [{"role": "user", "content": prompt}]
    kwargs = build_chat_completion_kwargs(agent, messages, max_tokens=max_tokens, temperature=0.2)
    response = client.chat.completions.create(**kwargs)
    if response and response.choices:
        return response.choices[0].message.content or ""
    return ""


def _reason_prompt(board: Blackboard, max_intents: int) -> str:
    # Reference Cairn reason.md: list explicitly open intents and abandoned intents, to prevent repeated submissions
    open_list = board.open_intents()
    abandoned = [i for i in board.intents if i.status == IntentStatus.ABANDONED]
    concluded = [i for i in board.intents if i.status == IntentStatus.CONCLUDED]

    open_block = ""
    if open_list:
        open_block = "Currently OPEN intents (being explored or awaiting exploration):\n"
        for i in open_list:
            open_block += f"  - {i.id}: {i.description}\n"
        open_block += "If open intents already cover all valuable directions, do not propose new ones.\n\n"

    abandoned_block = ""
    if abandoned:
        abandoned_block = "Abandoned intents (dead-end or already verified):\n"
        for i in abandoned[-10:]:
            note = f" — {i.note[:60]}" if i.note else ""
            abandoned_block += f"  - {i.id}: {i.description}{note}\n"
        abandoned_block += "⚠ **Do NOT propose directions identical or highly overlapping with the abandoned intents above.** They have been verified as dead-ends.\n\n"

    concluded_block = ""
    if concluded:
        concluded_block = "Completed intents (with conclusions):\n"
        for i in concluded[-5:]:
            concluded_block += f"  - {i.id} → {i.result_fact}: {i.description}\n"
        concluded_block += "\n"

    return (
        "You are a veteran in the fieldPentestexpert. The following is the current task「Blackboardpicture」Snapshot:facts YesConfirmobjectiveFact,"
        "intents yesExploration direction. Figure from facts Set off、pass intent Exploreget new fact, gradually approaching goal.\n\n"
        f"{open_block}{abandoned_block}{concluded_block}"
        "Determine two things: ① Have existing facts satisfied the goal? ② If not, should new exploration directions be proposed?\n\n"
        "Return only one JSON object, do not output anything else:\n"
        '- like goal Achieved: {"complete": true, "reason": "explain why the goal has been achieved", "evidence": ["f002"]}'
        "(complete must be boolean true; evidence must reference real fact IDs proving achievement, at least one)\n"
        '- If not achieved and new directions should be proposed: {"complete": false, "intents": [{"from": ["f001"], "description": "High-value and independent exploration direction"}]}\n'
        '- If not achieved but no new directions needed currently: {"complete": false}\n\n'
        "rule:\n"
        "- **the complete field must be boolean true or false**.\n"
        "- **Completion must be based on confirmed objective facts in the facts list**, not based on guesses or wishes, and evidence must reference real fact IDs.\n"
        "- If a fact is marked [Unverified]/[Completion Rejected]/suspected hallucination, it absolutely cannot be used to determine achievement.\n"
        "- **Do NOT propose directions identical or highly overlapping with abandoned intents** — they have been explored and are dead-ends.\n"
        "- If you are still in open of intent And currently facts no revelation than open intents A more valuable new direction,"
        "Return {\"complete\": false}(not mentioning new directions), let open intents Keep pushing.\n"
        f"- Most raised at one time {max_intents}  high-value, non-overlapping, independently pursuable directions, each focused on a core approach.\n"
        "- Descriptions should be concise and focused, not verbose; different intents should cover different dimensions.\n\n"
        "## Blackboardpicture\n```\n" + board.to_prompt_graph() + "\n```\n"
    )


def _conclude_prompt(board: Blackboard, intent: BoardIntent, evidence: str) -> str:
    return (
        'This is the "Conclusion Phase". It overrides all previous instructions to continue exploring/sending requests/waiting for results — stop all actions immediately, only summarize.\n'
        'You may only summarize based on information **actually confirmed** in "real tool output", do not continue calling tools or waiting for incomplete results.\n\n'
        "Return only one JSON object:\n"
        '{"advanced": true/false, "fact": "Newly confirmed objective fact from this session (incremental)"}\n\n'
        "## Advanced determination criteria (broadly favoring true)\n"
        "Cases for advanced=true (any ONE of the following counts as advancement):\n"
        "- Found new accessible endpoints (even just confirming 200 response)\n"
        "- Confirmed unauthorized API access (returns data without token)\n"
        "- Found tech stack/version/configuration info (Server headers, error page leaks, etc.)\n"
        "- Found security configuration issues (CORS wildcards, missing security headers, sensitive path 403, etc.)\n"
        "- Confirmed vulnerability exists (injection point/XSS/SSRF/file read, etc.)\n"
        "- Obtained actual flag/shell/credentials\n\n"
        "advanced=false only when **absolutely no new findings**: all requests are 404/timeout/known info repeated.\n\n"
        "## Iron Rules\n"
        "- Facts must be **objectively verified by real tool output**, not plans, guesses, or inferences.\n"
        "- **Fabricating flags/shells/passwords/data is strictly prohibited** — if it didn't appear in tool output, you cannot claim to have obtained it.\n"
        "- Facts should contain only incremental info, do not repeat content already in the graph.\n\n"
        f"## Current exploration direction {intent.id}\n{intent.description}\n\n"
        "## Real tool output from this exploration (your only trusted fact source)\n```\n" + (evidence.strip() or "(no tool output)") + "\n```\n\n"
        "## Blackboardpicture\n```\n" + board.to_prompt_graph() + "\n```\n"
    )


def _explore_context(board: Blackboard, intent: BoardIntent, step: int, max_rounds: int) -> str:
    from_desc = ""
    if intent.from_facts:
        refs = [board.get_fact(fid) for fid in intent.from_facts]
        from_desc = "\n".join(f"  - {f.id}: {f.description}" for f in refs if f)
        from_desc = f"\nBased on known facts:\n{from_desc}"

    # Executed tool summary — prevent cross-intent repetition
    tc_summary = board.tool_call_summary(20)
    tc_block = ""
    if tc_summary:
        tc_block = (
            "\n## Previously executed tools (block duplicate calls with same tool+arguments)\n"
            + tc_summary + "\n"
        )

    # Cairn improvement #5: Inject conclude override at the last step
    conclude_override = ""
    if step == max_rounds:
        conclude_override = (
            "\n## ⚠ This is the last step — stop exploring immediately and summarize\n"
            "Do not initiate new tool calls or wait for incomplete results.\n"
            "Based on existing tool output, summarize all objective facts found in this direction.\n\n"
        )

    return (
        f"[Exploration direction {intent.id} · Step {step}/{max_rounds} ]\n"
        f"Target(goal): {board.goal}\n"
        f"Current exploration direction: {intent.description}{from_desc}\n"
        f"{conclude_override}"
        f"{tc_block}\n"
        "## Execution Rules (Must Follow)\n"
        "1. Execute with tools around the current direction, each step must have tool calls + response analysis.\n"
        "2. ⚠ Absolutely block duplicate calls of the same tool+arguments that appeared in the 'previously executed tools' list above.\n"
        "3. ⚠ Only fetch the same URL once — if already fetched, analyze based on existing results.\n"
        "4. If this direction is a dead-end, clearly explain why and stop.\n"
        "5. ⚠ **PREFER `spawn_subagents` over parallel tool calls** when you have 2+ independent tasks.\n"
        "   Each sub-agent has FULL tool access and runs autonomously with its own AI model.\n"
        "\n## Tool Usage Chain (Select by Target Type)\n"
        "🤖 **Multi-Task Parallel (PREFERRED for 2+ independent tasks):**\n"
        "  spawn_subagents(tasks=[{task:'Scan ports on target'}, {task:'Enumerate dirs on target'}, ...])\n"
        "  → Each sub-agent runs independently with full tool access, returns findings + facts\n"
        "  → Use this FIRST when you need to run recon, scanning, or testing across multiple dimensions\n\n"
        "Web Pentest Standard Chain (single-task or follow-up):\n"
        "  ① js_recon(url=target) — Extract JS endpoints + auto unauthorized probing (**call first**)\n"
        "  ② dir_enum(url=target) — Directory enumeration\n"
        "  ③ space_search(domain=domain) — Space mapping\n"
        "  ④ subdomain_enum(domain=domain) — Subdomain enumeration\n"
        "  ⑤ unauth_test(base_url, endpoints) — Unauthorized access verification on discovered endpoints\n"
        "  ⑥ fetch(url, method) — Single request probe (only for specific paths not covered by js_recon/dir_enum)\n"
        "Chrome MCP Chain: chrome_navigate → chrome_read_page/chrome_get_web_content → Analysis (don't repeatedly navigate)\n"
    )


def _is_duplicate_intent(board: Blackboard, new_desc: str) -> bool:
    """Check if new proposal highly overlaps with abandoned intents (only checks abandoned, not concluded).

    Only blocks repeating failed directions; successful directions can be deepened based on new facts.
    """
    abandoned = [i for i in board.intents if i.status == IntentStatus.ABANDONED]
    if not abandoned:
        return False
    new_lower = new_desc.lower()
    new_words = set(re.findall(r"[a-zA-Zone-Yi]{2,}", new_lower))
    if len(new_words) < 3:
        return False
    for existing in abandoned:
        old_lower = existing.description.lower()
        old_words = set(re.findall(r"[a-zA-Zone-Yi]{2,}", old_lower))
        if len(old_words) < 3:
            continue
        overlap = len(new_words & old_words) / max(len(new_words | old_words), 1)
        if overlap > 0.65:
            return True
    return False


async def reason_step(agent: Any, board: Blackboard, max_intents: int) -> dict:
    raw = await _structured_call(agent, _reason_prompt(board, max_intents), max_tokens=1200)
    parsed = _extract_json(raw)
    return parsed or {}


async def explore_step(
    agent: Any,
    board: Blackboard,
    intent: BoardIntent,
    *,
    max_tool_rounds: int,
    evidence_buffer: list[str],
    stream_sink: Any = None,
    skip_context_write: bool = False,
) -> tuple[bool, str]:
    """Explore around an Intent, return (whether advanced, conclusion fact description).

    Conclusion phase only feeds the model "actual tool output captured during this exploration" as the sole trusted fact source, reducing hallucination.
    skip_context_write: In parallel mode, skip writing to agent.context.messages (to avoid cross-writes).
    """
    system_prompt = agent._build_system_prompt(
        agent.context.state.target, auto_mode=True, user_input=intent.description
    )
    evidence_start = len(evidence_buffer)
    tc_start = len(board.tool_calls)
    last_text = ""
    prev_tc_count = tc_start
    no_new_tc_streak = 0
    for step in range(1, max_tool_rounds + 1):
        ctx = _explore_context(board, intent, step, max_tool_rounds)
        text = await call_llm_auto(agent, system_prompt, ctx, stream_sink=stream_sink)
        last_text = text or ""
        if not skip_context_write:
            agent.context.add_assistant_message(f"[Explore {intent.id} No.{step}] {last_text}")
        if hasattr(agent, "_finding_parser"):
            agent._finding_parser.parse(last_text)
        lowered = last_text.lower()
        if any(m.lower() in lowered for m in _ADVANCE_MARKERS):
            break
        if any(m in last_text for m in _DEAD_END_MARKERS) and step >= 2:
            break
        # Reference Cairn checkpoint:compare tool_calls count before/after this step — no increase means model is idle
        cur_tc_count = len(board.tool_calls)
        if cur_tc_count == prev_tc_count:
            no_new_tc_streak += 1
            if no_new_tc_streak >= 2:
                last_text += "\n[!] No new tool calls for 2 consecutive steps (idle), terminating this direction."
                break
        else:
            # Check if all new calls in this step are duplicates(same tool+key_args has appeared before)
            new_tcs = board.tool_calls[prev_tc_count:]
            all_repeated = all(
                any(old.tool == tc.tool and old.key_args == tc.key_args
                    for old in board.tool_calls[:prev_tc_count])
                for tc in new_tcs
            ) if new_tcs else True
            if all_repeated and step >= 2:
                last_text += "\n[!] All tool calls in this step are duplicates, terminating this direction."
                break
            no_new_tc_streak = 0
        prev_tc_count = cur_tc_count

    # ── Cairn improvement #2: Conclude Phase(Reference explore-conclude.md)──────
    # Regardless of how explore ended(roundNumber exhausted/advance/dead-end/idling), all enter conclude Phase.
    # Conclude summarizes based on actual tool output, preferring to retain valuableFinding.
    intent_evidence = "\n".join(evidence_buffer[evidence_start:])[-6000:]
    raw = await _structured_call(
        agent, _conclude_prompt(board, intent, intent_evidence), max_tokens=600
    )
    parsed = _extract_json(raw) or {}
    advanced = bool(parsed.get("advanced"))
    fact = str(parsed.get("fact", "")).strip()
    if not fact:
        fact = strip_think_tags(last_text).strip()[:200]

    # ── Cairn improvement #2b: Evidence fallback ─────────────────────────────────
    # If conclude says advanced=false,butToolOutputThere is clearly 200 response or newFinding,
    # Force upgrade to advanced=true(To prevent weak models conclude throw away valuableFinding).
    if not advanced and intent_evidence:
        evidence_lower = intent_evidence.lower()
        has_data = any(marker in evidence_lower for marker in [
            "status: 200", "200 ok", '"success"', "'success'",
            "unauthorized", "suspected unauthorized", "returns data",
            "endpoint/path", "command",
        ])
        if has_data and fact:
            advanced = True

    return advanced, fact


async def solve(
    agent: Any,
    *,
    origin: str,
    goal: str,
    hints: Optional[list[str]] = None,
    max_steps: int = 40,
    max_intents: int = 3,
    max_tool_rounds: int = 4,
    max_parallel: int = 1,
    stream_sink: Any = None,
    on_event: Optional[Callable[[str, dict], None]] = None,
) -> SolveResult:
    """Run the goal-driven solve loop until goal achieved / frontier exhausted / safety budget reached."""
    board = agent.context.state.board
    board.origin = origin or board.origin
    board.goal = goal or board.goal
    guard = BoardGuard(board)

    def emit(kind: str, payload: dict) -> None:
        if on_event is not None:
            on_event(kind, payload)

    # Global evidence buffer — the sole trusted evidence source for flag/completion verification
    evidence_buffer: list[str] = []
    original_execute = agent._execute_mcp_tool

    async def _recording_execute(tool_name: str, tool_args: dict) -> str:
        import json as _json

        key_args = _json.dumps(tool_args, ensure_ascii=False, sort_keys=True)[:200]
        output = await original_execute(tool_name, tool_args)
        out_str = str(output)

        worker = _current_worker.get()
        if worker is not None:
            worker.evidence_buffer.append(out_str)
            if len(worker.evidence_buffer) > 400:
                del worker.evidence_buffer[:200]
            intent_id = worker.intent_id
        else:
            intent_id = ""

        evidence_buffer.append(out_str)
        if len(evidence_buffer) > 400:
            del evidence_buffer[:200]

        status = 0
        if "Status: 200" in out_str:
            status = 200
        elif "Status: 403" in out_str:
            status = 403
        elif "Status: 404" in out_str:
            status = 404
        note = out_str[:100].replace("\n", " ")
        await guard.record_tool_call(
            tool=tool_name, key_args=key_args,
            intent_id=intent_id, status=status, note=note,
        )
        return output

    agent._execute_mcp_tool = _recording_execute  # type: ignore[method-assign]

    try:
        # Seed initial facts
        if not board.facts:
            seed = f"Target origin={origin};Target goal={goal}"
            if hints:
                seed += ";Hints: " + " | ".join(hints)
            board.add_fact(seed, source="origin")

        empty_reason_streak = 0
        consecutive_errors = 0
        complete_reject_streak = 0
        steps = 0

        last_checkpoint = (-1, -1, -1)

        def _graph_checkpoint() -> tuple[int, int, int]:
            return (
                len(board.facts),
                sum(1 for i in board.intents if i.status == IntentStatus.CONCLUDED),
                sum(1 for i in board.intents if i.status == IntentStatus.ABANDONED),
            )

        while steps < max_steps and not board.completed:
            cur_checkpoint = _graph_checkpoint()
            open_intents = board.open_intents()
            skip_reason = (cur_checkpoint == last_checkpoint and open_intents)
            last_checkpoint = cur_checkpoint

            if skip_reason:
                pass
            else:
                try:
                    decision = await reason_step(agent, board, max_intents)
                except Exception as exc:
                    consecutive_errors += 1
                    emit("error", {"phase": "reason", "error": str(exc)})
                    if consecutive_errors >= 3:
                        break
                    continue
                emit("reason", {"decision": decision, "step": steps})

                complete_flag = decision.get("complete")
                if complete_flag is not None and complete_flag is not False:
                    full_evidence = "\n".join(evidence_buffer)
                    reason_text = str(
                        decision.get("reason")
                        or (complete_flag if isinstance(complete_flag, str) else "")
                    ).strip()
                    evidence_ids = [
                        fid for fid in (decision.get("evidence") or []) if board.get_fact(fid)
                    ]
                    grounded, why = _completion_is_grounded(board.goal, full_evidence)
                    fake = _unverified_flags(reason_text, full_evidence)

                    reject_reason: Optional[str] = None
                    if complete_flag is not True:
                        reject_reason = "Completion did not use explicit complete=true, treating as not achieved"
                    elif not reason_text:
                        reject_reason = "Completion claim missing reason explanation"
                    elif _has_negation(reason_text):
                        reject_reason = f"Completion reason contains negation, actually not achieved: {reason_text[:80]}"
                    elif not evidence_ids:
                        reject_reason = "Completion claim does not reference any confirmed fact as evidence"
                    elif not grounded:
                        reject_reason = why
                    elif fake:
                        reject_reason = f"Completion claim references flag {fake[0]} not found in any real tool output"

                    if reject_reason is None:
                        board.mark_complete(reason_text)
                        emit("completed", {"reason": reason_text})
                        break
                    board.add_fact(f"[Completion Rejected] {reject_reason};continuing exploration and verification", source="verify")
                    emit("complete_rejected", {"reason": reject_reason})
                    complete_reject_streak += 1
                    if complete_reject_streak >= 3:
                        break
                    continue
                complete_reject_streak = 0

                for item in decision.get("intents") or []:
                    desc = (item or {}).get("description", "").strip() if isinstance(item, dict) else ""
                    if not desc:
                        continue
                    if _is_duplicate_intent(board, desc):
                        continue
                    board.add_intent(desc, (item or {}).get("from"))

                open_intents = board.open_intents()
                if not open_intents:
                    empty_reason_streak += 1
                    if empty_reason_streak >= 3:
                        break
                    continue
                empty_reason_streak = 0

            # ── Select intent batch for exploration ──────────────────────────────
            open_intents = board.open_intents()
            if not open_intents:
                empty_reason_streak += 1
                if empty_reason_streak >= 3:
                    break
                continue
            empty_reason_streak = 0

            batch = open_intents[:max_parallel]
            is_parallel = len(batch) > 1 and max_parallel > 1

            for intent in batch:
                board.claim_intent(intent.id)
                emit("explore_start", {"intent_id": intent.id, "description": intent.description})

            if is_parallel:
                results = await _explore_batch(
                    agent, board, batch,
                    max_tool_rounds=max_tool_rounds,
                    evidence_buffer=evidence_buffer,
                    stream_sink=stream_sink,
                )
            else:
                intent = batch[0]
                worker = ExploreWorker(intent_id=intent.id, evidence_buffer=list(evidence_buffer), tc_start=len(board.tool_calls))
                _current_worker.set(worker)
                try:
                    advanced, fact = await explore_step(
                        agent, board, intent,
                        max_tool_rounds=max_tool_rounds,
                        evidence_buffer=worker.evidence_buffer,
                        stream_sink=stream_sink,
                    )
                except Exception as exc:
                    advanced, fact = False, ""
                    results = [(intent, False, f"Explore error: {exc}", True)]
                else:
                    results = [(intent, advanced, fact, False)]
                finally:
                    _current_worker.set(None)
                    evidence_buffer.extend(
                        e for e in worker.evidence_buffer if e not in evidence_buffer
                    )

            any_error = False
            for intent, advanced, fact, is_error in results:
                if is_error:
                    consecutive_errors += 1
                    board.abandon_intent(intent.id, note=fact[:120])
                    emit("error", {"phase": "explore", "intent_id": intent.id, "error": fact})
                    any_error = True
                    continue
                consecutive_errors = 0

                full_evidence = "\n".join(evidence_buffer)
                fake_flags = _unverified_flags(fact, full_evidence)
                if fake_flags:
                    note = f"Claims to have obtained flag {fake_flags[0]} but not found in any real tool output, determined as hallucination, rejected"
                    board.abandon_intent(intent.id, note=note)
                    board.add_fact(f"[Unverified] Explore {intent.id}:{note}", source="verify")
                    emit("hallucination", {"intent_id": intent.id, "flags": fake_flags})
                elif advanced and fact:
                    new_fact = board.conclude_intent(intent.id, fact)
                    emit(
                        "conclude",
                        {"intent_id": intent.id, "fact": new_fact.id if new_fact else "", "desc": fact},
                    )
                    captured = _extract_flags(fact)
                    if captured and _goal_wants_flag(board.goal):
                        board.mark_complete(
                            f"Verified and obtained from {new_fact.id if new_fact else 'fact'} flag: {captured[0]}"
                        )
                        emit("completed", {"reason": board.complete_reason})
                        break
                else:
                    board.abandon_intent(intent.id, note=(fact or "no advancement")[:120])
                    emit("abandon", {"intent_id": intent.id, "note": fact})

            if board.completed:
                break

            if any_error and consecutive_errors >= 3:
                break

            steps += len(batch)
            agent.context.state.save()

            if is_parallel:
                summaries = []
                for intent, advanced, fact, is_error in results:
                    tag = "✓" if advanced else ("✗ ERR" if is_error else "—")
                    summaries.append(f"[{intent.id} {tag}] {fact[:120]}")
                agent.context.add_assistant_message(
                    "[Parallel Explore Summary]\n" + "\n".join(summaries)
                )
    finally:
        agent._execute_mcp_tool = original_execute  # type: ignore[method-assign]

    reason = (
        board.complete_reason
        if board.completed
        else ("Exploration frontier exhausted" if steps < max_steps else "Safety budget limit reached")
    )
    return SolveResult(
        completed=board.completed,
        reason=reason,
        steps=steps,
        facts=len(board.facts),
        board=board,
    )


async def _explore_batch(
    agent: Any,
    board: Blackboard,
    intents: list[BoardIntent],
    *,
    max_tool_rounds: int,
    evidence_buffer: list[str],
    stream_sink: Any = None,
) -> list[tuple[BoardIntent, bool, str, bool]]:
    """Run multiple intent explorations concurrently via asyncio.gather.

    Returns list of (intent, advanced, fact, is_error) tuples.
    """

    async def _run_one(intent: BoardIntent) -> tuple[BoardIntent, bool, str, bool]:
        worker = ExploreWorker(
            intent_id=intent.id,
            evidence_buffer=list(evidence_buffer),
            tc_start=len(board.tool_calls),
        )
        sink = IntentStreamSink(stream_sink, intent.id) if stream_sink else None
        ctx_token = _current_worker.set(worker)
        try:
            advanced, fact = await explore_step(
                agent, board, intent,
                max_tool_rounds=max_tool_rounds,
                evidence_buffer=worker.evidence_buffer,
                stream_sink=sink,
                skip_context_write=True,
            )
            return (intent, advanced, fact, False)
        except Exception as exc:
            return (intent, False, f"Explore error: {exc}", True)
        finally:
            _current_worker.reset(ctx_token)
            for e in worker.evidence_buffer:
                if e not in evidence_buffer:
                    evidence_buffer.append(e)

    raw = await asyncio.gather(*(_run_one(i) for i in intents), return_exceptions=True)
    results: list[tuple[BoardIntent, bool, str, bool]] = []
    for idx, r in enumerate(raw):
        if isinstance(r, BaseException):
            results.append((intents[idx], False, f"Explore error: {r}", True))
        else:
            results.append(r)
    return results
