"""Configuration package for hlpr.

This package re-exports the legacy module-level configuration defined in
``src/hlpr/config.py`` so that existing imports like
``from hlpr.config import CONFIG`` continue to work even though there is
also a ``hlpr.config`` package containing additional configuration
modules (for guided mode, UI strings, etc.).

The module in ``src/hlpr/config.py`` is loaded dynamically and a small
set of attributes (currently ``CONFIG`` and ``HlprConfig``) are exposed
from this package for backward compatibility.
"""

from __future__ import annotations

import importlib.util
import os
import sys

__all__ = ["CONFIG", "HlprConfig"]

# Attempt to load the legacy module ``src/hlpr/config.py`` and re-export
# selected attributes. This keeps existing imports working while allowing
# the project to organize additional config submodules under
# ``src/hlpr/config/``.
_here = os.path.dirname(__file__)
_legacy_path = os.path.normpath(os.path.join(_here, "..", "config.py"))

if os.path.exists(_legacy_path):
    spec = importlib.util.spec_from_file_location("hlpr._legacy_config", _legacy_path)
    _mod = importlib.util.module_from_spec(spec)
    # Insert into sys.modules under a private name so other imports don't
    # accidentally pick it up under the same name.
    sys.modules["hlpr._legacy_config"] = _mod
    if spec and spec.loader:
        spec.loader.exec_module(_mod)
    # Re-export the commonly used names expected by the codebase
    try:
        CONFIG = _mod.CONFIG
    except AttributeError:
        CONFIG = None  # type: ignore[assignment]

    try:
        HlprConfig = _mod.HlprConfig
    except AttributeError:
        HlprConfig = None  # type: ignore[assignment]
else:
    # Fallbacks if the legacy module is missing: keep names defined to
    # avoid ImportError during startup; callers should detect None if
    # configuration couldn't be loaded.
    CONFIG = None  # type: ignore[assignment]
    HlprConfig = None  # type: ignore[assignment]
