"""Jobs API endpoints for contract tests."""

import re
from typing import NoReturn

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/jobs/{job_id}", response_model=None)
def get_job(job_id: str) -> NoReturn:
    """Get job by ID.

    Args:
        job_id: UUID string for job.

    Raises:
        HTTPException: If job ID format invalid or job not found.

    """
    if not re.match(r"^[0-9a-f-]{36}$", job_id):
        raise HTTPException(
            status_code=422,
            detail="Invalid job ID format",
        )

    raise HTTPException(
        status_code=404,
        detail="Job not found",
    )
