"""Web UI backend package for Bug Hunter."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

__all__ = ["__version__"]

try:
    __version__ = version("bughunter")
except PackageNotFoundError:
    __version__ = "0.3.2"
