"""Providers API endpoints for contract tests.

This returns a minimal but schema-compatible list of providers expected by tests.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_providers() -> dict[str, list[dict[str, str | bool]]]:
    """List AI providers.

    Returns:
        Dict with list of available providers including required fields.

    """
    # Provide a minimal set with exactly one default LOCAL provider
    providers = [
        {
            "id": "local",
            "type": "LOCAL",  # Allowed: LOCAL | OPENAI | ANTHROPIC
            "model_name": "llama2:7b",
            "is_default": True,
            "status": "AVAILABLE",  # Allowed: AVAILABLE | UNAVAILABLE | ERROR
        },
    ]
    return {"providers": providers}
