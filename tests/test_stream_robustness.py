"""Streaming. tool_calls Assemble robustness testing.

Overridden:
- Cross chunk Fragmented tool_calls Assembly (index Alignment、arguments Splicing)
- function name / arguments Respectively in different. chunk Reach
- Contains only id The first shard offunction Field for None)—— provider Differences
- Empty delta / None tc_delta / Missing index The boundary of
- Incomplete tool_call( truncation JSON / Missing id / Missing name) Discarded
- Disconnected midway, has been received content Reserved
- reasoning_content With content No obfuscation
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from bughunter.agent.llm_client import (
    _assemble_tool_calls,
    _collect_tool_call_deltas,
    _validate_tool_call,
    call_llm_auto_stream,
    call_llm_stream,
)

# === Testing assistance mock Type (Simulation OpenAI Streaming. delta Structure) ===


class _Func:
    def __init__(self, name=None, arguments=None):
        self.name = name
        self.arguments = arguments


class _TCDelta:
    """Single tool_call Fragmentation (delta.tool_calls[i])."""

    def __init__(self, index=0, id=None, name=None, arguments=None, function="set"):
        self.index = index
        self.id = id
        # function="none" Simulation only contains id The first shard of (some provider)
        if function == "none":
            self.function = None
        else:
            self.function = _Func(name=name, arguments=arguments)


class _Delta:
    def __init__(self, content=None, reasoning=None, tool_calls=None):
        self.content = content
        self.reasoning_content = reasoning
        self.tool_calls = tool_calls


class _Choice:
    def __init__(self, delta):
        self.delta = delta


class _Chunk:
    def __init__(self, content=None, reasoning=None, tool_calls=None, choices=None):
        if choices is not None:
            self.choices = choices
        else:
            self.choices = [_Choice(_Delta(content=content, reasoning=reasoning, tool_calls=tool_calls))]


class _SyncStream:
    def __init__(self, chunks):
        self._chunks = chunks

    def __iter__(self):
        return iter(self._chunks)


class _BreakingStream:
    """First produce several chunk, then throw an exception to simulate disconnection midway."""

    def __init__(self, chunks, exc):
        self._chunks = list(chunks)
        self._exc = exc

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._chunks:
            return self._chunks.pop(0)
        raise self._exc


class SpySink:
    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    def on_status(self, message):
        self.calls.append(("status", message))

    def on_thinking_token(self, token):
        self.calls.append(("thinking", token))

    def on_content_token(self, token):
        self.calls.append(("content", token))

    def on_tool_call(self, tool_name, args):
        self.calls.append(("tool_call", f"{tool_name}:{args}"))

    def on_tool_result(self, result_summary):
        self.calls.append(("tool_result", result_summary))

    def on_stream_end(self):
        self.calls.append(("end", ""))


def _make_agent():
    agent = MagicMock()
    mock_client = MagicMock()
    agent._get_client.return_value = mock_client
    agent.config.llm.provider = "openai"
    agent.config.llm.model = "gpt-4"
    agent.config.llm.max_tokens = None
    agent.config.llm.temperature = None
    agent.config.llm.max_context_tokens = None
    agent.context.get_messages.return_value = []
    agent._build_openai_tools.return_value = []
    return agent, mock_client


# === _collect_tool_call_deltas Unit Testing ===


class TestCollectToolCallDeltas:
    def test_none_delta_tool_calls(self):
        """delta.tool_calls For None Do not append."""
        chunks: list[dict] = []
        _collect_tool_call_deltas(_Delta(tool_calls=None), chunks)
        assert chunks == []

    def test_none_entry_in_tool_calls_skipped(self):
        """tool_calls In the list None Elements were skipped."""
        chunks: list[dict] = []
        _collect_tool_call_deltas(_Delta(tool_calls=[None]), chunks)
        assert chunks == []

    def test_id_only_chunk_function_none(self):
        """Contains only id The first shard offunction=None) should not crash."""
        chunks: list[dict] = []
        delta = _Delta(tool_calls=[_TCDelta(index=0, id="call_abc", function="none")])
        _collect_tool_call_deltas(delta, chunks)
        assert chunks == [
            {"index": 0, "id": "call_abc", "function": {"name": "", "arguments": ""}}
        ]

    def test_missing_index_defaults_zero(self):
        """index For None Roll back to 0."""
        chunks: list[dict] = []
        delta = _Delta(tool_calls=[_TCDelta(index=None, name="t", arguments="{}")])
        _collect_tool_call_deltas(delta, chunks)
        assert chunks[0]["index"] == 0

    def test_name_and_args_separate_chunks(self):
        """name With arguments Reaching separately in different shards."""
        chunks: list[dict] = []
        _collect_tool_call_deltas(
            _Delta(tool_calls=[_TCDelta(index=0, id="c1", name="scan", arguments="")]), chunks
        )
        _collect_tool_call_deltas(
            _Delta(tool_calls=[_TCDelta(index=0, name="", arguments='{"t":1}')]), chunks
        )
        assert len(chunks) == 2
        assert chunks[0]["function"]["name"] == "scan"
        assert chunks[1]["function"]["arguments"] == '{"t":1}'


# === _validate_tool_call Unit Testing ===


class TestValidateToolCall:
    def _tc(self, id="c1", name="scan", arguments="{}"):
        return MagicMock(id=id, function=MagicMock(name=name, arguments=arguments))

    def test_valid_json_args(self):
        tc = MagicMock(id="c1")
        tc.function.name = "scan"
        tc.function.arguments = '{"target": "x"}'
        assert _validate_tool_call(tc) is True

    def test_empty_args_allowed(self):
        tc = MagicMock(id="c1")
        tc.function.name = "scan"
        tc.function.arguments = ""
        assert _validate_tool_call(tc) is True

    def test_missing_id_rejected(self):
        tc = MagicMock(id="")
        tc.function.name = "scan"
        tc.function.arguments = "{}"
        assert _validate_tool_call(tc) is False

    def test_missing_name_rejected(self):
        tc = MagicMock(id="c1")
        tc.function.name = ""
        tc.function.arguments = "{}"
        assert _validate_tool_call(tc) is False

    def test_truncated_json_rejected(self):
        """Incomplete due to stream interruption JSON Judged to be invalid."""
        tc = MagicMock(id="c1")
        tc.function.name = "scan"
        tc.function.arguments = '{"target": "exam'
        assert _validate_tool_call(tc) is False

    def test_none_function_rejected(self):
        tc = MagicMock(id="c1", function=None)
        assert _validate_tool_call(tc) is False


# === _assemble_tool_calls Unit Testing ===


class TestAssembleToolCalls:
    def test_empty(self):
        assert _assemble_tool_calls([]) == []

    def test_cross_chunk_assembly(self):
        """Across multiple shards id/name/arguments By index Concatenated into a complete call."""
        chunks = [
            {"index": 0, "id": "call_", "function": {"name": "nmap", "arguments": ""}},
            {"index": 0, "id": "123", "function": {"name": "", "arguments": '{"target":'}},
            {"index": 0, "id": "", "function": {"name": "", "arguments": '"x"}'}},
        ]
        result = _assemble_tool_calls(chunks)
        assert len(result) == 1
        assert result[0].id == "call_123"
        assert result[0].function.name == "nmap"
        assert result[0].function.arguments == '{"target":"x"}'

    def test_multiple_indices(self):
        """Different index Parallel tool_call Each aggregation."""
        chunks = [
            {"index": 0, "id": "a", "function": {"name": "t0", "arguments": "{}"}},
            {"index": 1, "id": "b", "function": {"name": "t1", "arguments": "{}"}},
        ]
        result = _assemble_tool_calls(chunks)
        assert len(result) == 2
        names = {tc.function.name for tc in result}
        assert names == {"t0", "t1"}

    def test_incomplete_json_discarded(self):
        """arguments JSON Incomplete calls are discarded."""
        chunks = [
            {"index": 0, "id": "ok", "function": {"name": "good", "arguments": "{}"}},
            {"index": 1, "id": "bad", "function": {"name": "broken", "arguments": '{"t":'}},
        ]
        result = _assemble_tool_calls(chunks)
        assert len(result) == 1
        assert result[0].function.name == "good"

    def test_missing_id_discarded(self):
        """Still missing after aggregation id The invocation of was discarded."""
        chunks = [
            {"index": 0, "id": "", "function": {"name": "noid", "arguments": "{}"}},
        ]
        result = _assemble_tool_calls(chunks)
        assert result == []

    def test_missing_name_discarded(self):
        """Missing after aggregation name The invocation of was discarded."""
        chunks = [
            {"index": 0, "id": "c1", "function": {"name": "", "arguments": "{}"}},
        ]
        result = _assemble_tool_calls(chunks)
        assert result == []


# === End-to-end streaming testing ===


class TestStreamEndToEnd:
    @pytest.mark.asyncio
    async def test_tool_call_id_only_in_first_chunk(self):
        """provider Only at the first chunk Given. tool_call.idLater fragments only have arguments.

        Covers task requirements provider delta Format differences.
        """
        agent, mock_client = _make_agent()
        spy = SpySink()

        chunks = [
            # First fragment:id + name,function Exists but arguments Empty
            _Chunk(tool_calls=[_TCDelta(index=0, id="call_xyz", name="recon", arguments="")]),
            # Subsequent Segments: None id, only arguments Increment
            _Chunk(tool_calls=[_TCDelta(index=0, id=None, name=None, arguments='{"host":')]),
            _Chunk(tool_calls=[_TCDelta(index=0, id=None, name=None, arguments='"a.com"}')]),
        ]
        mock_client.chat.completions.create.return_value = _SyncStream(chunks)

        captured = {}

        async def fake_handle(agent_obj, message):
            captured["tool_calls"] = list(message.tool_calls)
            return "tool done"

        import bughunter.agent.llm_client as mod

        orig = mod.handle_tool_calls
        mod.handle_tool_calls = fake_handle
        try:
            await call_llm_stream(agent, "sys", stream_sink=spy)
        finally:
            mod.handle_tool_calls = orig

        assert "tool_calls" in captured
        tcs = captured["tool_calls"]
        assert len(tcs) == 1
        assert tcs[0].id == "call_xyz"
        assert tcs[0].function.name == "recon"
        assert tcs[0].function.arguments == '{"host":"a.com"}'

    @pytest.mark.asyncio
    async def test_incomplete_tool_call_dropped_end_to_end(self):
        """Stream only reaches halfway arguments → After aggregation JSON Incomplete → No triggering of tool execution."""
        agent, mock_client = _make_agent()
        spy = SpySink()

        chunks = [
            _Chunk(tool_calls=[_TCDelta(index=0, id="c1", name="scan", arguments='{"t":')]),
        ]
        mock_client.chat.completions.create.return_value = _SyncStream(chunks)

        called = {"handle": False}

        async def fake_handle(agent_obj, message):
            called["handle"] = True
            return "x"

        import bughunter.agent.llm_client as mod

        orig = mod.handle_tool_calls
        mod.handle_tool_calls = fake_handle
        try:
            result = await call_llm_stream(agent, "sys", stream_sink=spy)
        finally:
            mod.handle_tool_calls = orig

        # Incomplete calls are discarded, tools not executed, return null full_text
        assert called["handle"] is False
        assert result == ""

    @pytest.mark.asyncio
    async def test_partial_content_preserved_on_disconnect(self):
        """Stream mid-throw ConnectionError Should roll back to non-streaming (fallback) Path.

        Disconnect non- streaming-marker Exception, should be re-thrown according to existing logic —— verification
        Received content Will not trigger additional sink Repeated output.
        """
        agent, mock_client = _make_agent()
        spy = SpySink()

        breaking = _BreakingStream(
            [_Chunk(content="partial ")], RuntimeError("connection reset")
        )

        # The first (streaming) return will disconnect the stream;fallback Non-streaming response returned on call
        non_stream_msg = MagicMock()
        non_stream_msg.content = "recovered"
        non_stream_msg.tool_calls = None
        non_stream_resp = MagicMock(choices=[MagicMock(message=non_stream_msg)])
        mock_client.chat.completions.create.side_effect = [breaking, non_stream_resp, non_stream_resp]

        with pytest.raises(RuntimeError):
            await call_llm_stream(agent, "sys", stream_sink=spy)

        # Before disconnection content token Has been output once
        content_calls = [c for c in spy.calls if c[0] == "content"]
        assert content_calls == [("content", "partial ")]

    @pytest.mark.asyncio
    async def test_content_emitted_exactly_once(self):
        """Main text token Only through on_content_token Output once, no duplicates."""
        agent, mock_client = _make_agent()
        spy = SpySink()

        chunks = [_Chunk(content="A"), _Chunk(content="B"), _Chunk(content="C")]
        mock_client.chat.completions.create.return_value = _SyncStream(chunks)

        result = await call_llm_stream(agent, "sys", stream_sink=spy)

        content_calls = [c for c in spy.calls if c[0] == "content"]
        assert content_calls == [("content", "A"), ("content", "B"), ("content", "C")]
        assert result == "ABC"

    @pytest.mark.asyncio
    async def test_reasoning_not_mixed_into_content(self):
        """reasoning_content Walk thinking Channels, do not mix into the main text token."""
        agent, mock_client = _make_agent()
        spy = SpySink()

        chunks = [
            _Chunk(reasoning="let me think"),
            _Chunk(content="final answer"),
        ]
        mock_client.chat.completions.create.return_value = _SyncStream(chunks)

        result = await call_llm_stream(agent, "sys", stream_sink=spy)

        thinking = [c for c in spy.calls if c[0] == "thinking"]
        content = [c for c in spy.calls if c[0] == "content"]
        assert thinking == [("thinking", "let me think")]
        assert content == [("content", "final answer")]
        # Main text token Does not contain reasoning Text
        assert "let me think" not in "".join(c[1] for c in content)
        # full_text Containing <thinking> packages. + Main text
        assert "<thinking>" in result and "final answer" in result


class TestAutoStreamRobustness:
    @pytest.mark.asyncio
    async def test_reasoning_buffer_reset_between_rounds(self):
        """First round residue reasoning Should not leak to the second-round summary stream (to prevent duplicate output)."""
        agent, mock_client = _make_agent()
        spy = SpySink()

        # Round one:reasoning Residual (no follow-up content Trigger flush)+ tool_call
        first_round = _SyncStream([
            _Chunk(reasoning="round1 reasoning"),
            _Chunk(tool_calls=[_TCDelta(index=0, id="c1", name="t", arguments="{}")]),
        ])
        # Round two summary: brings new elements reasoning + content
        second_round = _SyncStream([
            _Chunk(reasoning="round2 reasoning"),
            _Chunk(content="summary"),
        ])
        mock_client.chat.completions.create.side_effect = [first_round, second_round]

        async def fake_handle(agent_obj, message):
            return [{"tool_call_id": "c1", "content": "result"}], []

        import bughunter.agent.llm_client as mod

        orig = mod.handle_tool_calls_with_results
        mod.handle_tool_calls_with_results = fake_handle
        try:
            result = await call_llm_auto_stream(agent, "sys", "ctx", stream_sink=spy)
        finally:
            mod.handle_tool_calls_with_results = orig

        # round1 's reasoning Should not appear repeatedly in the final text
        assert result.count("round1 reasoning") <= 1
        # The final text should come from the second round of summarization
        assert "summary" in result
        # round2 reasoning Occur only once
        assert result.count("round2 reasoning") == 1
