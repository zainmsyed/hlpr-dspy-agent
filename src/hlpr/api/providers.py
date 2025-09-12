"""Minimal providers API endpoints for contract tests."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/providers")
def list_providers() -> dict[str, list[dict[str, str | bool]]]:
    """List providers.

    Returns:
        Dict with list of available providers.

    """
    return {
        "providers": [
            {
                "name": "local",
                "type": "openai",
                "enabled": True,
            },
        ],
    }
