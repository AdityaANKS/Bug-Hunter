"""Tests for Trusted Execution Environment (TEE), Zero Data Retention (ZDR), and Privacy Guard."""

import os
from unittest.mock import MagicMock

import pytest

from bughunter.agent.tee_privacy import (
    build_tee_headers,
    get_effective_tee_status,
    sanitize_prompt,
)
from bughunter.config.schema import BugHunterConfig, LLMConfig, TEEConfig
from bughunter.config.settings import make_openai_client, openai_default_headers


def test_tee_config_defaults():
    llm = LLMConfig()
    assert isinstance(llm.tee, TEEConfig)
    assert llm.tee.enabled is False
    assert llm.tee.zero_data_retention is True
    assert llm.tee.mode == "zero_training"
    assert llm.tee.proxy_url == ""
    assert llm.tee.attestation_token == ""
    assert llm.tee.anonymize_sensitive_data is False


def test_build_tee_headers_default():
    llm = LLMConfig()
    headers = build_tee_headers(llm)
    assert headers.get("X-Option-No-Train") == "true"
    assert headers.get("X-No-Training") == "1"
    assert headers.get("X-Zero-Data-Retention") == "1"
    assert headers.get("X-Privacy-No-Log") == "1"
    assert "X-TEE-Attestation-Token" not in headers


def test_build_tee_headers_enabled_with_attestation():
    llm = LLMConfig(
        tee=TEEConfig(
            enabled=True,
            mode="attestation_enclave",
            attestation_token="token-12345-xyz",
            zero_data_retention=True,
        )
    )
    headers = build_tee_headers(llm)
    assert headers.get("X-Option-No-Train") == "true"
    assert headers.get("X-TEE-Mode") == "attestation_enclave"
    assert headers.get("X-Confidential-Compute") == "1"
    assert headers.get("X-TEE-Attestation-Token") == "token-12345-xyz"


def test_build_tee_headers_env_override(monkeypatch):
    monkeypatch.setenv("BUGHUNTER_TEE_ENABLED", "1")
    monkeypatch.setenv("BUGHUNTER_TEE_MODE", "confidential_proxy")
    monkeypatch.setenv("BUGHUNTER_TEE_ATTESTATION_TOKEN", "env-attest-token")

    llm = LLMConfig()
    headers = build_tee_headers(llm)
    assert headers.get("X-TEE-Mode") == "confidential_proxy"
    assert headers.get("X-TEE-Attestation-Token") == "env-attest-token"

    status = get_effective_tee_status(llm)
    assert status["enabled"] is True
    assert status["mode"] == "confidential_proxy"
    assert status["attestation_configured"] is True


def test_sanitize_prompt_redacts_credentials_and_private_ips():
    raw_prompt = (
        "Target internal endpoint: http://192.168.1.50/api with token "
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature "
        "and AWS key AKIAIOSFODNN7EXAMPLE and OpenAI key sk-1234567890abcdef12345678"
    )
    sanitized = sanitize_prompt(raw_prompt)

    assert "192.168.1.50" not in sanitized
    assert "[REDACTED_PRIVATE_IP]" in sanitized
    assert "eyJhbGci" not in sanitized
    assert "[REDACTED_JWT]" in sanitized
    assert "AKIAIOSFODNN7EXAMPLE" not in sanitized
    assert "[REDACTED_AWS_AK]" in sanitized
    assert "sk-1234567890" not in sanitized
    assert "[REDACTED_API_KEY]" in sanitized


def test_make_openai_client_injects_tee_headers_and_proxy():
    llm = LLMConfig(
        provider="openrouter",
        api_key="sk-or-test",
        tee=TEEConfig(
            enabled=True,
            proxy_url="https://confidential.enclave.proxy/v1",
            attestation_token="enclave-attest-abc",
        ),
    )
    client = make_openai_client(
        api_key=llm.api_key,
        base_url=llm.base_url,
        llm_config=llm,
    )

    assert str(client.base_url).rstrip("/") == "https://confidential.enclave.proxy/v1"
    headers = client._custom_headers
    assert headers.get("X-Option-No-Train") == "true"
    assert headers.get("X-TEE-Attestation-Token") == "enclave-attest-abc"


def test_settings_overlay_env_tee(monkeypatch):
    from bughunter.config.settings import load_config

    monkeypatch.setenv("BUGHUNTER_TEE_ENABLED", "1")
    monkeypatch.setenv("BUGHUNTER_TEE_MODE", "attestation_enclave")
    monkeypatch.setenv("BUGHUNTER_TEE_PROXY_URL", "https://tee.proxy.internal/v1")
    monkeypatch.setenv("BUGHUNTER_ZERO_DATA_RETENTION", "1")
    monkeypatch.setenv("BUGHUNTER_TEE_ANONYMIZE", "1")

    config = load_config()
    assert config.llm.tee.enabled is True
    assert config.llm.tee.mode == "attestation_enclave"
    assert config.llm.tee.proxy_url == "https://tee.proxy.internal/v1"
    assert config.llm.tee.zero_data_retention is True
    assert config.llm.tee.anonymize_sensitive_data is True
