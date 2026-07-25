"""Multi-model sub-agent orchestration for BugHunter.

The main AI agent can dynamically spawn sub-agents — each backed by a different
LLM from the model pool — that execute tasks in parallel with full tool access
(Kali sandbox, MCP, built-in tools) and report results back for consolidation.

Sub-agents are short-lived: assigned a task, run a solve loop, return results, die.
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Optional

from bughunter.config.schema import BugHunterConfig, ModelPoolEntry


# ── Data structures ─────────────────────────────────────────────────


@dataclass
class SubAgentConfig:
    """Defines a sub-agent's identity and assigned task."""

    agent_id: str  # e.g. "sub-001"
    model_name: str  # human-readable, from ModelPoolEntry.name
    model: str  # model ID, e.g. "deepseek-ai/deepseek-v4-pro"
    base_url: str
    api_key: str
    task: str  # the goal assigned by the main agent


@dataclass
class SubAgentResult:
    """What a sub-agent returns after completing its task."""

    agent_id: str = ""
    model_name: str = ""
    task: str = ""
    output: str = ""
    findings: list[Any] = field(default_factory=list)
    facts: list[str] = field(default_factory=list)
    tool_calls_count: int = 0
    duration_seconds: float = 0.0
    success: bool = False
    error: str = ""


# ── Stream sink wrapper ─────────────────────────────────────────────


class SubAgentStreamSink:
    """Wraps a parent StreamSink to prefix output with [sub-XXX ModelName].

    Uses an asyncio.Lock to serialize output from concurrent sub-agents,
    preventing interleaved terminal output.
    """

    _output_lock = asyncio.Lock()

    def __init__(self, inner: Any, agent_id: str, model_name: str) -> None:
        self._inner = inner
        self._prefix = f"[{agent_id} {model_name}] "
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
                self._inner.on_content_token(f"\n{self._prefix}")
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


# ── SubAgent ─────────────────────────────────────────────────────────


class SubAgent:
    """A lightweight agent instance backed by a specific LLM model.

    Creates a cloned BugHunterConfig with the sub-agent's model/base_url/api_key
    overriding config.llm, then instantiates its own AgentCore. Shares the parent's
    MCP manager (and thus Kali sandbox) but gets isolated context and blackboard.
    """

    def __init__(
        self,
        sub_config: SubAgentConfig,
        parent_config: BugHunterConfig,
        mcp_manager: Any = None,
        target: str = "",
    ) -> None:
        self.sub_config = sub_config
        self.target = target
        self._mcp_manager = mcp_manager

        # Clone the parent config and override LLM settings
        self._config = self._build_config(parent_config, sub_config)

        # Will be lazily created to avoid import cycles
        self._agent: Any = None

    @staticmethod
    def _build_config(
        parent: BugHunterConfig, sub: SubAgentConfig
    ) -> BugHunterConfig:
        """Clone parent config and override LLM fields for this sub-agent."""
        cloned = parent.model_copy(deep=True)
        cloned.llm.model = sub.model
        cloned.llm.base_url = sub.base_url
        cloned.llm.api_key = sub.api_key
        # Sub-agents don't need fallback providers — they ARE the pool
        cloned.llm.fallback_providers = []
        cloned.llm.model_pool = []
        return cloned

    def _get_agent(self) -> Any:
        """Lazily create the AgentCore to avoid import cycles."""
        if self._agent is None:
            from bughunter.agent.core import AgentCore

            self._agent = AgentCore(self._config, self._mcp_manager)
        return self._agent

    async def execute(
        self,
        stream_sink: Any = None,
        max_steps: int = 25,
        max_tool_rounds: int = 10,
    ) -> SubAgentResult:
        """Execute the assigned task via a solve loop.

        Returns a SubAgentResult with all findings, facts, and output.
        """
        result = SubAgentResult(
            agent_id=self.sub_config.agent_id,
            model_name=self.sub_config.model_name,
            task=self.sub_config.task,
        )
        start_time = time.monotonic()

        try:
            agent = self._get_agent()
            sink = (
                SubAgentStreamSink(
                    stream_sink,
                    self.sub_config.agent_id,
                    self.sub_config.model_name,
                )
                if stream_sink
                else None
            )

            # Run the solve loop
            solve_result = await agent.solve(
                self.sub_config.task,
                target=self.target,
                max_steps=max_steps,
                max_intents=3,
                max_tool_rounds=max_tool_rounds,
                stream_sink=sink,
            )

            # Extract results
            result.success = getattr(solve_result, "completed", False)
            result.output = getattr(solve_result, "reason", "")

            # Collect facts from the sub-agent's blackboard
            board = getattr(
                getattr(agent.context, "state", None), "board", None
            )
            if board is not None:
                result.facts = [f.description for f in board.facts]
                result.tool_calls_count = len(board.tool_calls)

            # Collect findings
            findings = getattr(
                getattr(agent.context, "state", None), "findings", []
            )
            result.findings = list(findings)

        except asyncio.CancelledError:
            result.error = "Sub-agent cancelled"
            result.success = False
        except Exception as exc:
            result.error = str(exc)
            result.success = False
            print(
                f"[!] Sub-agent {self.sub_config.agent_id} error: {exc}",
                file=sys.stderr,
                flush=True,
            )

        result.duration_seconds = time.monotonic() - start_time
        return result


# ── SubAgentManager ──────────────────────────────────────────────────


class SubAgentManager:
    """Orchestration layer: spawns, tracks, and collects results from sub-agents.

    Used by the main AgentCore to dispatch parallel tasks to different AI models.
    """

    def __init__(
        self,
        config: BugHunterConfig,
        mcp_manager: Any = None,
    ) -> None:
        self._config = config
        self._mcp_manager = mcp_manager
        self._seq = 0  # auto-increment for agent IDs
        self._active: dict[str, SubAgent] = {}
        self._completed: list[SubAgentResult] = []
        self._target: str = ""

    def set_target(self, target: str) -> None:
        """Set the current scan target for sub-agents to inherit."""
        self._target = target

    def available_models(self) -> list[ModelPoolEntry]:
        """Return enabled pool entries that have valid API keys.

        If model_pool is empty, auto-populates from the primary model and
        fallback providers so sub-agents work out-of-the-box.
        """
        pool = list(self._config.llm.model_pool)

        # Auto-populate from primary + fallback when no explicit pool configured
        if not pool:
            pool = self._auto_populate_pool()

        models = []
        for entry in pool:
            if not entry.enabled:
                continue
            api_key = ""
            if entry.api_key_env:
                api_key = os.environ.get(entry.api_key_env, "")
            elif entry.base_url == self._config.llm.base_url:
                # Primary model — use primary api_key directly
                api_key = self._config.llm.api_key
            if not api_key:
                # Try direct key from fallback config match
                for fb in self._config.llm.fallback_providers:
                    if fb.base_url == entry.base_url:
                        api_key = fb.api_key
                        break
            if not api_key:
                continue
            models.append(entry)
        # Sort by tier (lower tier = higher priority)
        models.sort(key=lambda m: m.tier)
        return models

    def _auto_populate_pool(self) -> list[ModelPoolEntry]:
        """Create pool entries from primary model + fallback providers."""
        entries: list[ModelPoolEntry] = []
        llm = self._config.llm

        # Add primary model
        entries.append(ModelPoolEntry(
            name=f"Primary ({llm.provider})",
            provider=llm.provider,
            model=llm.model,
            role="primary",
            tier=1,
            enabled=True,
            api_key_env="",
            base_url=llm.base_url,
        ))

        # Add fallback providers
        for idx, fb in enumerate(llm.fallback_providers):
            if not fb.api_key and not fb.api_keys:
                continue
            model = fb.model or llm.model
            entries.append(ModelPoolEntry(
                name=f"Fallback-{idx+1} ({fb.name})",
                provider=fb.name,
                model=model,
                role="fallback",
                tier=2 + idx,
                enabled=True,
                api_key_env="",
                base_url=fb.base_url,
            ))

        return entries

    def _resolve_api_key(self, entry: ModelPoolEntry) -> str:
        """Resolve the API key for a pool entry.

        Checks in order: api_key_env, primary LLM key (by base_url match),
        fallback provider keys (by base_url match).
        """
        # 1. Explicit env var
        if entry.api_key_env:
            key = os.environ.get(entry.api_key_env, "")
            if key:
                return key

        # 2. Primary model match
        if entry.base_url == self._config.llm.base_url:
            return self._config.llm.api_key

        # 3. Fallback provider match
        for fb in self._config.llm.fallback_providers:
            if fb.base_url == entry.base_url:
                if fb.api_key:
                    return fb.api_key
                if fb.api_keys:
                    return fb.api_keys[0]

        return ""

    def _next_id(self) -> str:
        """Generate the next sub-agent ID."""
        self._seq += 1
        return f"sub-{self._seq:03d}"

    def _resolve_model(
        self, model_hint: str, available: list[ModelPoolEntry], idx: int
    ) -> Optional[ModelPoolEntry]:
        """Resolve a model hint to a pool entry, or round-robin if no hint."""
        if model_hint:
            hint_lower = model_hint.lower()
            for entry in available:
                if (
                    hint_lower in entry.name.lower()
                    or hint_lower in entry.model.lower()
                    or hint_lower == entry.provider.lower()
                ):
                    return entry
        # Round-robin assignment
        if available:
            return available[idx % len(available)]
        return None

    def _make_fallback_config(self) -> SubAgentConfig:
        """Create a sub-agent config using the primary model (fallback)."""
        return SubAgentConfig(
            agent_id=self._next_id(),
            model_name="Primary",
            model=self._config.llm.model,
            base_url=self._config.llm.base_url,
            api_key=self._config.llm.api_key,
            task="",
        )

    async def spawn(
        self,
        tasks: list[dict[str, str]],
        stream_sink: Any = None,
    ) -> list[SubAgentResult]:
        """Spawn sub-agents for a batch of tasks and run them concurrently.

        Args:
            tasks: List of dicts with keys:
                - "task" (required): The goal/task description
                - "model_hint" (optional): Model name/provider hint for assignment
            stream_sink: Optional parent stream sink for output

        Returns:
            List of SubAgentResult in the same order as the input tasks.
        """
        max_concurrent = getattr(
            getattr(self._config, "session", None), "max_subagents", 3
        )
        max_steps = getattr(
            getattr(self._config, "session", None), "subagent_max_steps", 25
        )
        max_tool_rounds = getattr(
            getattr(self._config, "session", None),
            "subagent_max_tool_rounds",
            10,
        )

        available = self.available_models()

        # Build sub-agent configs
        sub_agents: list[SubAgent] = []
        for idx, task_spec in enumerate(tasks):
            task_str = task_spec.get("task", "")
            if not task_str:
                continue
            model_hint = task_spec.get("model_hint", "")
            entry = self._resolve_model(model_hint, available, idx)

            if entry is not None:
                api_key = self._resolve_api_key(entry)
                sub_cfg = SubAgentConfig(
                    agent_id=self._next_id(),
                    model_name=entry.name,
                    model=entry.model,
                    base_url=entry.base_url,
                    api_key=api_key,
                    task=task_str,
                )
            else:
                # Fallback to primary model
                sub_cfg = self._make_fallback_config()
                sub_cfg.task = task_str

            agent = SubAgent(
                sub_cfg,
                self._config,
                self._mcp_manager,
                target=self._target,
            )
            sub_agents.append(agent)
            self._active[sub_cfg.agent_id] = agent

        if not sub_agents:
            return []

        # Print spawn summary
        print(
            f"\n[*] Spawning {len(sub_agents)} sub-agent(s) "
            f"(max concurrent: {max_concurrent}):",
            file=sys.stdout,
            flush=True,
        )
        for sa in sub_agents:
            print(
                f"    → {sa.sub_config.agent_id} [{sa.sub_config.model_name}]: "
                f"{sa.sub_config.task[:80]}",
                file=sys.stdout,
                flush=True,
            )

        # Run concurrently with semaphore cap
        semaphore = asyncio.Semaphore(max_concurrent)

        async def _run_one(agent: SubAgent) -> SubAgentResult:
            async with semaphore:
                return await agent.execute(
                    stream_sink=stream_sink,
                    max_steps=max_steps,
                    max_tool_rounds=max_tool_rounds,
                )

        raw_results = await asyncio.gather(
            *(_run_one(sa) for sa in sub_agents),
            return_exceptions=True,
        )

        # Process results
        results: list[SubAgentResult] = []
        for idx, r in enumerate(raw_results):
            sa = sub_agents[idx]
            # Remove from active
            self._active.pop(sa.sub_config.agent_id, None)

            if isinstance(r, BaseException):
                result = SubAgentResult(
                    agent_id=sa.sub_config.agent_id,
                    model_name=sa.sub_config.model_name,
                    task=sa.sub_config.task,
                    error=str(r),
                    success=False,
                )
            else:
                result = r

            self._completed.append(result)
            results.append(result)

        return results

    async def spawn_one(
        self,
        task: str,
        model_hint: str = "",
        stream_sink: Any = None,
    ) -> SubAgentResult:
        """Convenience: spawn a single sub-agent for one task."""
        results = await self.spawn(
            [{"task": task, "model_hint": model_hint}],
            stream_sink=stream_sink,
        )
        return results[0] if results else SubAgentResult(error="No task provided")

    # ── Status / Reporting ───────────────────────────────────────────

    @property
    def active_count(self) -> int:
        return len(self._active)

    @property
    def completed_results(self) -> list[SubAgentResult]:
        return list(self._completed)

    def get_status_summary(self) -> str:
        """Return a formatted summary of all sub-agent activity."""
        lines = []
        if self._active:
            lines.append(f"🔄 Active sub-agents: {len(self._active)}")
            for aid, sa in self._active.items():
                lines.append(
                    f"   {aid} [{sa.sub_config.model_name}]: {sa.sub_config.task[:60]}"
                )
        if self._completed:
            lines.append(f"\n✅ Completed sub-agents: {len(self._completed)}")
            for r in self._completed:
                status = "✓" if r.success else "✗"
                findings_count = len(r.findings)
                lines.append(
                    f"   {r.agent_id} [{r.model_name}] {status} "
                    f"— {r.duration_seconds:.1f}s, "
                    f"{r.tool_calls_count} tools, "
                    f"{findings_count} findings"
                )
                if r.error:
                    lines.append(f"     Error: {r.error[:100]}")
        if not self._active and not self._completed:
            lines.append("No sub-agents have been spawned yet.")
        return "\n".join(lines)

    def format_results_for_agent(
        self, results: list[SubAgentResult]
    ) -> str:
        """Format sub-agent results into a text block for the main agent's context."""
        parts = [f"## Sub-Agent Results ({len(results)} agent(s) completed)\n"]
        for r in results:
            status = "✅ SUCCESS" if r.success else "❌ FAILED"
            parts.append(
                f"### [{r.agent_id}] {r.model_name} — {status} ({r.duration_seconds:.1f}s)\n"
                f"**Task**: {r.task}\n"
                f"**Tools executed**: {r.tool_calls_count}\n"
            )
            if r.error:
                parts.append(f"**Error**: {r.error}\n")
            if r.facts:
                parts.append("**Discovered facts**:")
                for fact in r.facts[-10:]:  # Last 10 facts (most relevant)
                    parts.append(f"  - {fact}")
                parts.append("")
            if r.findings:
                parts.append(f"**Findings**: {len(r.findings)} vulnerability(ies)")
                for finding in r.findings:
                    title = getattr(finding, "title", str(finding))
                    severity = getattr(finding, "severity", "?")
                    parts.append(f"  - [{severity}] {title}")
                parts.append("")
            if r.output:
                output_preview = r.output[:500]
                parts.append(f"**Summary**: {output_preview}\n")
            parts.append("---\n")
        return "\n".join(parts)
