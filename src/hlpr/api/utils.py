"""Small helpers for API serialization and sanitization."""

from typing import Any


def safe_serialize(obj: Any):
    """Recursively sanitize an object into JSON-friendly primitives.

    Non-primitive objects are converted to their string representation. This
    prevents Pydantic from attempting to serialize library-specific objects
    (for example LLM Message/Choices) which can emit warnings.
    """
    # Primitives
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj

    # Containers
    if isinstance(obj, dict):
        return {str(k): safe_serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [safe_serialize(v) for v in obj]

    # Fallback: return string representation
    try:
        return str(obj)
    except Exception:  # noqa: BLE001 - defensive fallback for objects with broken __str__
        return "<unserializable>"
