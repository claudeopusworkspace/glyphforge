"""Global settings loader — reads settings.json for tunable parameters."""

from __future__ import annotations

import json
import os
from typing import Any

# Default settings path: settings.json in the project root
_DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                              "settings.json")

_cache: dict[str, Any] | None = None
_cache_path: str | None = None


def load(path: str | None = None) -> dict[str, Any]:
    """Load settings from JSON file. Caches the result."""
    global _cache, _cache_path

    path = path or _DEFAULT_PATH

    if _cache is not None and _cache_path == path:
        return _cache

    if not os.path.exists(path):
        raise FileNotFoundError(f"Settings file not found: {path}")

    with open(path) as f:
        _cache = json.load(f)
    _cache_path = path
    return _cache


def reload(path: str | None = None) -> dict[str, Any]:
    """Force reload settings from disk."""
    global _cache, _cache_path
    _cache = None
    _cache_path = None
    return load(path)


def get_range(param: str) -> tuple[float, float]:
    """Get the (min, max) range for a numerical parameter."""
    settings = load()
    ranges = settings.get("parameter_ranges", {})
    if param not in ranges:
        raise KeyError(f"No range defined for parameter: {param!r}")
    lo, hi = ranges[param]
    return (float(lo), float(hi))


def get_allowed(param: str) -> list[str]:
    """Get allowed values for an enum parameter."""
    settings = load()
    allowed = settings.get("allowed_values", {})
    if param not in allowed:
        raise KeyError(f"No allowed values defined for parameter: {param!r}")
    return allowed[param]


def get_validation() -> dict[str, Any]:
    """Get validation thresholds."""
    settings = load()
    return settings.get("validation", {})


def get_export() -> dict[str, Any]:
    """Get export configuration."""
    settings = load()
    return settings.get("export", {})


def get_generation() -> dict[str, Any]:
    """Get generation configuration."""
    settings = load()
    return settings.get("generation", {})
