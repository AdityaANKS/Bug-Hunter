"""BugHunter basic integration tests: verify imports and version."""

import pytest


def test_import_bughunter():
    """Test that the main package can be imported."""
    from pathlib import Path

    import toml

    import bughunter

    # Read version from pyproject.toml to avoid hardcoding
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    pyproject = toml.load(pyproject_path)
    expected_version = pyproject["project"]["version"]

    assert bughunter.__version__ == expected_version


def test_all_submodules_importable():
    """Test that all major submodules can be imported."""


def test_no_import_errors():
    """Verify no module raises on import."""
    import importlib

    modules = [
        "bughunter",
        "bughunter.config.schema",
        "bughunter.config.settings",
        "bughunter.agent.context",
        "bughunter.agent.memory",
        "bughunter.agent.prompts",
        "bughunter.agent.core",
        "bughunter.mcp.registry",
        "bughunter.mcp.router",
        "bughunter.mcp.lifecycle",
        "bughunter.skills.loader",
        "bughunter.skills.dispatcher",
        "bughunter.kb.store",
        "bughunter.kb.retriever",
        "bughunter.kb.updater",
        "bughunter.report.generator",
        "bughunter.report.poc_builder",
        "bughunter.cli.main",
    ]
    for mod_name in modules:
        try:
            importlib.import_module(mod_name)
        except ImportError as e:
            pytest.fail(f"Failed to import {mod_name}: {e}")
