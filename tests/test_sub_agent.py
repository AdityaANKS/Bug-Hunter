"""Tests for the multi-model sub-agent orchestration system."""

from __future__ import annotations

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bughunter.agent.sub_agent import (
    SubAgent,
    SubAgentConfig,
    SubAgentManager,
    SubAgentResult,
    SubAgentStreamSink,
)
from bughunter.config.schema import (
    BugHunterConfig,
    LLMConfig,
    ModelPoolEntry,
    SessionConfig,
)


# ── Fixtures ─────────────────────────────────────────────────────────


def _make_config(**llm_overrides) -> BugHunterConfig:
    """Build a minimal BugHunterConfig for testing."""
    llm_kwargs = {
        "provider": "custom",
        "api_key": "test-key",
        "base_url": "https://test.api/v1",
        "model": "test-primary-model",
    }
    llm_kwargs.update(llm_overrides)
    return BugHunterConfig(
        llm=LLMConfig(**llm_kwargs),
        session=SessionConfig(
            max_subagents=3,
            subagent_max_steps=25,
            subagent_max_tool_rounds=10,
        ),
    )


def _make_pool_entries() -> list[ModelPoolEntry]:
    """Create sample model pool entries for testing."""
    return [
        ModelPoolEntry(
            name="DeepSeek",
            provider="deepseek",
            model="deepseek-v4-pro",
            role="secondary",
            tier=1,
            enabled=True,
            api_key_env="TEST_DEEPSEEK_KEY",
            base_url="https://api.deepseek.com",
        ),
        ModelPoolEntry(
            name="Qwen",
            provider="qwen",
            model="qwen3-max",
            role="fast",
            tier=2,
            enabled=True,
            api_key_env="TEST_QWEN_KEY",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        ),
        ModelPoolEntry(
            name="Disabled",
            provider="custom",
            model="disabled-model",
            role="fallback",
            tier=99,
            enabled=False,
            api_key_env="TEST_DISABLED_KEY",
            base_url="https://disabled.api/v1",
        ),
    ]


def _make_sub_config(agent_id: str = "sub-001", task: str = "test task") -> SubAgentConfig:
    return SubAgentConfig(
        agent_id=agent_id,
        model_name="TestModel",
        model="test-model",
        base_url="https://test.api/v1",
        api_key="test-key",
        task=task,
    )


# ── SubAgentConfig Tests ────────────────────────────────────────────


class TestSubAgentConfig:
    def test_config_creation(self):
        cfg = _make_sub_config()
        assert cfg.agent_id == "sub-001"
        assert cfg.model_name == "TestModel"
        assert cfg.model == "test-model"
        assert cfg.task == "test task"

    def test_config_with_custom_values(self):
        cfg = SubAgentConfig(
            agent_id="sub-042",
            model_name="DeepSeek V4",
            model="deepseek-v4-pro",
            base_url="https://api.deepseek.com",
            api_key="sk-deep",
            task="Scan port 80 for XSS",
        )
        assert cfg.agent_id == "sub-042"
        assert "XSS" in cfg.task


# ── SubAgentResult Tests ────────────────────────────────────────────


class TestSubAgentResult:
    def test_default_result(self):
        r = SubAgentResult()
        assert r.success is False
        assert r.output == ""
        assert r.findings == []
        assert r.facts == []
        assert r.tool_calls_count == 0
        assert r.error == ""

    def test_result_with_findings(self):
        r = SubAgentResult(
            agent_id="sub-001",
            model_name="DeepSeek",
            task="test SQL injection",
            success=True,
            facts=["Found open port 80", "SQL injection on /api/users"],
            tool_calls_count=5,
            duration_seconds=12.5,
        )
        assert r.success is True
        assert len(r.facts) == 2
        assert r.duration_seconds == 12.5


# ── SubAgent Tests ──────────────────────────────────────────────────


class TestSubAgent:
    def test_config_cloning(self):
        """SubAgent should create a cloned config with overridden LLM fields."""
        parent_config = _make_config()
        sub_cfg = _make_sub_config()

        cloned = SubAgent._build_config(parent_config, sub_cfg)

        # LLM fields should be overridden
        assert cloned.llm.model == "test-model"
        assert cloned.llm.base_url == "https://test.api/v1"
        assert cloned.llm.api_key == "test-key"
        # Fallback providers should be empty
        assert cloned.llm.fallback_providers == []
        assert cloned.llm.model_pool == []

    def test_config_preserves_non_llm_settings(self):
        """SubAgent should preserve non-LLM settings from parent."""
        parent_config = _make_config()
        parent_config.session.max_rounds = 42
        sub_cfg = _make_sub_config()

        cloned = SubAgent._build_config(parent_config, sub_cfg)

        assert cloned.session.max_rounds == 42

    def test_config_deep_copy_independence(self):
        """Cloned config changes should not affect parent."""
        parent_config = _make_config()
        sub_cfg = _make_sub_config()

        cloned = SubAgent._build_config(parent_config, sub_cfg)
        cloned.llm.model = "modified-model"

        assert parent_config.llm.model == "test-primary-model"


# ── SubAgentManager Tests ───────────────────────────────────────────


class TestSubAgentManager:
    def test_available_models_filters_disabled(self):
        """available_models should filter out disabled entries."""
        config = _make_config(model_pool=_make_pool_entries())

        # Set env vars for enabled models
        with patch.dict(os.environ, {
            "TEST_DEEPSEEK_KEY": "sk-deep",
            "TEST_QWEN_KEY": "sk-qwen",
            "TEST_DISABLED_KEY": "sk-disabled",
        }):
            mgr = SubAgentManager(config)
            available = mgr.available_models()

        assert len(available) == 2
        names = [m.name for m in available]
        assert "DeepSeek" in names
        assert "Qwen" in names
        assert "Disabled" not in names

    def test_available_models_filters_no_key(self):
        """available_models should filter out entries without API keys."""
        config = _make_config(model_pool=_make_pool_entries())

        # Only set one env var
        with patch.dict(os.environ, {"TEST_DEEPSEEK_KEY": "sk-deep"}, clear=False):
            # Remove the other key if it exists
            env = os.environ.copy()
            env.pop("TEST_QWEN_KEY", None)
            with patch.dict(os.environ, env, clear=True):
                with patch.dict(os.environ, {"TEST_DEEPSEEK_KEY": "sk-deep"}):
                    mgr = SubAgentManager(config)
                    available = mgr.available_models()

        # Only DeepSeek should be available (has env var set)
        deepseek_available = any(m.name == "DeepSeek" for m in available)
        assert deepseek_available

    def test_available_models_sorted_by_tier(self):
        """available_models should return models sorted by tier."""
        config = _make_config(model_pool=_make_pool_entries())

        with patch.dict(os.environ, {
            "TEST_DEEPSEEK_KEY": "sk-deep",
            "TEST_QWEN_KEY": "sk-qwen",
        }):
            mgr = SubAgentManager(config)
            available = mgr.available_models()

        assert available[0].tier <= available[1].tier

    def test_next_id_increments(self):
        mgr = SubAgentManager(_make_config())
        assert mgr._next_id() == "sub-001"
        assert mgr._next_id() == "sub-002"
        assert mgr._next_id() == "sub-003"

    def test_resolve_model_by_name(self):
        pool = _make_pool_entries()[:2]  # Only enabled entries
        mgr = SubAgentManager(_make_config())

        result = mgr._resolve_model("deepseek", pool, 0)
        assert result is not None
        assert result.name == "DeepSeek"

    def test_resolve_model_by_provider(self):
        pool = _make_pool_entries()[:2]
        mgr = SubAgentManager(_make_config())

        result = mgr._resolve_model("qwen", pool, 0)
        assert result is not None
        assert result.name == "Qwen"

    def test_resolve_model_round_robin(self):
        pool = _make_pool_entries()[:2]
        mgr = SubAgentManager(_make_config())

        r0 = mgr._resolve_model("", pool, 0)
        r1 = mgr._resolve_model("", pool, 1)

        assert r0.name != r1.name  # Should alternate

    def test_resolve_model_no_pool(self):
        mgr = SubAgentManager(_make_config())
        result = mgr._resolve_model("", [], 0)
        assert result is None

    def test_fallback_config(self):
        config = _make_config()
        mgr = SubAgentManager(config)
        fb = mgr._make_fallback_config()

        assert fb.model == "test-primary-model"
        assert fb.api_key == "test-key"
        assert fb.agent_id.startswith("sub-")

    def test_status_summary_empty(self):
        mgr = SubAgentManager(_make_config())
        summary = mgr.get_status_summary()
        assert "No sub-agents" in summary

    def test_format_results_for_agent(self):
        mgr = SubAgentManager(_make_config())
        results = [
            SubAgentResult(
                agent_id="sub-001",
                model_name="DeepSeek",
                task="Scan ports",
                success=True,
                facts=["Found port 80 open", "Found port 443 open"],
                tool_calls_count=3,
                duration_seconds=5.2,
            ),
            SubAgentResult(
                agent_id="sub-002",
                model_name="Qwen",
                task="Directory enum",
                success=False,
                error="Timeout",
                tool_calls_count=1,
                duration_seconds=30.0,
            ),
        ]
        formatted = mgr.format_results_for_agent(results)

        assert "sub-001" in formatted
        assert "DeepSeek" in formatted
        assert "SUCCESS" in formatted
        assert "FAILED" in formatted
        assert "Timeout" in formatted


# ── SubAgentStreamSink Tests ────────────────────────────────────────


class TestSubAgentStreamSink:
    def test_prefix_on_status(self):
        inner = MagicMock()
        sink = SubAgentStreamSink(inner, "sub-001", "DeepSeek")
        sink.on_status("Thinking...")

        inner.on_status.assert_called_once()
        call_args = inner.on_status.call_args[0][0]
        assert "[sub-001 DeepSeek]" in call_args
        assert "Thinking..." in call_args

    def test_prefix_on_first_content(self):
        inner = MagicMock()
        sink = SubAgentStreamSink(inner, "sub-002", "Qwen")
        sink.on_content_token("hello")

        # Should emit prefix first, then content
        assert inner.on_content_token.call_count == 2
        first_call = inner.on_content_token.call_args_list[0][0][0]
        assert "[sub-002 Qwen]" in first_call

    def test_prefix_only_on_first_content(self):
        inner = MagicMock()
        sink = SubAgentStreamSink(inner, "sub-001", "Test")
        sink.on_content_token("hello")
        sink.on_content_token("world")

        # Prefix on first call, plain on second
        assert inner.on_content_token.call_count == 3  # prefix + hello + world

    def test_prefix_on_tool_call(self):
        inner = MagicMock()
        sink = SubAgentStreamSink(inner, "sub-001", "DeepSeek")
        sink.on_tool_call("nmap_scan", '{"target": "x"}')

        inner.on_tool_call.assert_called_once()
        call_args = inner.on_tool_call.call_args[0][0]
        assert "[sub-001 DeepSeek]" in call_args

    def test_null_inner(self):
        """Should not raise when inner is None."""
        sink = SubAgentStreamSink(None, "sub-001", "Test")
        sink.on_status("test")
        sink.on_content_token("test")
        sink.on_tool_call("test", "{}")
        sink.on_stream_end()

    def test_stream_end_resets_prefix(self):
        inner = MagicMock()
        sink = SubAgentStreamSink(inner, "sub-001", "Test")
        sink.on_content_token("first")
        sink.on_stream_end()

        # After stream_end, next content should get prefix again
        sink.on_content_token("second")
        # Count: prefix1 + "first" + prefix2 + "second" = 4
        assert inner.on_content_token.call_count == 4


# ── Integration-like Tests (with mocked AgentCore) ──────────────────


class TestSubAgentSpawn:
    @pytest.mark.asyncio
    async def test_spawn_empty_tasks(self):
        mgr = SubAgentManager(_make_config())
        results = await mgr.spawn([])
        assert results == []

    @pytest.mark.asyncio
    async def test_spawn_creates_agents(self):
        config = _make_config(model_pool=_make_pool_entries())

        with patch.dict(os.environ, {
            "TEST_DEEPSEEK_KEY": "sk-deep",
            "TEST_QWEN_KEY": "sk-qwen",
        }):
            mgr = SubAgentManager(config)

            # Mock SubAgent.execute to avoid real LLM calls
            mock_result = SubAgentResult(
                agent_id="sub-001",
                model_name="DeepSeek",
                task="test",
                success=True,
                facts=["Found something"],
                tool_calls_count=2,
                duration_seconds=1.0,
            )

            with patch.object(SubAgent, "execute", return_value=mock_result):
                results = await mgr.spawn([
                    {"task": "Scan port 80"},
                    {"task": "Directory enumeration"},
                ])

            assert len(results) == 2
            assert mgr.active_count == 0  # All completed
            assert len(mgr.completed_results) == 2

    @pytest.mark.asyncio
    async def test_spawn_one_convenience(self):
        mgr = SubAgentManager(_make_config())

        mock_result = SubAgentResult(
            agent_id="sub-001",
            model_name="Primary",
            task="test task",
            success=True,
        )

        with patch.object(SubAgent, "execute", return_value=mock_result):
            result = await mgr.spawn_one("test task")

        assert result.task == "test task"

    @pytest.mark.asyncio
    async def test_spawn_handles_errors(self):
        """One sub-agent error should not crash others."""
        config = _make_config(model_pool=_make_pool_entries())

        with patch.dict(os.environ, {
            "TEST_DEEPSEEK_KEY": "sk-deep",
            "TEST_QWEN_KEY": "sk-qwen",
        }):
            mgr = SubAgentManager(config)

            call_count = 0

            async def _mock_execute(self, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise RuntimeError("LLM connection failed")
                return SubAgentResult(
                    agent_id=self.sub_config.agent_id,
                    model_name=self.sub_config.model_name,
                    task=self.sub_config.task,
                    success=True,
                )

            with patch.object(SubAgent, "execute", _mock_execute):
                results = await mgr.spawn([
                    {"task": "Task that fails"},
                    {"task": "Task that succeeds"},
                ])

            assert len(results) == 2
            # One should have an error
            errors = [r for r in results if r.error]
            successes = [r for r in results if r.success]
            assert len(errors) >= 1

    @pytest.mark.asyncio
    async def test_spawn_with_model_hints(self):
        config = _make_config(model_pool=_make_pool_entries())

        with patch.dict(os.environ, {
            "TEST_DEEPSEEK_KEY": "sk-deep",
            "TEST_QWEN_KEY": "sk-qwen",
        }):
            mgr = SubAgentManager(config)

            created_configs = []
            original_init = SubAgent.__init__

            def _capture_init(self, sub_config, *args, **kwargs):
                created_configs.append(sub_config)
                original_init(self, sub_config, *args, **kwargs)

            mock_result = SubAgentResult(success=True)

            with patch.object(SubAgent, "__init__", _capture_init):
                with patch.object(SubAgent, "execute", return_value=mock_result):
                    await mgr.spawn([
                        {"task": "Use DeepSeek", "model_hint": "deepseek"},
                        {"task": "Use Qwen", "model_hint": "qwen"},
                    ])

            assert len(created_configs) == 2
            assert created_configs[0].model_name == "DeepSeek"
            assert created_configs[1].model_name == "Qwen"

    @pytest.mark.asyncio
    async def test_spawn_fallback_to_primary(self):
        """When no pool models available, should use primary model."""
        config = _make_config()  # No pool entries
        mgr = SubAgentManager(config)

        mock_result = SubAgentResult(success=True, model_name="Primary")

        with patch.object(SubAgent, "execute", return_value=mock_result):
            results = await mgr.spawn([{"task": "Test"}])

        assert len(results) == 1


# ── Config Schema Tests ─────────────────────────────────────────────


class TestSubAgentConfig_Schema:
    def test_default_session_values(self):
        config = BugHunterConfig()
        assert config.session.max_subagents == 3
        assert config.session.subagent_max_steps == 25
        assert config.session.subagent_max_tool_rounds == 10

    def test_custom_session_values(self):
        config = BugHunterConfig(
            session=SessionConfig(
                max_subagents=5,
                subagent_max_steps=50,
                subagent_max_tool_rounds=20,
            )
        )
        assert config.session.max_subagents == 5
        assert config.session.subagent_max_steps == 50
        assert config.session.subagent_max_tool_rounds == 20


# ── Core Integration Tests ──────────────────────────────────────────


class TestCoreIntegration:
    def test_agent_core_has_sub_agent_manager(self):
        """AgentCore should have a sub_agent_manager attribute."""
        from bughunter.agent.core import AgentCore

        config = _make_config()
        agent = AgentCore(config)
        assert hasattr(agent, "sub_agent_manager")
        # Should be a SubAgentManager instance (or None if import failed)
        if agent.sub_agent_manager is not None:
            assert hasattr(agent.sub_agent_manager, "spawn")
            assert hasattr(agent.sub_agent_manager, "available_models")


# ── Tool Schema Tests ───────────────────────────────────────────────


class TestSpawnSubagentsTool:
    def test_tool_schema_present(self):
        """spawn_subagents should appear in the OpenAI tools list."""
        from bughunter.agent.builtin_tools import build_openai_tools

        tools = build_openai_tools(None)
        tool_names = [t["function"]["name"] for t in tools]
        assert "spawn_subagents" in tool_names

    def test_tool_schema_structure(self):
        """spawn_subagents schema should have tasks parameter."""
        from bughunter.agent.builtin_tools import build_openai_tools

        tools = build_openai_tools(None)
        spawn_tool = next(t for t in tools if t["function"]["name"] == "spawn_subagents")
        params = spawn_tool["function"]["parameters"]
        assert "tasks" in params["properties"]
        assert params["properties"]["tasks"]["type"] == "array"
