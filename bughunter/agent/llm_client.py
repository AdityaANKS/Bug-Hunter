"""LLM client helpers for AgentCore."""

from __future__ import annotations

import asyncio
import inspect
import json
import os
import sys
from typing import Any, Optional, Protocol, runtime_checkable

from bughunter.agent.token_counter import estimate_tokens, truncate_messages
from bughunter.agent.tool_call_manager import (
    handle_tool_calls,
    handle_tool_calls_with_results,
)

_CONTEXT_USABLE_RATIO = 0.9
_FALLBACK_RETRY_THRESHOLD = 3  # retries on primary before trying fallback


def _fit_context_window(agent: Any, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Truncate messages to fit the configured context window (90% usable budget).

    If max_context_tokens is not configured, applies a safe default of 60k tokens
    and per-message content truncation to prevent restored sessions from hanging.
    """
    llm = getattr(agent, "config", None)
    llm = getattr(llm, "llm", None) if llm is not None else None
    max_context = getattr(llm, "max_context_tokens", None)
    if not isinstance(max_context, (int, float)) or isinstance(max_context, bool) or max_context <= 0:
        # Safe default — prevents restored sessions from sending megabytes to the API
        max_context = _DEFAULT_CONTEXT_TOKENS

    # Phase 1: Truncate individual message content to prevent single tool outputs
    # from dominating the context window (e.g., massive nmap/fetch output from
    # a previous session). System prompt is exempt.
    messages = _cap_message_content(messages)

    budget = int(max_context * _CONTEXT_USABLE_RATIO)
    current = estimate_tokens(messages)

    # Debug log — helps diagnose slow responses due to large context
    try:
        print(
            f"[context] {len(messages)} messages, ~{current} tokens "
            f"(budget {budget})",
            file=sys.stderr,
        )
    except Exception:
        pass

    if current <= budget:
        return messages

    trimmed = truncate_messages(messages, budget, preserve_system=True)
    try:
        from rich.console import Console

        Console().print(
            f"[yellow][!] Context ~ {current} tokens exceeds window budget {budget},"
            f"truncated to ~ {estimate_tokens(trimmed)} tokens ({len(trimmed)} msgs)[/yellow]"
        )
    except Exception:
        print(f"[!] Context truncation: {current} → {estimate_tokens(trimmed)} tokens (budget {budget})")
    return trimmed


# Maximum characters per message content field before summarization kicks in.
# 8000 chars ≈ 2000 tokens — large enough for useful tool output, small enough
# to prevent a single restored message from consuming the entire context budget.
_MAX_MSG_CONTENT_CHARS = 8000
# Default context token budget when max_context_tokens is not configured.
# 60k tokens provides a good balance — large enough for useful history,
# small enough for fast API response times.
_DEFAULT_CONTEXT_TOKENS = 60_000

# Patterns that mark lines worth keeping during summarization
import re as _re

_IMPORTANT_LINE_PATTERNS = [
    _re.compile(r"(?:status|http)[:\s]*[1-5]\d{2}", _re.IGNORECASE),  # HTTP status codes
    _re.compile(r"\b(?:port|PORT)\s*\d+", _re.IGNORECASE),  # Port numbers
    _re.compile(r"\b(?:open|closed|filtered)\b", _re.IGNORECASE),  # Port states
    _re.compile(r"\b(?:vuln|vulnerability|CVE-\d{4}|exploit|injection|xss|sqli|rce|ssrf|lfi|rfi)\b", _re.IGNORECASE),
    _re.compile(r"\b(?:flag|ctf|key|secret|password|token|credential|hash)\b", _re.IGNORECASE),
    _re.compile(r"\b(?:found|discovered|detected|confirmed|verified|warning|critical|high|medium)\b", _re.IGNORECASE),
    _re.compile(r"\[(?:tool|✓|✗|!|\+|\-|DONE|finding|FINDING)[\]:]]", _re.IGNORECASE),  # Tool/finding markers
    _re.compile(r"(?:server|x-powered-by|content-type|set-cookie|authorization|www-authenticate)\s*:", _re.IGNORECASE),  # Key headers
    _re.compile(r"\b(?:nginx|apache|iis|tomcat|php|node|django|flask|spring|wordpress)\b", _re.IGNORECASE),  # Tech stack
    _re.compile(r"(?:endpoint|path|route|api|url)\s*[=:]\s*\S+", _re.IGNORECASE),  # Endpoints
    _re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),  # IP addresses
    _re.compile(r"(?:error|exception|traceback|denied|forbidden|unauthorized)", _re.IGNORECASE),  # Errors
]


def _cap_message_content(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarize oversized message content to preserve key findings and facts.

    Instead of dumb head/tail truncation, this extracts important lines (findings,
    vulnerabilities, HTTP status codes, tool results, ports, tech stack, etc.)
    into a structured summary so the LLM retains all critical pentest intelligence.
    System messages (index 0) are exempt.
    """
    result = []
    for idx, msg in enumerate(messages):
        content = msg.get("content")
        if idx == 0 or not isinstance(content, str) or len(content) <= _MAX_MSG_CONTENT_CHARS:
            result.append(msg)
            continue

        summarized = _summarize_long_content(content)
        capped = dict(msg)
        capped["content"] = summarized
        result.append(capped)
    return result


def _summarize_long_content(content: str) -> str:
    """Extract key findings from oversized content into a structured summary.

    Strategy:
    1. Keep the first 500 chars (usually contains the command/tool name + target)
    2. Scan ALL lines and keep those matching important patterns
    3. Keep the last 500 chars (usually contains conclusions)
    4. Deduplicate and format as a structured summary
    """
    lines = content.split("\n")
    original_len = len(content)

    # 1. Header — first few lines (command/target info)
    header_chars = 0
    header_lines = []
    for line in lines:
        if header_chars >= 500:
            break
        header_lines.append(line)
        header_chars += len(line) + 1

    # 2. Extract ALL important lines from the full content
    important_lines = []
    seen_normalized = set()
    
    def _normalize_for_dedup(text: str) -> str:
        # Lowercase, truncate, and strip out numbers/IPs to collapse highly similar lines 
        # (e.g. "PORT 80 open" vs "PORT 81 open")
        text = text.lower()[:80]
        text = _re.sub(r'\d+', 'N', text)
        return text

    for line in lines:
        stripped = line.strip()
        if not stripped or len(stripped) < 5:
            continue
        # Check against all important patterns
        for pattern in _IMPORTANT_LINE_PATTERNS:
            if pattern.search(stripped):
                norm_key = _normalize_for_dedup(stripped)
                if norm_key not in seen_normalized:
                    seen_normalized.add(norm_key)
                    # Cap individual lines at 300 chars
                    important_lines.append(stripped[:300])
                break

    # 3. Tail — last few lines (conclusions/summary)
    tail_chars = 0
    tail_lines = []
    for line in reversed(lines):
        if tail_chars >= 500:
            break
        tail_lines.insert(0, line)
        tail_chars += len(line) + 1

    # 4. Build structured summary
    parts = []
    parts.append("\n".join(header_lines))

    if important_lines:
        # Cap at 40 most important lines to stay within budget
        capped_important = important_lines[:40]
        parts.append(
            f"\n--- Key findings extracted from {original_len} chars ({len(lines)} lines) ---\n"
            + "\n".join(f"• {line}" for line in capped_important)
        )
        if len(important_lines) > 40:
            parts.append(f"  ... and {len(important_lines) - 40} more findings")
    else:
        parts.append(f"\n--- [summarized: {original_len} chars, no key findings extracted] ---")

    parts.append("\n--- End of content ---\n" + "\n".join(tail_lines))

    summary = "\n".join(parts)

    # Safety: if summary is still too long, hard-truncate
    if len(summary) > _MAX_MSG_CONTENT_CHARS:
        summary = summary[:_MAX_MSG_CONTENT_CHARS] + "\n... [hard truncated]"

    return summary



def extract_response(message: Any) -> str:
    """Extract the actual response text from an LLM message.

    Handles:
    1. Normal content (no thinking)
    2. Content with inline <thinking> tags (open/closed)
    3. Separate reasoning_content field (DeepSeek R1, etc.)
    """
    content = message.content or ""
    reasoning = getattr(message, "reasoning_content", None) or ""
    if reasoning and not content:
        content = f"<thinking>\n{reasoning}\n</thinking>\n"
    elif reasoning and content:
        content = f"<thinking>\n{reasoning}\n</thinking>\n{content}"
    return content


def _is_non_retriable_llm_error(error_text: str) -> bool:
    """Return True for configuration/auth errors that should fail fast."""
    hard_fail_markers = [
        "bad_request_error",
        "incorrect api key",
        "invalid api key",
        "invalid chat setting",
        "invalid function arguments json string",
        "tool_call_id",
        "authentication",
        "unauthorized",
        "permission denied",
        "model not found",
        "no such model",
        "invalid_request_error",
        "unsupported parameter",
    ]
    return any(marker in error_text for marker in hard_fail_markers)


def _is_fallback_eligible_error(error_text: str) -> bool:
    """Return True for errors that warrant trying a fallback provider.

    Rate limits, timeouts, model unavailability, and server errors.
    Auth errors are excluded (they'd fail on fallback too if misconfigured).
    """
    fallback_markers = [
        "rate limit",
        "rate_limit",
        "429",
        "timeout",
        "timed out",
        "server error",
        "502",
        "503",
        "504",
        "service unavailable",
        "model not found",
        "no such model",
        "overloaded",
        "capacity",
        "connection error",
        "connection reset",
    ]
    return any(marker in error_text for marker in fallback_markers)


def _is_openai_reasoning_model(provider: str, model: str) -> bool:
    """Return True for OpenAI models that use the newer reasoning parameter set."""
    if provider.lower() != "openai":
        return False
    normalized = model.lower()
    return normalized.startswith(("o1", "o3", "o4", "gpt-5"))


def build_chat_completion_kwargs(
    agent: Any,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    *,
    max_tokens: int | None = None,
    temperature: float | None = None,
) -> dict[str, Any]:
    """Build provider-compatible Chat Completions kwargs.

    OpenAI reasoning/GPT-5 models reject the legacy max_tokens field and expect
    max_completion_tokens instead. Other OpenAI-compatible providers may still
    require the older field, so keep the switch scoped to OpenAI's newer model
    families.
    """
    llm = agent.config.llm
    provider = str(getattr(llm, "provider", "") or "").lower()
    model = str(getattr(llm, "model", "") or "")
    token_limit = max_tokens if max_tokens is not None else getattr(llm, "max_tokens", None)
    temp = temperature if temperature is not None else getattr(llm, "temperature", None)
    uses_reasoning_params = _is_openai_reasoning_model(provider, model)

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
    }
    if token_limit is not None:
        if uses_reasoning_params:
            kwargs["max_completion_tokens"] = token_limit
        else:
            kwargs["max_tokens"] = token_limit
    if temp is not None and not uses_reasoning_params:
        kwargs["temperature"] = temp
    if tools:
        kwargs["tools"] = tools
    if uses_reasoning_params:
        reasoning_effort = getattr(llm, "reasoning_effort", None)
        if reasoning_effort:
            kwargs["reasoning_effort"] = reasoning_effort
    return kwargs


async def _call_with_persistent_retries(
    agent: Any, request_fn, stage_label: str
) -> tuple[Any, int]:
    """Keep retrying retriable LLM calls until success or manual interruption.

    After _FALLBACK_RETRY_THRESHOLD failed attempts on the primary provider,
    automatically tries fallback providers (with key rotation) before resuming
    retries on the primary.

    Returns:
        (response, retry_attempts)
    """
    from bughunter.config.settings import make_openai_client

    loop = asyncio.get_running_loop()
    retry_attempts = 0
    last_error: Exception | None = None

    while True:
        try:
            maybe_response = loop.run_in_executor(None, request_fn)
            response = await maybe_response if inspect.isawaitable(maybe_response) else maybe_response
            if response is not None and getattr(response, "choices", None):
                return response, retry_attempts

            retry_attempts += 1
            print(
                f"[!] {stage_label} LLM API abnormal response, retry #{retry_attempts} in 5s...",
                file=sys.stdout,
                flush=True,
            )
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            error_text = str(exc).lower()
            if _is_non_retriable_llm_error(error_text):
                raise

            retry_attempts += 1
            last_error = exc
            print(
                f"[!] {stage_label} LLM connection error, retry #{retry_attempts}... ({exc})",
                file=sys.stdout,
                flush=True,
            )
            await asyncio.sleep(5)

        # ── Fallback: model pool + legacy fallback providers ────────
        if retry_attempts >= _FALLBACK_RETRY_THRESHOLD:
            # Try model pool entries first (tier-ordered)
            model_pool = getattr(
                getattr(getattr(agent, "config", None), "llm", None),
                "model_pool", [],
            )
            primary_model = getattr(
                getattr(getattr(agent, "config", None), "llm", None),
                "model", "",
            )

            for pool_entry in model_pool:
                if not pool_entry.enabled:
                    continue
                if pool_entry.model == primary_model:
                    continue  # skip primary, we already tried it
                api_key = os.environ.get(pool_entry.api_key_env, "") if pool_entry.api_key_env else ""
                if not api_key:
                    continue
                print(
                    f"[*] Pool failover → {pool_entry.name} (tier {pool_entry.tier}, {pool_entry.role})",
                    file=sys.stdout,
                    flush=True,
                )
                try:
                    pool_client = make_openai_client(
                        api_key=api_key,
                        base_url=pool_entry.base_url,
                    )
                    pool_kwargs = _build_fallback_kwargs(agent, pool_entry.model)
                    pool_response = await loop.run_in_executor(
                        None,
                        lambda c=pool_client, k=pool_kwargs: c.chat.completions.create(**k),
                    )
                    if pool_response is not None and getattr(pool_response, "choices", None):
                        print(
                            f"[+] Pool model {pool_entry.name} succeeded!",
                            file=sys.stdout,
                            flush=True,
                        )
                        return pool_response, retry_attempts
                except asyncio.CancelledError:
                    raise
                except KeyboardInterrupt:
                    raise
                except Exception as pool_exc:
                    print(
                        f"[!] Pool model {pool_entry.name} failed: {pool_exc}",
                        file=sys.stdout,
                        flush=True,
                    )
                    continue

            # Legacy fallback providers
            fallback_providers = getattr(
                getattr(getattr(agent, "config", None), "llm", None),
                "fallback_providers", [],
            )
            if fallback_providers:
                for fb in fallback_providers:
                    all_keys = [fb.api_key] + list(fb.api_keys or [])
                    fb_model = fb.model or primary_model

                    for key_idx, api_key in enumerate(all_keys):
                        key_label = f"key #{key_idx + 1}" if len(all_keys) > 1 else "key"
                        print(
                            f"[*] Switching to fallback provider: {fb.name} ({key_label}), model: {fb_model}",
                            file=sys.stdout,
                            flush=True,
                        )
                        try:
                            fb_client = make_openai_client(
                                api_key=api_key,
                                base_url=fb.base_url,
                            )
                            fb_kwargs = _build_fallback_kwargs(agent, fb_model)
                            fb_response = await loop.run_in_executor(
                                None,
                                lambda c=fb_client, k=fb_kwargs: c.chat.completions.create(**k),
                            )
                            if fb_response is not None and getattr(fb_response, "choices", None):
                                print(
                                    f"[+] Fallback provider {fb.name} succeeded!",
                                    file=sys.stdout,
                                    flush=True,
                                )
                                return fb_response, retry_attempts
                        except asyncio.CancelledError:
                            raise
                        except KeyboardInterrupt:
                            raise
                        except Exception as fb_exc:
                            print(
                                f"[!] Fallback provider {fb.name} ({key_label}) failed: {fb_exc}",
                                file=sys.stdout,
                                flush=True,
                            )
                            continue

            # All pool models and fallbacks exhausted, continue retrying primary
            print(
                f"[!] All pool models and fallback providers exhausted, resuming primary retries...",
                file=sys.stdout,
                flush=True,
            )


def _build_fallback_kwargs(agent: Any, model: str) -> dict[str, Any]:
    """Build minimal chat completion kwargs for a fallback provider call.

    Re-uses the agent's current messages and tools but overrides the model.
    """
    llm = getattr(agent, "config", None)
    llm = getattr(llm, "llm", None) if llm is not None else None
    messages = [{"role": "system", "content": getattr(agent, "_last_system_prompt", "You are a helpful assistant.")}]
    messages.extend(agent.context.get_messages())
    messages = _fit_context_window(agent, messages)

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
    }
    max_tokens = getattr(llm, "max_tokens", None) if llm else None
    temp = getattr(llm, "temperature", None) if llm else None
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if temp is not None:
        kwargs["temperature"] = temp

    tools = agent._build_openai_tools()
    if tools:
        kwargs["tools"] = tools
    return kwargs


def _prepend_retry_notice(text: str, retry_attempts: int) -> str:
    """Annotate a successful response if retries happened within the same round."""
    if retry_attempts <= 0:
        return text
    return f"[LLM recovered] This round recovered after {retry_attempts} reconnection(s).\n{text}"


def _format_tool_results_fallback(
    tool_results: list[dict[str, Any]], skipped_info: list[str]
) -> str:
    """Build a plain-text fallback summary when provider tool-summary format is incompatible."""
    parts = ["[tool results processed] Provider incompatible with standard tool summary, degraded to plain text:"]
    for item in tool_results:
        content = item.get("content", "") if isinstance(item, dict) else str(item)
        if len(content) > 800:
            content = content[:400] + "\n...[truncated]...\n" + content[-400:]
        parts.append(content)
    if skipped_info:
        parts.append("⚠️ Skipped this round: " + "; ".join(skipped_info))
    return "\n".join(parts)


async def call_llm(
    agent: Any,
    system_prompt: str,
    *,
    stream_sink: Optional["StreamSink"] = None,
) -> str:
    """Call the LLM with the current context and system prompt (single turn)."""
    if stream_sink is not None:
        return await call_llm_stream(agent, system_prompt, stream_sink)

    client = agent._get_client()

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(agent.context.get_messages())
    messages = _fit_context_window(agent, messages)
    tools = agent._build_openai_tools()

    kwargs = build_chat_completion_kwargs(agent, messages, tools)

    response, retry_attempts = await _call_with_persistent_retries(
        agent,
        lambda: client.chat.completions.create(**kwargs),
        "Single-turn",
    )

    choice = response.choices[0]
    if choice.message.tool_calls:
        return _prepend_retry_notice(await handle_tool_calls(agent, choice.message), retry_attempts)
    return _prepend_retry_notice(extract_response(choice.message), retry_attempts)


async def call_llm_auto(
    agent: Any,
    system_prompt: str,
    round_context: str,
    *,
    stream_sink: Optional["StreamSink"] = None,
) -> str:
    """Call the LLM in auto-pentest mode with round context appended."""
    if stream_sink is not None:
        return await call_llm_auto_stream(agent, system_prompt, round_context, stream_sink)

    client = agent._get_client()

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(agent.context.get_messages())
    messages.append({"role": "user", "content": round_context})
    messages = _fit_context_window(agent, messages)
    tools = agent._build_openai_tools()

    kwargs = build_chat_completion_kwargs(agent, messages, tools)

    response, retry_attempts = await _call_with_persistent_retries(
        agent,
        lambda: client.chat.completions.create(**kwargs),
        "Auto-loop",
    )

    choice = response.choices[0]
    if choice.message.tool_calls:
        tool_results, skipped_info = await handle_tool_calls_with_results(agent, choice.message)

        executed_tcs = []
        for tc in tool_results:
            if not isinstance(tc, dict) or "tool_call" not in tc:
                import sys

                print(f"[!] Skipped malformed ToolResult: {type(tc).__name__} {str(tc)[:100]}", file=sys.stderr)
                continue
            executed_tcs.append(tc["tool_call"])

        assistant_msg = {
            "role": "assistant",
            "content": choice.message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in executed_tcs
            ],
        }
        messages.append(assistant_msg)

        for tool_result in tool_results:
            if isinstance(tool_result, dict) and "tool_call_id" in tool_result:
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_result["tool_call_id"],
                        "content": tool_result.get("content", ""),
                    }
                )

        tool_summary_parts = []
        for tc in executed_tcs:
            try:
                args_str = str(tc.function.arguments)[:200]
            except Exception:
                args_str = "<unreadable>"
            tool_summary_parts.append(f"Called tool: {tc.function.name}({args_str})")
        for tr in tool_results:
            content = tr.get("content", "") if isinstance(tr, dict) else str(tr)
            if len(content) > 1000:
                content = content[:500] + "\n...[truncated]...\n" + content[-500:]
            tool_summary_parts.append(f"ToolResult: {content}")
            if (
                isinstance(tr, dict)
                and isinstance(tr.get("structured_content"), dict)
                and tr["structured_content"]
            ):
                structured = json.dumps(tr["structured_content"], ensure_ascii=False)
                if len(structured) > 1000:
                    structured = structured[:500] + "\n...[truncated]...\n" + structured[-500:]
                tool_summary_parts.append(f"Structured result: {structured}")
        if skipped_info:
            tool_summary_parts.append(f"⚠️ Skipped this round: {'; '.join(skipped_info)}")

        try:
            kwargs["messages"] = _fit_context_window(agent, messages)
            response2, second_retry_attempts = await _call_with_persistent_retries(
                agent,
                lambda: client.chat.completions.create(**kwargs),
                "Tool-summary",
            )
            final_text = extract_response(response2.choices[0].message)
            # Context already written by loop_controller / core.py, avoid duplicates
            return _prepend_retry_notice(final_text, retry_attempts + second_retry_attempts)
        except Exception as e2:
            error_text = str(e2).lower()
            if _is_non_retriable_llm_error(error_text):
                fallback = _format_tool_results_fallback(tool_results, skipped_info)
                # Same as above: don't write context here
                return fallback
            return f"[tool results processed] Follow-up analysis error: {e2}"

    return _prepend_retry_notice(extract_response(choice.message), retry_attempts)


# === Stream LLM Call Helpers ===


class _AsyncIterWrapper:
    """Wrap sync iterable as async iterable for unified async-for usage.

    OpenAI sync client returns a sync Stream (needs wrapping for async-for).
    Test mock / async client returns an async Stream (used directly).
    """

    def __init__(self, iterable):
        self._iter = iter(iterable)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


def _ensure_async_iter(response):
    """Return an async-iterable, compatible with both sync and async Streams.

    Check order: async-iterable → sync-iterable → non-iterable returns None (triggers fallback).
    """
    if hasattr(response, "__aiter__"):
        return response
    if hasattr(response, "__iter__"):
        return _AsyncIterWrapper(response)
    return None  # Not iterable; caller should degrade to non-streaming path


def _collect_tool_call_deltas(delta: Any, tool_calls_chunks: list[dict]) -> None:
    """Extract tool_call fragments from a single streaming delta, append to accumulator.

    Handles cross-provider differences:
    - Some providers send only the id in the first fragment (function field is None)
    - Some providers deliver name and arguments in separate fragments
    - index may be missing or None (falls back to 0)
    - tc_delta itself may be None
    """
    tc = getattr(delta, "tool_calls", None)
    if not tc:
        return
    for tc_delta in tc:
        if tc_delta is None:
            continue
        # function field may be None in the first fragment that only contains the id
        func = getattr(tc_delta, "function", None)
        if func is not None:
            name = getattr(func, "name", None) or ""
            arguments = getattr(func, "arguments", None) or ""
        else:
            name = ""
            arguments = ""
        index = getattr(tc_delta, "index", None)
        if index is None:
            index = 0
        tool_calls_chunks.append({
            "index": index,
            "id": getattr(tc_delta, "id", None) or "",
            "function": {"name": name, "arguments": arguments},
        })


def _validate_tool_call(tool_call: Any) -> bool:
    """Validate that an assembled tool_call is complete and usable.

    Requirements:
    - id is non-empty (some providers only emit it in the first fragment)
    - function.name is non-empty
    - arguments is valid JSON or an empty string (stream interruption can produce truncated JSON)
    """
    tc_id = getattr(tool_call, "id", None)
    if not tc_id:
        return False
    func = getattr(tool_call, "function", None)
    if func is None or not getattr(func, "name", None):
        return False
    arguments = getattr(func, "arguments", None)
    if arguments in (None, ""):
        return True
    try:
        json.loads(arguments)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def _build_tool_call(tc_id: str, name: str, arguments: str) -> Any:
    """Construct a tool_call object.

    Prefers the official OpenAI pydantic types (production path); falls back to
    lightweight equivalent objects (exposing .id/.type/.function.name/.function.arguments)
    so assembly logic can be tested without the openai package installed.
    """
    try:
        from openai.types.chat.chat_completion_message_tool_call import (
            ChatCompletionMessageToolCall,
            Function,
        )

        return ChatCompletionMessageToolCall(
            id=tc_id,
            type="function",
            function=Function(name=name, arguments=arguments),
        )
    except Exception:
        func = type("Function", (), {"name": name, "arguments": arguments})()
        return type("ToolCall", (), {"id": tc_id, "type": "function", "function": func})()


def _assemble_tool_calls(tool_calls_chunks: list[dict]) -> list[Any]:
    """Assemble accumulated streaming fragments into complete tool_call objects by index.

    Concatenates id/name/arguments from fragments arriving across multiple chunks, aligned by index.
    Validates each assembled call, discarding those with missing id, missing name, or incomplete JSON args.
    """
    if not tool_calls_chunks:
        return []

    # Align and concatenate by index (dict preserves first-seen order)
    tc_by_index: dict[int, dict] = {}
    for tc_chunk in tool_calls_chunks:
        idx = tc_chunk["index"]
        if idx not in tc_by_index:
            tc_by_index[idx] = {"id": "", "function": {"name": "", "arguments": ""}}
        tc_by_index[idx]["id"] += tc_chunk["id"]
        tc_by_index[idx]["function"]["name"] += tc_chunk["function"]["name"]
        tc_by_index[idx]["function"]["arguments"] += tc_chunk["function"]["arguments"]

    tool_calls: list[Any] = []
    for tc_data in tc_by_index.values():
        candidate = _build_tool_call(
            tc_data["id"],
            tc_data["function"]["name"],
            tc_data["function"]["arguments"],
        )
        if not _validate_tool_call(candidate):
            print(
                f"[!] Discarded incomplete streaming tool_call: id={tc_data['id']!r} "
                f"name={tc_data['function']['name']!r} "
                f"args={tc_data['function']['arguments'][:80]!r}",
                file=sys.stderr,
                flush=True,
            )
            continue
        tool_calls.append(candidate)

    return tool_calls


async def call_llm_stream(
    agent: Any,
    system_prompt: str,
    stream_sink: Optional["StreamSink"] = None,
) -> str:
    """Call the LLM with streaming output.

    Args:
        agent: AgentCore instance
        system_prompt: System prompt
        stream_sink: Output sink for streaming (None = silent)

    Returns:
        Full response text (same as non-streaming version)
    """
    if stream_sink is None:
        stream_sink = _NullSink()

    client = agent._get_client()

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(agent.context.get_messages())
    messages = _fit_context_window(agent, messages)
    tools = agent._build_openai_tools()

    kwargs = build_chat_completion_kwargs(agent, messages, tools)

    try:
        stream_sink.on_status("Thinking...")
        response = client.chat.completions.create(**kwargs, stream=True)

        full_text = ""
        reasoning_buffer = ""
        tool_calls_chunks: list[dict] = []

        # Auto-adapt sync/async Stream (sync Stream wrapped with _AsyncIterWrapper)
        _stream = _ensure_async_iter(response)
        if _stream is None:
            raise ValueError("LLM response is not a valid stream object")
        async for chunk in _stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta

                # Handle reasoning_content (DeepSeek R1, etc.)
                reasoning = getattr(delta, "reasoning_content", None) or ""
                if reasoning:
                    reasoning_buffer += reasoning
                    stream_sink.on_thinking_token(reasoning)

                # Handle content
                content = getattr(delta, "content", None) or ""
                if content:
                    if reasoning_buffer:
                        full_text += f"<thinking>\n{reasoning_buffer}\n</thinking>\n"
                        reasoning_buffer = ""
                    stream_sink.on_content_token(content)
                    full_text += content

                # Handle tool_calls (streaming chat mode also needs processing)
                _collect_tool_call_deltas(delta, tool_calls_chunks)

        if reasoning_buffer:
            full_text += f"<thinking>\n{reasoning_buffer}\n</thinking>\n"

        stream_sink.on_stream_end()

        # If tool_calls present, route to handle_tool_calls (same logic as call_llm_auto_stream)
        if tool_calls_chunks:
            tool_calls = _assemble_tool_calls(tool_calls_chunks)

            if tool_calls:
                dummy_msg = type("obj", (object,), {
                    "content": full_text,
                    "tool_calls": tool_calls,
                })()
                for tc in tool_calls:
                    stream_sink.on_tool_call(tc.function.name, tc.function.arguments[:200])
                # Execute tools and make a second-round LLM call
                result = await handle_tool_calls(agent, dummy_msg)
                if result:
                    stream_sink.on_content_token(result)
                stream_sink.on_stream_end()
                return result

        return full_text

    except Exception as e:
        # Fallback to non-streaming on streaming-related errors or general failures
        error_text = str(e).lower()
        streaming_markers = [
            "not supported", "not implemented", "streaming",
            "requires an object with __aiter__",
            "stream is not iterable", "doesn't support",
            "not a valid stream",
        ]
        if any(marker in error_text for marker in streaming_markers):
            # Provider doesn't support streaming or other streaming error, fall back
            pass
        else:
            # Other error, re-raise
            raise

    # Fallback: non-streaming with simulated streaming
    # Use existing call_llm as fallback
    response_fallback, _ = await _call_with_persistent_retries(
        agent,
        lambda: client.chat.completions.create(**kwargs),
        "Single-turn",
    )

    # Degrade to non-streaming call_llm (with retry + tool_calls handling), consistent behavior
    return await call_llm(agent, system_prompt)


async def call_llm_auto_stream(
    agent: Any,
    system_prompt: str,
    round_context: str,
    stream_sink: Optional["StreamSink"] = None,
) -> str:
    """Call the LLM in auto-pentest mode with streaming output.

    Args:
        agent: AgentCore instance
        system_prompt: System prompt
        round_context: Round context for auto mode
        stream_sink: Output sink for streaming (None = silent)

    Returns:
        Full response text
    """
    if stream_sink is None:
        stream_sink = _NullSink()

    client = agent._get_client()

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(agent.context.get_messages())
    messages.append({"role": "user", "content": round_context})
    messages = _fit_context_window(agent, messages)
    tools = agent._build_openai_tools()

    kwargs = build_chat_completion_kwargs(agent, messages, tools)

    try:
        # First LLM call with streaming
        stream_sink.on_status("Thinking...")
        response = client.chat.completions.create(**kwargs, stream=True)

        full_text = ""
        reasoning_buffer = ""
        tool_calls_chunks: list[dict] = []

        # Auto-adapt sync/async Stream
        _stream = _ensure_async_iter(response)
        if _stream is None:
            raise ValueError("LLM response is not a valid stream object")
        async for chunk in _stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta

                # Handle reasoning_content
                reasoning = getattr(delta, "reasoning_content", None) or ""
                if reasoning:
                    reasoning_buffer += reasoning
                    stream_sink.on_thinking_token(reasoning)

                # Handle content
                content = getattr(delta, "content", None) or ""
                if content:
                    if reasoning_buffer:
                        full_text += f"<thinking>\n{reasoning_buffer}\n</thinking>\n"
                        reasoning_buffer = ""
                    stream_sink.on_content_token(content)
                    full_text += content

                # Handle tool_calls
                _collect_tool_call_deltas(delta, tool_calls_chunks)

        stream_sink.on_stream_end()

        # Flush reasoning (reset buffer to avoid leaking into second-round summary stream)
        if reasoning_buffer:
            full_text += f"<thinking>\n{reasoning_buffer}\n</thinking>\n"
            reasoning_buffer = ""

        # Check if we have tool calls
        choice_dummy = type("obj", (object,), {"message": type("obj", (object,), {
            "content": full_text,
            "tool_calls": None,
        })()})()

        # Reconstruct message for tool call handling
        # We need to check if there are tool calls from the accumulated chunks
        if tool_calls_chunks:
            tool_calls = _assemble_tool_calls(tool_calls_chunks)

            if tool_calls:
                # Streaming-assembled tool_calls only exist in delta fragments; backfill to aggregated message
                # Patch the dummy message with actual tool calls
                choice_dummy.message.tool_calls = tool_calls
                # Execute tool calls
                for tc in tool_calls:
                    stream_sink.on_tool_call(tc.function.name, tc.function.arguments[:200])

                tool_results, skipped_info = await handle_tool_calls_with_results(agent, choice_dummy.message)

                for tr in tool_results:
                    if isinstance(tr, dict) and "content" in tr:
                        content = tr["content"]
                        if len(content) > 200:
                            content = content[:200] + "..."
                        stream_sink.on_tool_result(content)

                # Continue with the messages including tool results
                assistant_msg = {
                    "role": "assistant",
                    "content": full_text,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in tool_calls
                    ],
                }
                messages.append(assistant_msg)

                for tool_result in tool_results:
                    if isinstance(tool_result, dict) and "tool_call_id" in tool_result:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_result["tool_call_id"],
                            "content": tool_result.get("content", ""),
                        })

                # Second LLM call (streaming) for summary
                kwargs["messages"] = _fit_context_window(agent, messages)
                stream_sink.on_status("Summarizing...")

                try:
                    response2 = client.chat.completions.create(**kwargs, stream=True)
                    full_text = ""

                    _stream2 = _ensure_async_iter(response2)
                    if _stream2 is None:
                        raise ValueError("LLM response is not a valid stream object")
                    async for chunk in _stream2:
                        if chunk.choices and len(chunk.choices) > 0:
                            delta = chunk.choices[0].delta
                            reasoning = getattr(delta, "reasoning_content", None) or ""
                            if reasoning:
                                reasoning_buffer += reasoning
                                stream_sink.on_thinking_token(reasoning)

                            content = getattr(delta, "content", None) or ""
                            if content:
                                if reasoning_buffer:
                                    full_text += f"<thinking>\n{reasoning_buffer}\n</thinking>\n"
                                    reasoning_buffer = ""
                                stream_sink.on_content_token(content)
                                full_text += content

                    if reasoning_buffer:
                        full_text += f"<thinking>\n{reasoning_buffer}\n</thinking>\n"

                    # Context written by loop_controller, not duplicated here
                    stream_sink.on_stream_end()
                    return full_text

                except Exception as e2:
                    error_text = str(e2).lower()
                    if _is_non_retriable_llm_error(error_text):
                        fallback = _format_tool_results_fallback(tool_results, skipped_info)
                        # Same as above: don't write context here
                        return fallback
                    return f"[tool results processed] Follow-up analysis error: {e2}"

        # Context already written by caller, not duplicated here
        return full_text

    except (NotImplementedError, ValueError, Exception) as e:
        error_text = str(e).lower()
        if not any(
            marker in error_text
            for marker in [
                "not supported", "not implemented", "streaming",
            ]
        ):
            raise

    # Fallback to non-streaming
    return await call_llm_auto(agent, system_prompt, round_context)


# === Stream Output Protocol ===


@runtime_checkable
class StreamSink(Protocol):
    """Abstract output stream sink.

    The LLM call layer routes output to different targets (CLI/Web/silent) via this interface.
    Placed in llm_client.py per the module placement guidelines in CONTRIBUTING.md.
    """

    def on_status(self, message: str) -> None:
        """Display a status hint (e.g. 'Thinking...')."""
        ...

    def on_thinking_token(self, token: str) -> None:
        """Receive a thinking/reasoning token (display is optional)."""
        ...

    def on_content_token(self, token: str) -> None:
        """Receive a content token."""
        ...

    def on_tool_call(self, tool_name: str, args: str) -> None:
        """Display a tool call notification."""
        ...

    def on_tool_result(self, result_summary: str) -> None:
        """Display a tool result summary."""
        ...

    def on_stream_end(self) -> None:
        """Stream-end callback (newline/cleanup)."""
        ...


class _NullSink:
    """No-op implementation, ensures no output when no sink is provided."""

    def on_status(self, message: str) -> None:
        pass

    def on_thinking_token(self, token: str) -> None:
        pass

    def on_content_token(self, token: str) -> None:
        pass

    def on_tool_call(self, tool_name: str, args: str) -> None:
        pass

    def on_tool_result(self, result_summary: str) -> None:
        pass

    def on_stream_end(self) -> None:
        pass
