"""Exceptions package for hlpr.

This package re-exports the domain exceptions defined in the legacy
top-level module ``src/hlpr/exceptions.py`` so that existing imports
like ``from hlpr.exceptions import DocumentProcessingError`` continue to
work while allowing submodules (for example, ``hlpr.exceptions.guided``)
to live inside this package.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from types import ModuleType

_here = os.path.dirname(__file__)
_legacy_path = os.path.normpath(os.path.join(_here, "..", "exceptions.py"))

if os.path.exists(_legacy_path):
	spec = importlib.util.spec_from_file_location("hlpr._legacy_exceptions", _legacy_path)
	_mod = importlib.util.module_from_spec(spec)  # type: ModuleType
	sys.modules["hlpr._legacy_exceptions"] = _mod
	if spec and spec.loader:
		spec.loader.exec_module(_mod)

	# Re-export common exception classes from the legacy module
	try:
		DocumentProcessingError = getattr(_mod, "DocumentProcessingError")
		SummarizationError = getattr(_mod, "SummarizationError")
		HlprError = getattr(_mod, "HlprError")
		ValidationError = getattr(_mod, "ValidationError")
		ConfigurationError = getattr(_mod, "ConfigurationError")
	except AttributeError:
		# If something is missing, avoid raising during import; modules
		# that rely on these names will surface a clearer error when used.
		DocumentProcessingError = None  # type: ignore[assignment]
		SummarizationError = None  # type: ignore[assignment]
		HlprError = None  # type: ignore[assignment]
		ValidationError = None  # type: ignore[assignment]
		ConfigurationError = None  # type: ignore[assignment]
else:
	DocumentProcessingError = None  # type: ignore[assignment]
	SummarizationError = None  # type: ignore[assignment]
	HlprError = None  # type: ignore[assignment]
	ValidationError = None  # type: ignore[assignment]
	ConfigurationError = None  # type: ignore[assignment]

__all__ = [
	"DocumentProcessingError",
	"SummarizationError",
	"HlprError",
	"ValidationError",
	"ConfigurationError",
]