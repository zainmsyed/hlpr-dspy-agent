"""Email API endpoints for contract tests."""


from fastapi import APIRouter, Body, HTTPException

router = APIRouter()


@router.get("/accounts", response_model=dict[str, list])
def list_accounts() -> dict[str, list]:
    """List email accounts.

    Returns:
        Dict with list of email accounts.

    """
    return {"accounts": []}


@router.post("/accounts", status_code=201)
def create_account(
    email_address: str = Body(embed=True),
    auth_type: str = Body(embed=True),
) -> dict[str, str]:
    """Create email account.

    Args:
        email_address: Email address for account.
        auth_type: Authentication type.

    Returns:
        Success message with account details.

    Raises:
        HTTPException: If email format is invalid.

    """
    if "@" not in email_address:
        raise HTTPException(
            status_code=422,
            detail="Invalid email format",
        )

    return {
        "message": "Account created successfully",
        "email_address": email_address,
        "auth_type": auth_type,
    }


@router.post("/process")
def process_emails() -> dict[str, str]:
    """Process emails (stub)."""
    return {"message": "Processing started"}
