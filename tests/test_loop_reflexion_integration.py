import pytest

from bughunter.agent.context import PentestPhase
from bughunter.agent.core import AgentCore
from bughunter.agent.reflexion import FailureCategory
from bughunter.config.schema import BugHunterConfig


def _make_agent(tmp_path, reflexion_enabled=True):
    config = BugHunterConfig()
    config.session.output_dir = tmp_path
    config.session.reflexion_enabled = reflexion_enabled
    config.session.reflexion_max_same_vuln_fails = 2
    config.session.reflexion_max_total_no_progress = 5
    return AgentCore(config)


@pytest.mark.asyncio
async def test_consecutive_same_failures_generate_reflexion_prompt(tmp_path, monkeypatch):
    agent = _make_agent(tmp_path, reflexion_enabled=True)
    captured_contexts = []

    from bughunter.agent import loop_controller

    async def _fake_call_llm_auto(agent_obj, system_prompt, round_context, **kwargs):
        captured_contexts.append(round_context)
        return "Try sqli payload,ConnectionError Request failed."

    monkeypatch.setattr(loop_controller, "call_llm_auto", _fake_call_llm_auto)

    await agent.auto_pentest("Scan example.com 's SQLInjection vulnerability", max_rounds=4)

    assert "🔴 Reflective Takeover" in captured_contexts[3]
    assert "Stop repeating switch on the current attack path payload." in captured_contexts[3]
    assert "Path-switching force command" not in captured_contexts[3]
    assert agent.runtime.same_path_fail_count >= 2


def test_reflexion_disabled_keeps_legacy_same_path_warning(tmp_path):
    agent = _make_agent(tmp_path, reflexion_enabled=False)
    agent.context.state.advance_phase(PentestPhase.VULN_DISCOVERY)
    agent.runtime.same_path_fail_count = 3

    context = agent._build_round_context(5, 5)

    assert "Path-switching force command" in context
    assert "🔴 Reflective Takeover" not in context
    assert agent.runtime.same_path_fail_count == 0
    assert agent.runtime.path_switch_forced is True


def test_reflexion_memory_persists_across_cycles(tmp_path):
    """P2-7: persistent Fail to retain memory across cycles, but reset this cycle stuck Count."""
    agent = _make_agent(tmp_path, reflexion_enabled=True)

    # Cycle 1:Accumulate similar failures
    rx = agent.runtime.reflexion
    for _ in range(2):
        rx.record_attempt(
            path="sqli",
            success=False,
            category=FailureCategory.ENV_CONSTRAINT,
            details="WAF Intercept",
            vuln_type="sqli",
        )
    assert rx.state.consecutive_failures == 2
    assert rx.state.vuln_type_fail_count == 2

    # Cycle 1 End: Write back snapshot
    agent._save_reflexion_snapshot()
    assert agent.context.state.reflexion_snapshot

    # Cycle 2 Boundary: Rebuild runtime And restore memory
    agent._reset_runtime_state(user_input="[Persistent Cycle 2] Continue penetration")
    rx2 = agent.runtime.reflexion

    # Memory retention: failed paths visible
    assert "sqli" in rx2.get_failed_paths()
    # Current cycle stuck Count Reset, Stuck Detection Restart
    assert rx2.state.consecutive_failures == 0
    assert rx2.state.vuln_type_fail_count == 0


def test_reflexion_snapshot_skipped_when_disabled(tmp_path):
    """reflexion_enabled=False Not written during/Do not restore snapshots."""
    agent = _make_agent(tmp_path, reflexion_enabled=False)
    agent.runtime.reflexion.record_attempt(path="sqli", success=False, vuln_type="sqli")
    agent._save_reflexion_snapshot()
    assert agent.context.state.reflexion_snapshot == {}
