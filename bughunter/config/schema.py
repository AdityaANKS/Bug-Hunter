"""Bug Hunter configuration schema — Pydantic models for type-safe config."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ── LLM Provider Presets ────────────────────────────────────────────


class LLMProvider(str, Enum):
    """Supported LLM providers with OpenAI-compatible APIs."""

    OPENAI = "openai"
    NVIDIA = "nvidia"
    OPENROUTER = "openrouter"
    MINIMAX = "minimax"
    DEEPSEEK = "deepseek"
    ZHIPU = "zhipu"
    MOONSHOT = "moonshot"
    QWEN = "qwen"
    SILICONFLOW = "siliconflow"
    DOUBAO = "doubao"
    BAICHUAN = "baichuan"
    STEPFUN = "stepfun"
    SENSETIME = "sensetime"
    YI = "yi"
    CUSTOM = "custom"


# Provider preset definitions: base_url + default_model + notes
PROVIDER_PRESETS: dict[LLMProvider, dict[str, str]] = {
    LLMProvider.OPENAI: {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
        "label": "OpenAI",
    },
    LLMProvider.NVIDIA: {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "default_model": "z-ai/glm-5.2",
        "label": "NVIDIA (NIM)",
    },
    LLMProvider.OPENROUTER: {
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "z-ai/glm-5.2",
        "label": "OpenRouter",
    },
    LLMProvider.MINIMAX: {
        "base_url": "https://api.minimaxi.com/v1",
        "default_model": "MiniMax-M3",
        "label": "MiniMax",
    },
    LLMProvider.DEEPSEEK: {
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-v4-pro",
        "label": "DeepSeek",
    },
    LLMProvider.ZHIPU: {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-5.2",
        "label": "Zhipu GLM",
    },
    LLMProvider.MOONSHOT: {
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "kimi-k2.6",
        "label": "Kimi (Moonshot)",
    },
    LLMProvider.QWEN: {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen3-max",
        "label": "Qwen (Alibaba)",
    },
    LLMProvider.SILICONFLOW: {
        "base_url": "https://api.siliconflow.cn/v1",
        "default_model": "deepseek-ai/DeepSeek-V4-Flash",
        "label": "SiliconFlow",
    },
    LLMProvider.DOUBAO: {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "default_model": "Doubao-Seed-2.0-Pro",
        "label": "Doubao (ByteDance)",
    },
    LLMProvider.BAICHUAN: {
        "base_url": "https://api.baichuan-ai.com/v1",
        "default_model": "Baichuan4-Turbo",
        "label": "Baichuan",
    },
    LLMProvider.STEPFUN: {
        "base_url": "https://api.stepfun.com/v1",
        "default_model": "step-3.5-flash",
        "label": "StepFun",
    },
    LLMProvider.SENSETIME: {
        "base_url": "https://api.sensenova.cn/v1",
        "default_model": "SenseNova-6.7-Flash-Lite",
        "label": "SenseTime (SenseNova)",
    },
    LLMProvider.YI: {
        "base_url": "https://api.lingyiwanwu.com/v1",
        "default_model": "yi-lightning",
        "label": "01.AI (Yi)",
    },
    LLMProvider.CUSTOM: {
        "base_url": "",
        "default_model": "",
        "label": "Custom",
    },
}


class FallbackProviderConfig(BaseModel):
    """Configuration for a fallback LLM provider."""

    name: str = Field(description="Provider identifier (e.g. 'openrouter', 'nvidia')")
    api_key: str = Field(description="API key for this fallback provider")
    api_keys: list[str] = Field(
        default_factory=list,
        description="Additional API keys for round-robin rotation",
    )
    base_url: str = Field(description="OpenAI-compatible API base URL")
    model: str = Field(
        default="",
        description="Model to use (empty = same as primary)",
    )
    priority: int = Field(
        default=1,
        description="Priority order: lower value = tried first",
    )


class ModelPoolEntry(BaseModel):
    """A single model in the cooperative pool."""
    name: str = Field(description="Human-readable name for this model")
    provider: str = Field(description="Provider: nvidia, openrouter, etc.")
    model: str = Field(description="Full model ID (e.g. deepseek-ai/deepseek-v4-pro)")
    role: str = Field(default="fallback", description="Role: primary, secondary, fast, fallback")
    tier: int = Field(default=99, description="Priority tier (1=highest, tried first)")
    enabled: bool = Field(default=True, description="Whether this model is active in the pool")
    api_key_env: str = Field(default="", description="Env var name that holds the API key")
    base_url: str = Field(default="", description="API base URL for this model")


class TEEConfig(BaseModel):
    """Trusted Execution Environment (TEE) & Privacy Protection configuration."""

    enabled: bool = Field(
        default=False,
        description="Whether TEE & Privacy protection is active for API calls",
    )
    mode: str = Field(
        default="zero_training",
        description="TEE privacy mode: zero_training, confidential_proxy, or attestation_enclave",
    )
    proxy_url: str = Field(
        default="",
        description="API base URL of confidential TEE enclave proxy / relay",
    )
    attestation_token: str = Field(
        default="",
        description="Hardware attestation token/header for TEE enclave verification",
    )
    zero_data_retention: bool = Field(
        default=True,
        description="Enforce zero-data-retention (ZDR) anti-training headers on all LLM requests",
    )
    anonymize_sensitive_data: bool = Field(
        default=False,
        description="Sanitize credentials, tokens, and private infrastructure IPs before sending to API",
    )


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: str = Field(
        default="nvidia",
        description="LLM provider name (nvidia/openrouter/openai/minimax/deepseek/zhipu/moonshot/qwen/siliconflow/doubao/baichuan/stepfun/sensetime/yi/custom)",
    )
    api_key: str = Field(default="", description="API key for the chosen provider")
    base_url: str = Field(
        default="https://integrate.api.nvidia.com/v1",
        description="OpenAI-compatible API base URL (auto-filled by provider)",
    )
    model: str = Field(default="z-ai/glm-5.2", description="Model name to use (auto-filled by provider)")
    max_tokens: int = Field(default=4096, description="Max tokens per response")
    max_context_tokens: int = Field(
        default=128000, description="Max context window tokens before sliding-window truncation"
    )
    temperature: float = Field(default=0.1, description="Sampling temperature")
    reasoning_effort: str = Field(
        default="high", description="Reasoning effort level (OpenAI o-series only)"
    )
    fallback_providers: list[FallbackProviderConfig] = Field(
        default_factory=list,
        description="Ordered list of fallback providers for automatic failover",
    )
    model_pool: list[ModelPoolEntry] = Field(
        default_factory=list,
        description="Cooperative model pool — multiple models with roles and tiers",
    )
    tee: TEEConfig = Field(
        default_factory=TEEConfig,
        description="Trusted Execution Environment & Privacy configuration",
    )


class MCPTransportConfig(BaseModel):
    """MCP server transport configuration."""

    type: str = Field(description="Transport type: stdio, sse, streamable-http")
    command: str | None = Field(default=None, description="Command to start the server (stdio)")
    args: list[str] | None = Field(default=None, description="Command arguments")
    url: str | None = Field(default=None, description="Server URL (sse / streamable-http)")
    env: dict[str, str] | None = Field(
        default=None, description="Environment variables (stdio) / HTTP headers (streamable-http)"
    )
    startup_timeout: int = Field(default=30000, description="Startup timeout in ms")
    tool_timeout: int = Field(default=300000, description="Tool call timeout in ms")


class MCPServerConfig(BaseModel):
    """Single MCP server configuration."""

    name: str = Field(description="Server identifier")
    enabled: bool = Field(default=True, description="Whether to auto-start this server")
    priority: int = Field(default=1, description="Priority: 0=critical, 1=normal, 2=optional")
    transport: MCPTransportConfig = Field(description="Transport configuration")
    description: str = Field(default="", description="Human-readable description")


class MCPServersConfig(BaseModel):
    """All MCP servers configuration."""

    servers: dict[str, MCPServerConfig] = Field(default_factory=dict)


class ReconConfig(BaseModel):
    """Information-gathering configuration: space-mapping API keys + recon knobs.

    Keys are read here OR from environment variables (FOFA_KEY, HUNTER_KEY,
    QUAKE_KEY, ZOOMEYE_KEY, SHODAN_KEY, ZEROZONE_KEY) — never hard-coded. Put real
    keys in ~/.bughunter/config.yaml (gitignored), not in source.
    """

    fofa_email: str = Field(default="", description="FOFA account email")
    fofa_key: str = Field(default="", description="FOFA API key")
    hunter_key: str = Field(default="", description="Hunter (Qi'an Xin Eagle Picture) API key")
    quake_key: str = Field(default="", description="Quake (360) API token")
    zoomeye_key: str = Field(default="", description="ZoomEye (Zhong Kui's Eye) API key")
    shodan_key: str = Field(default="", description="Shodan API key")
    zerozone_key: str = Field(default="", description="Zero Zero Security 0.zone API key")
    http_timeout: float = Field(default=15.0, description="Per-request HTTP timeout (s)")
    max_concurrency: int = Field(default=20, description="Max concurrent recon requests")
    space_size: int = Field(default=100, description="Default result size per space-mapping query")
    dir_wordlist_path: str = Field(
        default="", description="Optional path to a custom directory-bruteforce wordlist"
    )
    dir_max_requests: int = Field(
        default=1500, description="Hard cap on requests per directory-enumeration call"
    )
    js_max_files: int = Field(
        default=30, description="Max JavaScript files fetched per js_recon call"
    )


class SafetyConfig(BaseModel):
    """Safety / sandbox configuration."""

    enable_python_execute: bool = Field(
        default=True,
        description="Enable the python_execute built-in tool (disable for safer runs)",
    )
    python_execute_restricted: bool = Field(
        default=False,
        description="Restricted mode: block file I/O and network in python_execute",
    )
    python_execute_mode: str = Field(
        default="trusted-local",
        description="Execution mode for python_execute: safe, lab, trusted-local",
    )
    python_execute_max_lines: int = Field(
        default=900,
        description="Max lines of code allowed per python_execute call",
    )
    python_execute_show_warning: bool = Field(
        default=True,
        description="Show a security warning before each python_execute invocation",
    )
    python_execute_max_output_chars: int = Field(
        default=8000,
        description="Max stdout/stderr characters returned from a python_execute call",
    )
    python_execute_audit_enabled: bool = Field(
        default=True,
        description="Write python_execute audit records to the local config directory",
    )
    tool_parallel: bool = Field(
        default=True,
        description="Execute independent tool calls in a single LLM turn concurrently",
    )
    tool_max_concurrent: int = Field(
        default=5,
        description="Max number of tool calls executed concurrently per round (1=serial)",
    )
    sandbox_auto_start: bool = Field(
        default=True,
        description="Automatically start Kali Linux sandbox when REPL/TUI launches (requires Docker)",
    )


class SessionConfig(BaseModel):
    """Session / output configuration."""

    output_dir: Path = Field(default=Path("./bughunter-output"), description="Output directory")
    auto_save: bool = Field(default=True, description="Auto-save session state")
    report_format: str = Field(
        default="markdown", description="Default report format: markdown, html"
    )
    poc_language: str = Field(default="python", description="Default PoC language: python, bash")
    max_rounds: int = Field(default=15, description="Max autonomous pentest rounds (1-100)")
    # Autonomous engine: "solve" = goal-driven OODA (default), "rounds" = legacy fixed-round loop
    engine: str = Field(
        default="solve", description="Autonomous engine: solve (goal-driven) or rounds (legacy)"
    )
    # Solve-engine knobs
    solve_max_steps: int = Field(
        default=40, description="Safety cap on solve explore steps (not a fixed workflow length)"
    )
    solve_max_intents: int = Field(default=3, description="Max new intents per reason step")
    solve_max_tool_rounds: int = Field(
        default=6, description="Max tool-calling rounds per intent exploration"
    )
    solve_max_parallel: int = Field(
        default=3, description="Max intents explored concurrently per solve batch (1=serial)"
    )
    show_thinking: bool = Field(
        default=True, description="Show LLM thinking/reasoning output (default: on)"
    )
    # Dead-loop detection
    stale_rounds_threshold: int = Field(
        default=5,
        description="Consecutive rounds without progress before dead-loop warning (1-50)",
    )
    # Persistent pentest configuration
    persistent_rounds_per_cycle: int = Field(
        default=100, description="Rounds per persistent pentest cycle"
    )
    persistent_max_cycles: int = Field(
        default=10, description="Max cycles for persistent pentest (0=unlimited)"
    )
    persistent_auto_report: bool = Field(
        default=True, description="Auto-generate report after each cycle"
    )
    # Language configuration
    language: str = Field(
        default="auto", description="UI language: auto, zh, en"
    )
    reasoning_state_enabled: bool = Field(
        default=True, description="Enable reasoning state tracking"
    )
    reflexion_enabled: bool = Field(
        default=True, description="Enable reflexion feedback loop"
    )
    reflexion_max_same_vuln_fails: int = Field(
        default=2, description="Max repeated failures for the same vulnerability"
    )
    reflexion_max_total_no_progress: int = Field(
        default=5, description="Max total rounds without progress before reflexion"
    )
    escalation_max_level: int = Field(
        default=4, description="Max escalation level"
    )
    plugin_runtime_enabled: bool = Field(
        default=True, description="Enable plugin runtime"
    )
    plugin_default_timeout: int = Field(
        default=10, description="Default plugin timeout in seconds"
    )
    plugin_max_requests_per_target: int = Field(
        default=30, description="Max plugin requests per target"
    )
    evidence_min_report_level: str = Field(
        default="L4", description="Minimum evidence level for report inclusion"
    )
    # Time-budgeted scan settings
    scan_time_budget: int = Field(
        default=0,
        description="Total scan time budget in minutes (0=unlimited, recommended: 10-60)",
    )
    scan_tool_timeout_quick: int = Field(
        default=30, description="Max seconds per tool in quick recon phase"
    )
    scan_tool_timeout_standard: int = Field(
        default=120, description="Max seconds per tool in standard scan phase"
    )
    scan_tool_timeout_deep: int = Field(
        default=180, description="Max seconds per tool in deep exploitation phase"
    )
    # Sub-agent orchestration settings
    max_subagents: int = Field(
        default=3,
        description="Max concurrent sub-agents (1-10). Main agent can request more if needed.",
    )
    subagent_max_steps: int = Field(
        default=25,
        description="Max solve steps per sub-agent task (safety cap)",
    )
    subagent_max_tool_rounds: int = Field(
        default=10,
        description="Max tool-calling rounds per sub-agent intent",
    )

class BugHunterConfig(BaseModel):
    """Top-level Bug Hunter configuration."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    mcp: MCPServersConfig = Field(default_factory=MCPServersConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    recon: ReconConfig = Field(default_factory=ReconConfig)

    model_config = ConfigDict(
        env_prefix="BUGHUNTER_",
        env_nested_delimiter="__",
    )


# ── Built-in MCP server definitions (MVP) ──────────────────────────

BUILTIN_MCP_SERVERS: dict[str, dict[str, Any]] = {
    "fetch": {
        "name": "fetch",
        "enabled": True,
        "priority": 0,
        "description": "HTTP request tool for API testing & web interaction",
        "transport": {
            "type": "stdio",
            "command": "uvx",
            "args": ["mcp-server-fetch"],
        },
    },
    "memory": {
        "name": "memory",
        "enabled": True,
        "priority": 0,
        "description": "Context memory & session state persistence",
        "transport": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"],
        },
    },
    "chrome-devtools": {
        "name": "chrome-devtools",
        "enabled": False,
        "priority": 0,
        "description": "Browser automation for Web app pentest",
        "transport": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "chrome-devtools-mcp@latest"],
        },
    },
    "burp": {
        "name": "burp",
        "enabled": False,
        "priority": 0,
        "description": "Burp Suite proxy integration for HTTP interception via SSE",
        "transport": {
            "type": "sse",
            "url": "http://127.0.0.1:9876",
        },
    },
}
