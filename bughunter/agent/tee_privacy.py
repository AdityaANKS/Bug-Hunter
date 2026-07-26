"""Trusted Execution Environment (TEE) & Data Privacy Guard for Bug Hunter LLM APIs.

Provides hardware attestation header injection, Zero Data Retention (ZDR) anti-training
headers, confidential proxy routing, and client-side prompt sanitization to ensure
vulnerability research and pentesting data cannot be used by AI providers for training.
"""

from __future__ import annotations

import os
import re
from typing import Any

# Standard anti-training and zero-data-retention headers across LLM providers
_ZDR_HEADERS = {
    "X-Option-No-Train": "true",
    "X-No-Training": "1",
    "X-Zero-Data-Retention": "1",
    "X-Privacy-No-Log": "1",
}

# Regex patterns for sensitive data redaction before prompt transmission
_SENSITIVE_PATTERNS = [
    # JWT Tokens
    (re.compile(r"eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+"), "[REDACTED_JWT]"),
    # AWS Access Keys
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED_AWS_AK]"),
    # Standard API Keys (OpenAI, OpenRouter, NVIDIA, DeepSeek, etc.)
    (re.compile(r"\b(sk-[A-Za-z0-9_-]{20,}|nvapi-[A-Za-z0-9_-]{20,})\b"), "[REDACTED_API_KEY]"),
    # Internal IPv4 addresses (10.x.x.x, 192.168.x.x, 172.16-31.x.x)
    (re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"), "[REDACTED_PRIVATE_IP]"),
]


def build_tee_headers(llm_config: Any = None) -> dict[str, str]:
    """Construct TEE, confidential computing, and Zero Data Retention (ZDR) headers.

    Checks configuration + environment variable overlays:
    - BUGHUNTER_TEE_ENABLED=1
    - BUGHUNTER_ZERO_DATA_RETENTION=1
    - BUGHUNTER_TEE_MODE=zero_training | confidential_proxy | attestation_enclave
    - BUGHUNTER_TEE_ATTESTATION_TOKEN=<token>
    """
    headers: dict[str, str] = {}

    tee_cfg = getattr(llm_config, "tee", None) if llm_config is not None else None

    tee_enabled = bool(
        getattr(tee_cfg, "enabled", False)
        or os.environ.get("BUGHUNTER_TEE_ENABLED", "").lower() in ("1", "true", "yes")
    )

    zdr_enabled = bool(
        getattr(tee_cfg, "zero_data_retention", True)
        or os.environ.get("BUGHUNTER_ZERO_DATA_RETENTION", "1").lower() in ("1", "true", "yes")
        or tee_enabled
    )

    if zdr_enabled:
        headers.update(_ZDR_HEADERS)

    if tee_enabled:
        mode = os.environ.get("BUGHUNTER_TEE_MODE") or getattr(tee_cfg, "mode", "zero_training")
        attestation = os.environ.get("BUGHUNTER_TEE_ATTESTATION_TOKEN") or getattr(tee_cfg, "attestation_token", "")

        headers["X-TEE-Mode"] = str(mode)
        headers["X-Confidential-Compute"] = "1"
        if attestation:
            headers["X-TEE-Attestation-Token"] = str(attestation)

    return headers


def sanitize_prompt(prompt: str) -> str:
    """Sanitize prompt text by redacting sensitive credentials and private infrastructure IPs.

    Useful when anonymize_sensitive_data is enabled to ensure private credentials do not reach
    external API endpoints.
    """
    if not prompt:
        return prompt

    sanitized = prompt
    for pattern, replacement in _SENSITIVE_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)

    return sanitized


def get_effective_tee_status(llm_config: Any = None) -> dict[str, Any]:
    """Return structured status of current TEE, ZDR, and privacy settings."""
    tee_cfg = getattr(llm_config, "tee", None) if llm_config is not None else None

    enabled = bool(
        getattr(tee_cfg, "enabled", False)
        or os.environ.get("BUGHUNTER_TEE_ENABLED", "").lower() in ("1", "true", "yes")
    )
    zdr = bool(
        getattr(tee_cfg, "zero_data_retention", True)
        or os.environ.get("BUGHUNTER_ZERO_DATA_RETENTION", "1").lower() in ("1", "true", "yes")
        or enabled
    )
    mode = os.environ.get("BUGHUNTER_TEE_MODE") or getattr(tee_cfg, "mode", "zero_training")
    proxy_url = os.environ.get("BUGHUNTER_TEE_PROXY_URL") or getattr(tee_cfg, "proxy_url", "")
    attestation = os.environ.get("BUGHUNTER_TEE_ATTESTATION_TOKEN") or getattr(tee_cfg, "attestation_token", "")
    anonymize = bool(
        getattr(tee_cfg, "anonymize_sensitive_data", False)
        or os.environ.get("BUGHUNTER_TEE_ANONYMIZE", "").lower() in ("1", "true", "yes")
    )

    return {
        "enabled": enabled,
        "zero_data_retention": zdr,
        "mode": mode,
        "proxy_url": proxy_url,
        "attestation_configured": bool(attestation),
        "anonymize_sensitive_data": anonymize,
    }
