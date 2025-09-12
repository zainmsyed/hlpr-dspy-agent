"""Jobs API endpoints for contract tests."""

import re

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/{job_id}")
def get_job(job_id: str) -> JSONResponse:
    """Get job by ID.

    Args:
        job_id: UUID string for job.

    Returns:
        JSONResponse with either job data (not implemented) or error body.
    """
    if not re.match(r"^[0-9a-f-]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", job_id):
        return JSONResponse(
            status_code=422,
            content={
                "error": "Invalid job ID format",
                "error_code": "INVALID_JOB_ID",
            },
        )

    # In this stub we always return not found for valid UUIDs
    return JSONResponse(
        status_code=404,
        content={
            "error": "Job not found",
            "error_code": "JOB_NOT_FOUND",
        },
    )
