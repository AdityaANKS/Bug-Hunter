"""Bug Hunter Agent Core — the main AI agent loop with tool calling."""

from __future__ import annotations

from typing import Any, Callable, Optional

from bughunter.agent.anti_loop import (
    detect_attack_path,
    detect_phase_from_output,
    is_completion_signal,
    is_meaningful_step,
    track_failed_target,
)
from bughunter.agent.builtin_tools import (
    BLOCKED_PATTERNS,
    RESERVED_IP_RANGES,
    build_openai_tools,
    execute_mcp_tool,
    execute_nmap,
    execute_python,
    is_reserved_ip,
    parse_nmap_xml,
    validate_scan_target,
)
from bughunter.agent.context import ContextManager, PentestPhase, SessionState, TaskConstraints
from bughunter.agent.ctf_mode import detect_flag_claim
from bughunter.agent.finding_parser import FindingParser
from bughunter.agent.input_analysis import (
    detect_phase,
    detect_target,
    extract_task_constraints,
    extract_user_vuln_hint,
    get_payload_examples,
)
from bughunter.agent.kb_context import build_kb_context
from bughunter.agent.llm_client import StreamSink, call_llm
from bughunter.agent.loop_controller import auto_pentest as run_auto_pentest
from bughunter.agent.loop_controller import persistent_pentest as run_persistent_pentest
from bughunter.agent.prompt_context import build_round_context, generate_attack_summary
from bughunter.agent.recon_tracker import update_recon_dimension_completion
from bughunter.agent.runtime_state import AgentResult, PersistentCycleResult, RuntimeState
from bughunter.agent.skill_context import get_active_skill_context
from bughunter.agent.system_prompt import build_dynamic_system_prompt
from bughunter.agent.tool_call_manager import safe_parse_tool_args
from bughunter.config.schema import BugHunterConfig
from bughunter.config.settings import make_openai_client
from bughunter.target_state.store import save_target_state

# Optional KB integration — gracefully degrade if KB data is unavailable
try:
    from bughunter.kb.retriever import KnowledgeRetriever, RetrieverStatus
except Exception:
    KnowledgeRetriever = None
    RetrieverStatus = None


class AgentCore:
    """Core AI agent that orchestrates LLM calls and tool execution."""

    def __init__(self, config: BugHunterConfig, mcp_manager: Any = None) -> None:
        self.config = config
        self.mcp_manager = mcp_manager
        self.context = ContextManager()
        self._client = None
        self._last_system_prompt: str = ""  # cached for fallback provider message rebuild
        self.runtime = RuntimeState()
        self._reset_runtime_state()
        # Optional KB retriever — lazily initialized on first use
        self._kb_retriever: Any = None
        self._kb_context_cache: dict[Any, str] = {}
        self._finding_parser = FindingParser(self.context, self.runtime)
        # Sub-agent orchestration manager
        self.sub_agent_manager = self._init_sub_agent_manager()
        self._report_kb_status()

    def _report_kb_status(self) -> None:
        """Print the knowledge-base backend status once at startup.

        If the KB is empty, automatically seeds it with built-in security
        knowledge so the agent always starts with a functional knowledge base.
        """
        if KnowledgeRetriever is None:
            return
        try:
            self._kb_retriever = KnowledgeRetriever()
            status = self._kb_retriever.get_status()
        except Exception:
            return

        # Auto-seed when KB is empty — fixes "no data available" on first run
        if status == RetrieverStatus.DISABLED:
            try:
                from bughunter.kb.store import KnowledgeStore
                from bughunter.kb.updater import seed_knowledge_base

                store = KnowledgeStore()
                seed_knowledge_base(store)
                # Re-initialize retriever with seeded data
                self._kb_retriever = KnowledgeRetriever(store=store)
                status = self._kb_retriever.get_status()
            except Exception:
                pass  # If seeding fails, continue with disabled status

        try:
            from rich.console import Console

            console = Console()
        except Exception:
            return

        if RetrieverStatus is None:
            return
        if status == RetrieverStatus.CHROMADB_ACTIVE:
            console.print("[green]✓ Knowledge base enabled (ChromaDB)[/green]")
        elif status == RetrieverStatus.KEYWORD_FALLBACK:
            console.print(
                "[yellow]⚠ Knowledge base in keyword mode "
                "(install chromadb for semantic search: pip install bughunter[kb])[/yellow]"
            )
        else:
            console.print("[red]✗ Knowledge base disabled (no data available)[/red]")

    def _init_sub_agent_manager(self) -> Any:
        """Initialize the sub-agent orchestration manager."""
        try:
            from bughunter.agent.sub_agent import SubAgentManager

            return SubAgentManager(self.config, self.mcp_manager)
        except Exception:
            return None

    def _maybe_auto_save_session(self) -> None:
        """Persist session state when auto-save is enabled."""
        if self.config.session.auto_save:
            session_path = self.context.state.save()
            if self.context.state.target:
                save_target_state(
                    self.context.state.target,
                    self.context.state,
                    command="auto",
                    session_file=str(session_path),
                    runtime=self.runtime,
                )

    @property
    def session_state(self) -> SessionState:
        """Access current session state."""
        return self.context.state

    def reset_context(self) -> None:
        """Reset agent context and runtime loop state."""
        self.context.reset()
        self._reset_runtime_state()

    def _reset_runtime_state(
        self,
        user_input: str = "",
        detected_phase: Optional[PentestPhase] = None,
    ) -> None:
        """Reset per-run runtime state to avoid cross-run contamination."""
        user_lower = user_input.lower() if user_input else ""
        existing_constraints = self.context.state.task_constraints
        parsed_constraints = (
            extract_task_constraints(user_input)
            if user_input
            else self.context.state.task_constraints
        )
        if (
            user_input
            and "[Persistent Cycle " in user_input
            and parsed_constraints.allowed_ports == []
            and parsed_constraints.blocked_ports == []
            and parsed_constraints.allowed_actions == []
            and parsed_constraints.blocked_actions == []
            and parsed_constraints.allowed_paths == []
            and parsed_constraints.blocked_paths == []
        ):
            parsed_constraints = existing_constraints
        elif parsed_constraints.is_empty():
            parsed_constraints = self.context.state.task_constraints
        self.runtime = RuntimeState(
            auto_skill_input=user_input,
            user_vuln_hint=self._extract_user_vuln_hint(user_input) if user_input else "",
            task_constraints=parsed_constraints,
            is_recon_phase=detected_phase == PentestPhase.RECON,
            is_ctf_mode=any(
                kw in user_lower for kw in ["ctf", "flag", "ctf", "solve challenge", "find flag", "find the flag"]
            ),
        )
        self.runtime.user_vuln_hint_rounds = 3 if self.runtime.user_vuln_hint else 0
        self.context.state.task_constraints = self.runtime.task_constraints
        if self.mcp_manager and hasattr(self.mcp_manager, "set_task_constraints"):
            self.mcp_manager.set_task_constraints(self.context.state.task_constraints)

        self.context.state.recon_dimensions_completed = {
            "server": False,
            "website": False,
            "domain": False,
            "personnel": False,
        }
        social_engineering_keywords = [
            "social engineering",
            "social eng",
            "personnelInfo",
            "Authortrack",
            "Character tracking",
            "person image",
            "osint",
            "intelligence",
            "Author",
            "investigate",
        ]
        self.context.state.recon_dimension4_active = self.runtime.is_recon_phase and any(
            kw in user_lower for kw in social_engineering_keywords
        )
        # Re-bind finding parser to the new runtime object
        self._finding_parser = FindingParser(self.context, self.runtime)

        # acrosscyclerecoverReflectionmemory(persistent mode): reservedFailedPath/history/attribution, resetcycle stuck count
        self._restore_reflexion_history()

    # ── Reflexion acrosscycleEndurance ───────────────────────────────────────
    _REFLEXION_ATTEMPT_MEMORY = 50  # acrosscycleMost carried attempt Number of items, limited memory and attribution overhead

    def _restore_reflexion_history(self) -> None:
        """from SessionState Snapshot recoveryReflectionmemory section, but resets everycycle stuck count."""
        if not getattr(self.config.session, "reflexion_enabled", True):
            return
        snapshot = getattr(self.context.state, "reflexion_snapshot", None)
        reflexion = getattr(self.runtime, "reflexion", None)
        if not snapshot or reflexion is None:
            return
        try:
            from bughunter.agent.reflexion import ReflexionState

            restored = ReflexionState.model_validate(snapshot)
        except Exception:
            return
        # memory:FailedPath / Attribution material / recently attempts / Known obstacles
        reflexion.state.failed_paths = restored.failed_paths
        reflexion.state.constraints = restored.constraints
        reflexion.state.attempts = restored.attempts[-self._REFLEXION_ATTEMPT_MEMORY :]
        reflexion.state.last_vuln_type = restored.last_vuln_type
        # EverycycleReset: Loser Counter / similarFailedcount / Upgrade the driver (reflections)
        reflexion.state.consecutive_failures = 0
        reflexion.state.vuln_type_fail_count = 0
        reflexion.state.reflections = []

    def _save_reflexion_snapshot(self) -> None:
        """put the currentReflectionStatuswrite back SessionState Snapshot for nextcycle/sameTargetReuse during recovery."""
        if not getattr(self.config.session, "reflexion_enabled", True):
            return
        reflexion = getattr(self.runtime, "reflexion", None)
        if reflexion is None:
            return
        try:
            self.context.state.reflexion_snapshot = reflexion.state.model_dump(mode="json")
        except Exception:
            pass

    def _get_client(self):
        """Lazy-initialize OpenAI client."""
        if self._client is None:
            try:
                self._client = make_openai_client(
                    api_key=self.config.llm.api_key,
                    base_url=self.config.llm.base_url,
                )
            except ImportError:
                raise RuntimeError("Please install the openai package: pip install openai")
        return self._client

    @staticmethod
    def _extract_response(message: Any) -> str:
        """Compatibility wrapper for old tests and call sites."""
        from bughunter.agent.llm_client import extract_response

        return extract_response(message)

    def _build_system_prompt(
        self,
        target: Optional[str] = None,
        auto_mode: bool = False,
        user_input: Optional[str] = None,
    ) -> str:
        """Build the dynamic system prompt for this turn."""
        # Collect MCP tools if available
        mcp_tools = []
        if self.mcp_manager:
            mcp_tools = self.mcp_manager.get_tool_schemas()

        # Collect skill context — dynamically dispatch based on user input
        skill_context = self._get_active_skill_context(user_input=user_input)

        phase = (
            self.context.state.phase.value
            if self.context.state.phase != PentestPhase.IDLE
            else None
        )
        personnel_keywords = [
            "social engineering",
            "social eng",
            "personnelInfo",
            "Authortrack",
            "Character tracking",
            "person image",
            "osint",
            "intelligence",
            "investigate",
            "Author",
        ]
        enable_personnel = any(kw in (user_input or "").lower() for kw in personnel_keywords)
        if (
            hasattr(self.context.state, "recon_dimension4_active")
            and self.context.state.recon_dimension4_active
        ):
            enable_personnel = True

        kb_context = self._build_kb_context(user_input)

        prompt = build_dynamic_system_prompt(
            target=target or self.context.state.target,
            phase=phase,
            skill_context=skill_context,
            mcp_tools=mcp_tools,
            enable_personnel_dim=enable_personnel,
            auto_mode=auto_mode,
            user_input=user_input,
            kb_context=kb_context,
        )
        # Cache for fallback provider message rebuild
        self._last_system_prompt = prompt
        return prompt

    def _get_active_skill_context(self, user_input: Optional[str] = None) -> Optional[str]:
        return get_active_skill_context(user_input)

    def _build_kb_context(self, user_input: Optional[str] = None) -> str:
        return build_kb_context(self, user_input)

    def _detect_phase(self, user_input: str) -> Optional[PentestPhase]:
        """Detect pentest phase from user input using keyword matching."""
        return detect_phase(user_input)

    def _extract_user_vuln_hint(self, user_input: str) -> str:
        """Extract explicit vulnerability hints from user input.

        When the user says "There is this pointSQLinjection,test this" or "Test it for meXSS",
        returns a directive telling LLM to test that specific vuln immediately.
        Returns "" if no explicit hint found.
        """
        return extract_user_vuln_hint(user_input)

    @staticmethod
    def _get_payload_examples(found_vulns: list[str], target: str) -> str:
        """Return concrete PoC payload examples for the given vulnerability types."""
        return get_payload_examples(found_vulns, target)

    def _detect_target(self, user_input: str) -> Optional[str]:
        """Extract target from user input."""
        return detect_target(user_input)

    # ── Single-turn chat (for manual REPL interaction) ──────────────

    async def chat(
        self,
        user_input: str,
        target: Optional[str] = None,
        *,
        stream_sink: Optional["StreamSink"] = None,
    ) -> AgentResult:
        """Process a user message and return agent response (single turn).

        For multi-step tasks with targets, use auto_pentest() instead.
        Chat mode is for quick Q&A and simple single-step queries.
        """
        result = AgentResult()

        # Chat mode is free-form — don't inherit constraints from previous sessions
        self.context.state.task_constraints = TaskConstraints()

        # Detect target and phase from input
        detected_target = target or self._detect_target(user_input)
        detected_phase = self._detect_phase(user_input)

        # Update session state
        if detected_target:
            self.context.state.target = detected_target
            result.target = detected_target

        if detected_phase:
            self.context.state.advance_phase(detected_phase)
            result.phase = detected_phase.value

        # Add user message to context
        self.context.add_user_message(user_input)

        # Build system prompt — pass user_input for dynamic Skill dispatch
        system_prompt = self._build_system_prompt(
            detected_target, auto_mode=False, user_input=user_input
        )

        # Call LLM
        try:
            response_text = await call_llm(self, system_prompt, stream_sink=stream_sink)
            result.output = response_text

            # Add assistant response to context
            self.context.add_assistant_message(response_text)

            # Parse any structured findings from the response
            self._finding_parser.parse(response_text)

            # Auto-save session when enabled
            self._maybe_auto_save_session()

        except Exception as e:
            result.output = f"[!] Agent Error: {e}"

        return result

    # ── Autonomous pentest loop ─────────────────────────────────────

    async def auto_pentest(
        self,
        user_input: str,
        target: Optional[str] = None,
        max_rounds: int = 15,
        on_step: Optional[Callable[[int, AgentResult], None]] = None,
        *,
        stream_sink: Optional["StreamSink"] = None,
    ) -> list[AgentResult]:
        """Autonomous penetration test loop."""
        return await run_auto_pentest(self, user_input, target, max_rounds, on_step, stream_sink=stream_sink)

    def _build_round_context(self, round_num: int, max_rounds: int) -> str:
        """Build context string for the current round in auto loop."""
        return build_round_context(self, round_num, max_rounds)

    # ── TargetdriveSolvecycle(Blackboardpicture OODA, no fixedroundnumber)──────────────────

    async def solve(
        self,
        user_input: str,
        target: Optional[str] = None,
        *,
        goal: Optional[str] = None,
        max_steps: int = 40,
        max_intents: int = 3,
        max_tool_rounds: int = 4,
        stream_sink: Optional["StreamSink"] = None,
        on_event: Optional[Callable[[str, dict], None]] = None,
        time_budget_minutes: int = 0,
    ) -> Any:
        """by「Goal achieved / Exploration frontier exhausted / Safety budget」as a termination conditionSolve, rather than fixedroundnumber."""
        from bughunter.agent.solver import solve as run_solve

        detected_target = target or self._detect_target(user_input)
        if detected_target:
            self.context.state.target = detected_target
        self._reset_runtime_state(user_input=user_input)
        self.context.add_user_message(user_input)

        # Set up scan budget if configured
        budget_minutes = time_budget_minutes or getattr(
            getattr(self.config, "session", None), "scan_time_budget", 0
        )
        if budget_minutes > 0:
            from bughunter.agent.scan_budget import ScanBudget
            scan_budget = ScanBudget(
                total_minutes=budget_minutes,
                tool_timeout_quick=getattr(self.config.session, "scan_tool_timeout_quick", 30),
                tool_timeout_standard=getattr(self.config.session, "scan_tool_timeout_standard", 120),
                tool_timeout_deep=getattr(self.config.session, "scan_tool_timeout_deep", 180),
            )
            scan_budget.start()
            self.runtime.scan_budget = scan_budget

        resolved_goal = goal or user_input
        origin = detected_target or self.context.state.target or user_input
        max_parallel = getattr(self.config.session, "solve_max_parallel", 1)
        return await run_solve(
            self,
            origin=origin,
            goal=resolved_goal,
            max_steps=max_steps,
            max_intents=max_intents,
            max_tool_rounds=max_tool_rounds,
            max_parallel=max_parallel,
            stream_sink=stream_sink,
            on_event=on_event,
        )

    # ── Persistent pentest loop ──────────────────────────────────────

    async def persistent_pentest(
        self,
        user_input: str,
        target: Optional[str] = None,
        rounds_per_cycle: int = 100,
        max_cycles: int = 10,
        auto_report: bool = True,
        on_cycle_step: Optional[Callable[[int, int, AgentResult], None]] = None,
        on_cycle_complete: Optional[Callable[[int, "PersistentCycleResult"], None]] = None,
        *,
        # stream_sink Depend on main.py Incoming, transparently transmitted to call_llm_auto_stream Implement streamingOutput
        stream_sink: Optional["StreamSink"] = None,
    ) -> list["PersistentCycleResult"]:
        """Persistent penetration test — runs cycles of auto_pentest until stopped."""
        return await run_persistent_pentest(
            self,
            user_input,
            target,
            rounds_per_cycle,
            max_cycles,
            auto_report,
            on_cycle_step,
            on_cycle_complete,
            stream_sink=stream_sink,
        )

    def _detect_phase_from_output(self, output: str) -> Optional[PentestPhase]:
        """Detect phase transition signals from LLM output."""
        return detect_phase_from_output(output)

    def _is_completion_signal(self, output: str) -> bool:
        """Check if the LLM output signals task completion."""
        return is_completion_signal(output)

    def _detect_flag_claim(self, output: str) -> Optional[str]:
        """Detect if the LLM claims to have found a flag, return the claimed flag or None.

        This is used to trigger automatic verification — if the LLM claims
        a flag but we can't verify it independently, we should NOT stop.
        """
        return detect_flag_claim(output)

    def _track_failed_target(self, response_text: str) -> Optional[str]:
        """Track target-level failures and detect repeatedly failed targets.

        Returns the hostname of a blocked target if one is detected, else None.
        """
        return track_failed_target(self, response_text)

    def _is_meaningful_step(self, step: str) -> bool:
        """Check if a step represents meaningful progress (not just a failed retry).

        Only steps with actual discoveries or confirmations count as progress.
        A step is considered NOT meaningful only when it is a PURE failure —
        i.e., it mentions failure indicators AND has no progress indicators at all.
        If a step has BOTH failure and progress keywords (e.g. "XSStestTimeoutbutFindingnewPath"),
        it is still meaningful because progress was made.
        """
        return is_meaningful_step(step)

    def _detect_attack_path(self, output: str) -> Optional[str]:
        """Detect the current attack path/technique from LLM output.

        Returns a canonical path name like "regex_bypass", "rce", "file_inclusion", etc.
        Used to track whether the agent is stuck on the same approach.
        """
        return detect_attack_path(output)

    async def _generate_attack_summary(self) -> str:
        """Generate a detailed attack path summary for the cycle report.

        Provides all execution steps, notes, and findings to the LLM and asks
        for a detailed narrative of the attack chain with specific URLs/techniques.
        """
        return await generate_attack_summary(self)

    @staticmethod
    def _safe_parse_tool_args(arguments: Optional[str]) -> dict:
        """Safely parse tool call arguments JSON, with fallback for malformed input."""
        return safe_parse_tool_args(arguments)

    async def _execute_mcp_tool(self, tool_name: str, args: dict) -> str:
        """Execute a tool call via MCP manager or built-in tools."""
        return await execute_mcp_tool(self, tool_name, args)

    def _build_openai_tools(self) -> list[dict]:
        """Build OpenAI function calling schema from MCP tools + built-in tools."""
        return build_openai_tools(self.mcp_manager)

    # ── Python code executor ─────────────────────────────────────────

    _BLOCKED_PATTERNS = BLOCKED_PATTERNS

    async def _execute_nmap(self, args: dict) -> str:
        return await execute_nmap(self, args)

    # ── Reserved IP detection helpers ─────────────────────────────────

    _RESERVED_IP_RANGES = RESERVED_IP_RANGES

    def _is_reserved_ip(self, ip: str) -> tuple[bool, str]:
        return is_reserved_ip(ip)

    def _validate_scan_target(self, target: str) -> str:
        return validate_scan_target(target)

    def _parse_nmap_xml(self, xml_output: str, target: str) -> str:
        return parse_nmap_xml(xml_output, target)

    async def _execute_python(self, args: dict) -> str:
        return await execute_python(self, args)

    def _update_recon_dimension_completion(self, response: str) -> None:
        """Auto-detect which recon dimensions have been explored."""
        update_recon_dimension_completion(self, response)
