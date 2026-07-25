"""Bug Hunter configuration management — load, save, and access settings.

Built on the Bug Hunter engine.
"""

from __future__ import annotations

import os
from contextlib import suppress
from pathlib import Path
from typing import Any

# Load .env file if present (before any env var reads)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
except ImportError:
    pass

import yaml
from pydantic import ValidationError

from .schema import (
    BUILTIN_MCP_SERVERS,
    PROVIDER_PRESETS,
    BugHunterConfig,
    FallbackProviderConfig,
    LLMProvider,
    MCPServerConfig,
    MCPServersConfig,
    MCPTransportConfig,
    ModelPoolEntry,
)

# ── Paths ──────────────────────────────────────────────────────────

CONFIG_DIR = Path(os.environ.get("BUGHUNTER_CONFIG_DIR", str(Path.home() / ".bughunter")))
CONFIG_FILE = CONFIG_DIR / "config.yaml"
SESSIONS_DIR = CONFIG_DIR / "sessions"
TARGETS_DIR = CONFIG_DIR / "targets"
KB_DIR = CONFIG_DIR / "kb"
SKILLS_DIR = CONFIG_DIR / "skills"
WEB_TASKS_FILE = CONFIG_DIR / "web_tasks.json"
SANDBOX_SESSIONS_FILE = CONFIG_DIR / "sandbox_sessions.json"
PYTHON_EXECUTE_AUDIT_FILE = CONFIG_DIR / "python_execute_audit.jsonl"
DEFAULT_OPENAI_USER_AGENT = "Mozilla/5.0"


def ensure_dirs() -> None:
    """Create Bug Hunter config directories if they don't exist."""
    for d in [CONFIG_DIR, SESSIONS_DIR, TARGETS_DIR, KB_DIR, SKILLS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def openai_default_headers() -> dict[str, str]:
    return {"User-Agent": os.environ.get("BUGHUNTER_LLM_USER_AGENT", DEFAULT_OPENAI_USER_AGENT)}


def make_openai_client(api_key: str, base_url: str, timeout: float | None = None):
    from openai import OpenAI

    kwargs: dict[str, Any] = {
        "api_key": api_key,
        "base_url": base_url,
        "default_headers": openai_default_headers(),
    }
    if timeout is not None:
        kwargs["timeout"] = timeout
    return OpenAI(**kwargs)


# ── Load / Save ────────────────────────────────────────────────────


def load_config() -> BugHunterConfig:
    """Load configuration from file + env vars.

    Priority: env vars > config file > built-in defaults.
    """
    ensure_dirs()

    # Start with built-in defaults + registered MCP servers
    servers: dict[str, MCPServerConfig] = {}
    for name, cfg in BUILTIN_MCP_SERVERS.items():
        servers[name] = _parse_mcp_server(name, cfg)

    config = BugHunterConfig(mcp=MCPServersConfig(servers=servers))

    # Overlay from config file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
            config = _merge_config(config, raw)
        except (yaml.YAMLError, ValidationError) as e:
            # Log warning but don't crash
            print(f"[!] Warning: Failed to parse config file {CONFIG_FILE}: {e}")

    # Overlay from env vars
    config = _overlay_env(config)

    return config


def save_config(config: BugHunterConfig) -> None:
    """Save configuration to YAML file."""
    ensure_dirs()
    raw = config.model_dump(mode="json")
    # Remove default values to keep config clean
    _strip_defaults(raw)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(raw, f, default_flow_style=False, allow_unicode=True)


def set_config_value(key: str, value: str) -> None:
    """Set a nested config value using dot notation.

    Example: set_config_value("llm.api_key", "sk-xxx")
    """
    config = load_config()
    parts = key.split(".")
    obj: Any = config
    for part in parts[:-1]:
        obj = obj[part] if isinstance(obj, dict) else getattr(obj, part)
    field_name = parts[-1]

    # Type coercion based on field annotation
    model_fields = getattr(type(obj), "model_fields", {})
    if field_name in model_fields:
        field_info = model_fields[field_name]
        annotation = field_info.annotation
        if annotation is int:
            value = int(value)
        elif annotation is float:
            value = float(value)
        elif annotation is bool:
            value = value.lower() in ("true", "1", "yes")

    if isinstance(obj, dict):
        obj[field_name] = value
    else:
        setattr(obj, field_name, value)
    save_config(config)


# ── Helpers ─────────────────────────────────────────────────────────


def _parse_mcp_server(name: str, raw: dict[str, Any]) -> MCPServerConfig:
    """Parse a raw dict into MCPServerConfig."""
    transport_raw = raw.get("transport", {})
    return MCPServerConfig(
        name=raw.get("name", name),
        enabled=raw.get("enabled", True),
        priority=raw.get("priority", 1),
        description=raw.get("description", ""),
        transport=MCPTransportConfig(
            type=transport_raw.get("type", "stdio"),
            command=transport_raw.get("command"),
            args=transport_raw.get("args"),
            url=transport_raw.get("url"),
            env=transport_raw.get("env"),
            startup_timeout=transport_raw.get("startup_timeout", 30000),
            tool_timeout=transport_raw.get("tool_timeout", 300000),
        ),
    )


def _merge_config(base: BugHunterConfig, raw: dict[str, Any]) -> BugHunterConfig:
    """Merge raw dict into existing config, preserving unset defaults."""
    data = base.model_dump(mode="json")

    # Deep merge
    _deep_merge(data, raw)

    try:
        return BugHunterConfig(**data)
    except ValidationError:
        # If merged data is invalid, return base
        return base


def _deep_merge(base: dict, override: dict) -> None:
    """Recursively merge override into base (mutates base)."""
    for key, val in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(val, dict):
            _deep_merge(base[key], val)
        else:
            base[key] = val


def _overlay_env(config: BugHunterConfig) -> BugHunterConfig:
    """Overlay environment variables onto config.

    Supported env var prefixes (checked in order): BUGHUNTER_, BUGHUNTER_
        LLM:        API_KEY, BASE_URL, MODEL, PROVIDER, MAX_TOKENS, MAX_CONTEXT_TOKENS, TEMPERATURE
        Session:    OUTPUT_DIR, AUTO_SAVE, REPORT_FORMAT, MAX_ROUNDS, SHOW_THINKING
        Safety:     PYTHON_EXECUTE_ENABLED, PYTHON_EXECUTE_RESTRICTED, PYTHON_EXECUTE_MODE,
                    PYTHON_EXECUTE_MAX_LINES, PYTHON_EXECUTE_SHOW_WARNING,
                    PYTHON_EXECUTE_MAX_OUTPUT_CHARS, PYTHON_EXECUTE_AUDIT_ENABLED
    """

    def _env(suffix: str) -> str | None:
        """Check BUGHUNTER_ prefix first, then BUGHUNTER_ fallback."""
        return os.environ.get(f"BUGHUNTER_{suffix}") or os.environ.get(f"BUGHUNTER_{suffix}")

    # ── LLM ──────────────────────────────────────────────────────────
    if v := _env("LLM_API_KEY"):
        config.llm.api_key = v
    if v := _env("LLM_BASE_URL"):
        config.llm.base_url = v
    if v := _env("LLM_MODEL"):
        config.llm.model = v
    if v := _env("LLM_PROVIDER"):
        config.llm.provider = v
    if v := _env("LLM_MAX_TOKENS"):
        with suppress(ValueError):
            config.llm.max_tokens = int(v)
    if v := _env("LLM_MAX_CONTEXT_TOKENS"):
        with suppress(ValueError):
            config.llm.max_context_tokens = int(v)
    if v := _env("LLM_TEMPERATURE"):
        with suppress(ValueError):
            config.llm.temperature = float(v)

    # ── Session ──────────────────────────────────────────────────────
    if v := _env("SESSION_OUTPUT_DIR"):
        config.session.output_dir = Path(v)
    if v := _env("SESSION_AUTO_SAVE"):
        config.session.auto_save = v.lower() in ("1", "true", "yes", "on")
    if v := _env("SESSION_REPORT_FORMAT"):
        config.session.report_format = v
    if v := _env("SESSION_MAX_ROUNDS"):
        with suppress(ValueError):
            config.session.max_rounds = int(v)
    if v := _env("SESSION_SHOW_THINKING"):
        config.session.show_thinking = v.lower() in ("1", "true", "yes", "on")
    if v := _env("SESSION_STALE_ROUNDS_THRESHOLD"):
        with suppress(ValueError):
            config.session.stale_rounds_threshold = int(v)

    # ── Session: Reasoning state / Reflection engine / Plugin runtime ──────────────
    _truthy = ("1", "true", "yes", "on")
    if v := _env("SESSION_REASONING_STATE_ENABLED"):
        config.session.reasoning_state_enabled = v.lower() in _truthy
    if v := _env("SESSION_REFLEXION_ENABLED"):
        config.session.reflexion_enabled = v.lower() in _truthy
    if v := _env("SESSION_REFLEXION_MAX_SAME_VULN_FAILS"):
        with suppress(ValueError):
            config.session.reflexion_max_same_vuln_fails = int(v)
    if v := _env("SESSION_REFLEXION_MAX_TOTAL_NO_PROGRESS"):
        with suppress(ValueError):
            config.session.reflexion_max_total_no_progress = int(v)
    if v := _env("SESSION_ESCALATION_MAX_LEVEL"):
        with suppress(ValueError):
            config.session.escalation_max_level = int(v)
    if v := _env("SESSION_PLUGIN_RUNTIME_ENABLED"):
        config.session.plugin_runtime_enabled = v.lower() in _truthy
    if v := _env("SESSION_PLUGIN_DEFAULT_TIMEOUT"):
        with suppress(ValueError):
            config.session.plugin_default_timeout = int(v)
    if v := _env("SESSION_PLUGIN_MAX_REQUESTS_PER_TARGET"):
        with suppress(ValueError):
            config.session.plugin_max_requests_per_target = int(v)
    if v := _env("SESSION_EVIDENCE_MIN_REPORT_LEVEL"):
        config.session.evidence_min_report_level = v

    # ── Safety ───────────────────────────────────────────────────────
    if v := _env("SAFETY_PYTHON_EXECUTE_ENABLED"):
        config.safety.enable_python_execute = v.lower() in ("1", "true", "yes", "on")
    if v := _env("SAFETY_PYTHON_EXECUTE_RESTRICTED"):
        config.safety.python_execute_restricted = v.lower() in ("1", "true", "yes", "on")
    if v := _env("SAFETY_PYTHON_EXECUTE_MODE"):
        config.safety.python_execute_mode = v
    if v := _env("SAFETY_PYTHON_EXECUTE_MAX_LINES"):
        with suppress(ValueError):
            config.safety.python_execute_max_lines = int(v)
    if v := _env("SAFETY_PYTHON_EXECUTE_SHOW_WARNING"):
        config.safety.python_execute_show_warning = v.lower() in ("1", "true", "yes", "on")
    if v := _env("SAFETY_PYTHON_EXECUTE_MAX_OUTPUT_CHARS"):
        with suppress(ValueError):
            config.safety.python_execute_max_output_chars = int(v)
    if v := _env("SAFETY_PYTHON_EXECUTE_AUDIT_ENABLED"):
        config.safety.python_execute_audit_enabled = v.lower() in ("1", "true", "yes", "on")

    # ── Recon: space-mapping API keys ────────────────────────────────
    # Accept short form (FOFA_KEY), BUGHUNTER_ prefix, and BUGHUNTER_ prefix;
    # short form wins if multiple are set.
    for field, names in {
        "fofa_email": ("FOFA_EMAIL", "BUGHUNTER_RECON_FOFA_EMAIL", "BUGHUNTER_RECON_FOFA_EMAIL"),
        "fofa_key": ("FOFA_KEY", "BUGHUNTER_RECON_FOFA_KEY", "BUGHUNTER_RECON_FOFA_KEY"),
        "hunter_key": ("HUNTER_KEY", "BUGHUNTER_RECON_HUNTER_KEY", "BUGHUNTER_RECON_HUNTER_KEY"),
        "quake_key": ("QUAKE_KEY", "BUGHUNTER_RECON_QUAKE_KEY", "BUGHUNTER_RECON_QUAKE_KEY"),
        "zoomeye_key": ("ZOOMEYE_KEY", "BUGHUNTER_RECON_ZOOMEYE_KEY", "BUGHUNTER_RECON_ZOOMEYE_KEY"),
        "shodan_key": ("SHODAN_KEY", "BUGHUNTER_RECON_SHODAN_KEY", "BUGHUNTER_RECON_SHODAN_KEY"),
        "zerozone_key": ("ZEROZONE_KEY", "BUGHUNTER_RECON_ZEROZONE_KEY", "BUGHUNTER_RECON_ZEROZONE_KEY"),
    }.items():
        for env_name in names:
            if v := os.environ.get(env_name):
                setattr(config.recon, field, v)
                break

    # ── Fallback providers: auto-detect from env vars ────────────────
    # Only auto-build if no fallback providers were loaded from config file
    if not config.llm.fallback_providers:
        _auto_fallbacks: list[FallbackProviderConfig] = []

        # Detect OpenRouter keys
        or_key = os.environ.get("OPENROUTER_API_KEY", "")
        or_key1 = os.environ.get("OPENROUTER_API_KEY1", "")
        if or_key:
            extra_keys = [or_key1] if or_key1 else []
            _auto_fallbacks.append(FallbackProviderConfig(
                name="openrouter",
                api_key=or_key,
                api_keys=extra_keys,
                base_url="https://openrouter.ai/api/v1",
                model="",  # use same model as primary
                priority=1,
            ))

        # Detect NVIDIA key (as fallback when primary is NOT NVIDIA)
        nvidia_key = os.environ.get("NVIDIA_API_KEY", "")
        primary_is_nvidia = (
            "nvidia" in config.llm.base_url.lower()
            or config.llm.provider == "nvidia"
        )
        if nvidia_key and not primary_is_nvidia:
            _auto_fallbacks.append(FallbackProviderConfig(
                name="nvidia",
                api_key=nvidia_key,
                base_url="https://integrate.api.nvidia.com/v1",
                model="",
                priority=2,
            ))

        # Sort by priority and assign
        _auto_fallbacks.sort(key=lambda fb: fb.priority)
        config.llm.fallback_providers = _auto_fallbacks

    # ── Model Pool: auto-build cooperative pool from env vars ────────
    if not config.llm.model_pool:
        _pool: list[ModelPoolEntry] = []

        # NVIDIA models (via NVIDIA_API_KEY)
        nvidia_key_val = os.environ.get("NVIDIA_API_KEY", "")
        if nvidia_key_val:
            nvidia_base = "https://integrate.api.nvidia.com/v1"
            _pool.extend([
                ModelPoolEntry(
                    name="GLM 5.2",
                    provider="nvidia",
                    model="z-ai/glm-5.2",
                    role="primary",
                    tier=1,
                    api_key_env="NVIDIA_API_KEY",
                    base_url=nvidia_base,
                ),
                ModelPoolEntry(
                    name="DeepSeek V4 Pro",
                    provider="nvidia",
                    model="deepseek-ai/deepseek-v4-pro",
                    role="secondary",
                    tier=2,
                    api_key_env="NVIDIA_API_KEY",
                    base_url=nvidia_base,
                ),
                ModelPoolEntry(
                    name="Kimi K2.6",
                    provider="nvidia",
                    model="moonshotai/kimi-k2.6",
                    role="secondary",
                    tier=3,
                    api_key_env="NVIDIA_API_KEY",
                    base_url=nvidia_base,
                ),
                ModelPoolEntry(
                    name="MiniMax M3",
                    provider="nvidia",
                    model="minimaxai/minimax-m3",
                    role="secondary",
                    tier=4,
                    api_key_env="NVIDIA_API_KEY",
                    base_url=nvidia_base,
                ),
                ModelPoolEntry(
                    name="Mistral Medium 3.5",
                    provider="nvidia",
                    model="mistralai/mistral-medium-3.5-128k",
                    role="fast",
                    tier=5,
                    api_key_env="NVIDIA_API_KEY",
                    base_url=nvidia_base,
                ),
            ])

        # OpenRouter models (via OPENROUTER_API_KEY)
        or_key_val = os.environ.get("OPENROUTER_API_KEY", "")
        if or_key_val:
            or_base = "https://openrouter.ai/api/v1"
            _pool.extend([
                ModelPoolEntry(
                    name="Nemotron Ultra 550B",
                    provider="openrouter",
                    model="nvidia/nemotron-3-ultra-550b-a55b:free",
                    role="fallback",
                    tier=10,
                    api_key_env="OPENROUTER_API_KEY",
                    base_url=or_base,
                ),
                ModelPoolEntry(
                    name="GPT-OSS 120B",
                    provider="openrouter",
                    model="openai/gpt-oss-120b:free",
                    role="fallback",
                    tier=11,
                    api_key_env="OPENROUTER_API_KEY",
                    base_url=or_base,
                ),
                ModelPoolEntry(
                    name="Poolside Laguna",
                    provider="openrouter",
                    model="poolside/laguna-m.1:free",
                    role="fallback",
                    tier=12,
                    api_key_env="OPENROUTER_API_KEY",
                    base_url=or_base,
                ),
            ])

        _pool.sort(key=lambda entry: entry.tier)
        config.llm.model_pool = _pool

        # Set primary model from pool tier-1 entry
        if _pool:
            primary = _pool[0]
            config.llm.model = primary.model
            if primary.base_url:
                config.llm.base_url = primary.base_url
            env_key = os.environ.get(primary.api_key_env, "")
            if env_key:
                config.llm.api_key = env_key

    return config


def _strip_defaults(raw: dict) -> None:
    """Remove fields that match defaults to keep config file clean."""
    # Keep it simple — just strip known default values
    if raw.get("llm", {}).get("api_key") == "":
        raw["llm"].pop("api_key", None)
    # Don't strip base_url/model if provider is set — they may be provider-specific
    # Only strip if still at NVIDIA defaults (the new built-in default)
    if raw.get("llm", {}).get("provider") in ("nvidia", "openai"):
        if raw.get("llm", {}).get("base_url") in (
            "https://integrate.api.nvidia.com/v1",
            "https://api.openai.com/v1",
        ):
            raw["llm"].pop("base_url", None)
        if raw.get("llm", {}).get("model") in ("minimaxai/minimax-m3", "deepseek-ai/deepseek-v4-pro", "z-ai/glm-5.2", "gpt-4o"):
            raw["llm"].pop("model", None)
    # Strip auto-detected fallback providers (they are rebuilt from env each time)
    raw.get("llm", {}).pop("fallback_providers", None)
    raw.get("llm", {}).pop("model_pool", None)


# ── Provider Management ─────────────────────────────────────────────


def apply_provider_preset(config: BugHunterConfig, provider_name: str) -> BugHunterConfig:
    """Apply a provider preset, auto-filling base_url and model.

    Only fills fields that haven't been explicitly changed from the previous
    provider's defaults. This way, if the user manually set a model, we don't
    overwrite it unless the provider itself changed.
    """
    # Resolve provider enum
    try:
        provider = LLMProvider(provider_name.lower())
    except ValueError:
        # Unknown provider — treat as custom, don't auto-fill
        config.llm.provider = provider_name
        return config

    preset = PROVIDER_PRESETS.get(provider)
    if not preset:
        return config

    old_provider = config.llm.provider
    config.llm.provider = provider.value

    # Auto-fill base_url and model only when switching providers
    # (or when they still match the old provider's defaults)
    old_preset = PROVIDER_PRESETS.get(LLMProvider(old_provider)) if old_provider else None

    # Fill base_url: always fill from preset on provider switch
    if preset.get("base_url"):
        config.llm.base_url = preset["base_url"]

    # Fill model: fill from preset unless user has a custom model set
    # that doesn't match the old provider's default
    if old_preset and config.llm.model != old_preset.get("default_model", ""):
        # User has a custom model, keep it
        pass
    elif preset.get("default_model"):
        config.llm.model = preset["default_model"]

    return config


def list_providers() -> list[dict[str, str]]:
    """Return all available provider presets as a list of dicts."""
    result = []
    for provider, preset in PROVIDER_PRESETS.items():
        result.append(
            {
                "provider": provider.value,
                "label": preset.get("label", provider.value),
                "base_url": preset.get("base_url", ""),
                "default_model": preset.get("default_model", ""),
            }
        )
    return result


def fetch_provider_models(base_url: str, api_key: str, timeout: float = 10.0) -> list[str]:
    """Fetch available models from a provider's OpenAI-compatible API.

    Uses the OpenAI SDK's ``client.models.list()`` endpoint.
    Returns a sorted list of model ID strings.  Returns an empty list
    on any error (network, auth, timeout, etc.).
    """
    if not base_url or not api_key:
        return []
    try:
        client = make_openai_client(api_key=api_key, base_url=base_url, timeout=timeout)
        models_page = client.models.list()
        model_ids = [m.id for m in models_page if m.id]
        return sorted(model_ids)
    except Exception:
        return []


def fetch_provider_models_async(
    base_url: str,
    api_key: str,
    timeout: float = 10.0,
    on_result: Any = None,
):
    """Fetch provider models in a background thread.

    Calls ``fetch_provider_models()`` in a daemon thread.  When the
    fetch completes, *on_result* (if provided) is called with the
    model list on the **calling** thread via ``app.call_later()``-style
    scheduling — the caller is responsible for arranging thread-safe
    delivery (e.g. by passing a lambda that uses ``call_later``).

    Returns the ``Thread`` object so callers can track or join it.
    """
    import threading

    def _worker() -> None:
        models = fetch_provider_models(base_url, api_key, timeout)
        if on_result is not None:
            on_result(models)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return t
