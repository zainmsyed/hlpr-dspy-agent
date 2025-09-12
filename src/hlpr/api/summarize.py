"""API endpoints for document summarization."""

import json as _json
import logging
import shutil
import tempfile
import time
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from hlpr.document.parser import DocumentParser
from hlpr.document.summarizer import DocumentSummarizer
from hlpr.models.document import Document

logger = logging.getLogger(__name__)

# API configuration constants
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB max file size
MAX_TEXT_LENGTH = 10 * 1024 * 1024  # 10MB max text length

router = APIRouter()


class SummarizeTextRequest(BaseModel):
    """Request model for text-based summarization."""

    text_content: str = Field(..., description="Raw text content to summarize")
    title: str | None = Field(None, description="Document title")
    provider_id: str | None = Field(
        "local", description="AI provider to use",
    )
    format: str | None = Field(
        "json", description="Output format", pattern="^(txt|md|json)$",
    )


class DocumentSummaryResponse(BaseModel):
    """Response model for document summarization."""

    id: str = Field(..., description="Unique identifier for the summary")
    summary: str = Field(..., description="Generated summary")
    key_points: list[str] = Field(
        default_factory=list, description="Extracted key points",
    )
    word_count: int = Field(..., description="Original document word count")
    processing_time_ms: int = Field(..., description="Time taken to process")
    provider_used: str = Field(
        ..., description="AI provider that generated the summary",
    )
    format: str = Field(..., description="Response format")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Machine-readable error code")
    details: dict | None = Field(None, description="Additional error details")


def _raise_http(status_code: int, error: ErrorResponse) -> None:
    """Helper to raise HTTPException with a standardized body."""
    raise HTTPException(status_code=status_code, detail=error.model_dump())


def _process_file_upload(
    *,
    filename: str,
    file_content: bytes,
    provider_id: str | None,
    start_time: float,
) -> DocumentSummaryResponse:
    """Handle uploaded file processing and summarization."""
    file_path = Path(filename)
    extension = file_path.suffix.lower().lstrip(".")
    if extension not in ["pdf", "docx", "txt", "md"]:
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            ErrorResponse(
                error=f"Unsupported file format: {extension}",
                error_code="UNSUPPORTED_FORMAT",
                details={"supported_formats": ["pdf", "docx", "txt", "md"]},
            ),
        )

    file_size = len(file_content)
    if file_size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE // (1024 * 1024)
        actual_mb = file_size // (1024 * 1024)
        _raise_http(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            ErrorResponse(
                error=f"File size exceeds maximum limit of {max_mb}MB",
                error_code="FILE_TOO_LARGE",
                details={
                    "max_size_bytes": MAX_FILE_SIZE,
                    "actual_size_bytes": file_size,
                    "max_size_mb": max_mb,
                    "actual_size_mb": actual_mb,
                },
            ),
        )

    if file_size == 0:
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            ErrorResponse(
                error="Uploaded file is empty",
                error_code="EMPTY_FILE",
            ),
        )

    temp_dir = None
    temp_file_path = None
    try:
        # Create secure temporary directory
        temp_dir = tempfile.mkdtemp(prefix="hlpr_upload_")
        temp_file_path = Path(temp_dir) / f"upload_{uuid4().hex}.{extension}"

        # Write uploaded content to secure temp file
        with temp_file_path.open("wb") as temp_file:
            temp_file.write(file_content)

        # Parse document
        extracted_text = DocumentParser.parse_file(str(temp_file_path))

        # Create document model
        document = Document.from_file(str(temp_file_path))
        document.extracted_text = extracted_text

        # Initialize summarizer
        summarizer = DocumentSummarizer(provider=provider_id or "local")

        # Generate summary
        if len(extracted_text) > 8192:
            result = summarizer.summarize_large_document(
                document, chunking_strategy="sentence",
            )
        else:
            result = summarizer.summarize_document(document)

        word_count = len(extracted_text.split())
        processing_time_ms = int((time.time() - start_time) * 1000)

        return DocumentSummaryResponse(
            id=str(uuid4()),
            summary=result.summary,
            key_points=result.key_points,
            word_count=word_count,
            processing_time_ms=processing_time_ms,
            provider_used=provider_id or "local",
            format="json",
        )
    finally:
        # Clean up temporary directory securely
        try:
            if temp_dir and Path(temp_dir).exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:  # noqa: BLE001
            logger.warning("Failed to cleanup temporary directory %s: %s", temp_dir, e)


def _process_text_request(
    *,
    text_content: str,
    title: str | None,
    provider: str,
    start_time: float,
) -> DocumentSummaryResponse:
    """Handle raw text summarization path."""
    if not text_content.strip():
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            ErrorResponse(error="Text content is empty", error_code="EMPTY_CONTENT"),
        )

    text_length = len(text_content)
    if text_length > MAX_TEXT_LENGTH:
        max_mb = MAX_TEXT_LENGTH // (1024 * 1024)
        actual_mb = text_length // (1024 * 1024)
        _raise_http(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            ErrorResponse(
                error=f"Text content exceeds maximum length of {max_mb}MB",
                error_code="TEXT_TOO_LONG",
                details={
                    "max_length_bytes": MAX_TEXT_LENGTH,
                    "actual_length_bytes": text_length,
                    "max_length_mb": max_mb,
                    "actual_length_mb": actual_mb,
                },
            ),
        )

    summarizer = DocumentSummarizer(provider=provider)
    result = summarizer.summarize_text(text_content, title)

    word_count = len(text_content.split())
    processing_time_ms = int((time.time() - start_time) * 1000)

    return DocumentSummaryResponse(
        id=str(uuid4()),
        summary=result.summary,
        key_points=result.key_points,
        word_count=word_count,
        processing_time_ms=processing_time_ms,
        provider_used=provider,
        format="json",
    )

@router.post(
    "/document",
    response_model=DocumentSummaryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        422: {"model": ErrorResponse, "description": "Processing error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def summarize_document(  # noqa: C901 - endpoint orchestrates multiple validation paths
    request: Request,
    file: UploadFile | None = None,
    provider_id: str | None = None,
    format_param: str | None = "json",
) -> DocumentSummaryResponse:
    """Summarize a document from file upload.

    Supports PDF, DOCX, TXT, and MD files.
    """
    start_time = time.time()

    try:
        # Disallow both file upload and JSON text_content together
        # We will inspect the request body to check for presence of JSON
        body_bytes = None
        try:
            body_bytes = await request.body()
        except Exception:  # noqa: BLE001
            body_bytes = None

        has_json = False
        if body_bytes:
            try:
                _ = _json.loads(body_bytes)
                has_json = True
            except Exception:  # noqa: BLE001
                has_json = False

        # If both file and JSON are provided, return error
        if file is not None and file.filename and has_json:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(
                    error=(
                        "Provide either a file upload or JSON body with text_content,"
                        " not both"
                    ),
                    error_code="MULTIPLE_INPUTS",
                ).model_dump(),
            )

        # If a file was uploaded, process it
        if file is not None and file.filename:
            file_content = await file.read()
            resp = _process_file_upload(
                filename=file.filename,
                file_content=file_content,
                provider_id=provider_id,
                start_time=start_time,
            )
            # Respect requested format param
            resp.format = format_param or resp.format
            return resp

        # Otherwise, expect JSON with text_content
        body = await request.json()
        text_content = body.get("text_content")
        if not text_content:
            # Return standardized ErrorResponse at top-level for missing content
            error = ErrorResponse(
                error="Missing text_content in request",
                error_code="MISSING_TEXT_CONTENT",
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, content=error.model_dump(),
            )

        # Validate text length
        text_length = len(text_content)
        if text_length > MAX_TEXT_LENGTH:
            max_mb = MAX_TEXT_LENGTH // (1024 * 1024)
            actual_mb = text_length // (1024 * 1024)
            error = ErrorResponse(
                error=f"Text content exceeds maximum length of {max_mb}MB",
                error_code="TEXT_TOO_LONG",
                details={
                    "max_length_bytes": MAX_TEXT_LENGTH,
                    "actual_length_bytes": text_length,
                    "max_length_mb": max_mb,
                    "actual_length_mb": actual_mb,
                },
            )
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content=error.model_dump(),
            )

        title = body.get("title")
        provider = body.get("provider_id") or provider_id or "local"
        resp_format = body.get("format") or format_param or "json"

        resp = _process_text_request(
            text_content=text_content,
            title=title,
            provider=provider,
            start_time=start_time,
        )
        resp.format = resp_format
        # fall through to return in else

    except HTTPException:
        raise
    except Exception as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        logger.exception("Failed to process document upload/text")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ErrorResponse(
                error="Failed to process document",
                error_code="PROCESSING_ERROR",
                details={
                    "processing_time_ms": processing_time_ms,
                    "error": str(e),
                },
            ).model_dump(),
        ) from e
    else:
        return resp


@router.post(
    "/document/text",
    response_model=DocumentSummaryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        422: {"model": ErrorResponse, "description": "Processing error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def summarize_text(request: SummarizeTextRequest) -> DocumentSummaryResponse:
    """Summarize raw text content."""
    start_time = time.time()

    try:
        # Validate and process via helper for consistency
        response_obj = _process_text_request(
            text_content=request.text_content,
            title=request.title,
            provider=request.provider_id or "local",
            start_time=start_time,
        )
        # Respect requested response format; fall through to return in else
        response_obj.format = request.format or response_obj.format

    except HTTPException:
        raise
    except Exception as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        logger.exception("Failed to process text summarization")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ErrorResponse(
                error="Failed to process text",
                error_code="PROCESSING_ERROR",
                details={"processing_time_ms": processing_time_ms},
            ).model_dump(),
        ) from e
    else:
        return response_obj
