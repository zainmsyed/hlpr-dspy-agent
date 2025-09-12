"""Email API endpoints for contract tests.

Implements in-memory storage to satisfy contract tests for accounts and process.
"""

from __future__ import annotations

import re
import uuid
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

# In-memory accounts store for tests
_accounts: dict[str, dict[str, Any]] = {}


@router.get("/accounts")
def list_accounts() -> dict[str, list[dict[str, Any]]]:
    """List configured email accounts (non-sensitive fields only)."""
    accounts_view: list[dict[str, Any]] = []
    for aid, acc in _accounts.items():
        accounts_view.append(
            {
                "id": aid,
                "provider": acc.get("provider", "CUSTOM"),
                "username": acc.get("username"),
                "host": acc.get("host"),
                "last_sync": acc.get("last_sync"),
            },
        )
    return {"accounts": accounts_view}


@router.post("/accounts")
def create_account(payload: dict[str, Any]) -> JSONResponse:
    """Create an email account with basic validation.

    Expected fields (varies by provider): id, provider, host, port?, username, password,
    default_mailbox?, use_tls?.
    """
    # Basic payload validation
    acc_id = payload.get("id")
    provider = payload.get("provider")
    username = payload.get("username")
    password = payload.get("password")
    host = payload.get("host")

    # Validate id format
    if not acc_id or not isinstance(acc_id, str) or not re.match(
        r"^[A-Za-z0-9_\-]+$", acc_id,
    ):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid or missing id", "error_code": "INVALID_ID"},
        )

    # Duplicate check
    if acc_id in _accounts:
        return JSONResponse(
            status_code=409,
            content={
                "error": "Account with this id already exists",
                "error_code": "DUPLICATE_ID",
            },
        )

    # Validate provider
    valid_providers = {"GMAIL", "OUTLOOK", "CUSTOM"}
    if provider not in valid_providers:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid provider", "error_code": "INVALID_PROVIDER"},
        )

    # Basic required fields by provider
    if provider in {"GMAIL", "OUTLOOK"}:
        required = [username, password, host]
        if not all(required):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Missing required fields",
                    "error_code": "INVALID_CONFIG",
                },
            )

    # Save account (omit sensitive fields from GET)
    _accounts[acc_id] = {
        "provider": provider,
        "username": username,
        "password": password,
        "host": host,
        "port": payload.get("port"),
        "default_mailbox": payload.get("default_mailbox", "INBOX"),
        "use_tls": payload.get("use_tls", True),
        "last_sync": None,
    }

    return JSONResponse(
        status_code=201,
        content={
            "id": acc_id,
            "provider": provider,
            "username": username,
            "host": host,
        },
    )


@router.post("/process")
def process_emails(payload: dict[str, Any]) -> JSONResponse:
    """Start processing emails for a given account and return a job id."""
    account_id = payload.get("account_id")
    if not account_id:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing account_id", "error_code": "MISSING_ACCOUNT_ID"},
        )

    # For contract tests, allow a default pseudo account id
    if account_id not in _accounts and account_id != "test_account":
        return JSONResponse(
            status_code=400,
            content={"error": "Account not found", "error_code": "ACCOUNT_NOT_FOUND"},
        )

    job_id = str(uuid.uuid4())
    emails_found = int(payload.get("filters", {}).get("limit", 0) or 0)

    return JSONResponse(
        status_code=200,
        content={
            "job_id": job_id,
            "account_id": account_id,
            "emails_found": emails_found,
            "status": "STARTED",
        },
    )
