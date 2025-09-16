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

from hlpr.api.utils import safe_serialize
from hlpr.config import CONFIG
from hlpr.document.parser import DocumentParser
from hlpr.document.summarizer import DocumentSummarizer
from hlpr.models.document import Document

logger = logging.getLogger(__name__)

# Use centralized configuration
MAX_FILE_SIZE = CONFIG.max_file_size
MAX_TEXT_LENGTH = CONFIG.max_text_length

router = APIRouter()


class SummarizeTextRequest(BaseModel):
    """Request model for text-based summarization."""

    text_content: str = Field(..., description="Raw text content to summarize")
    title: str | None = Field(None, description="Document title")
    provider_id: str | None = Field(
        "local", description="AI provider to use",
    )
    temperature: float | None = Field(
        None, description="Sampling temperature for the model (0.0-1.0)",
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


class MeetingSummaryResponse(BaseModel):
    """Response model for meeting summarization."""

    id: str = Field(..., description="Unique identifier for the meeting summary")
    overview: str = Field(
        ..., description="Short overview / summary of the meeting",
    )
    key_points: list[str] = Field(
        default_factory=list, description="Key points from the meeting",
    )
    action_items: list[str] = Field(
        default_factory=list, description="Extracted action items",
    )
    participants: list[str] = Field(
        default_factory=list, description="Detected participants",
    )
    processing_time_ms: int = Field(..., description="Time taken to process")


def _raise_http(status_code: int, error: ErrorResponse) -> None:
    """Helper to raise HTTPException with a standardized body."""
    detail = safe_serialize(error.model_dump())
    raise HTTPException(status_code=status_code, detail=detail)


def _process_file_upload(
    *,
    filename: str,
    file_content: bytes,
    provider_id: str | None,
    temperature: float | None,
    start_time: float,
) -> DocumentSummaryResponse:
    """Handle uploaded file processing and summarization."""
    file_path = Path(filename)
    extension = file_path.suffix.lower().lstrip(".")
    if extension not in ["pdf", "docx", "txt", "md"]:
        supported = {"supported_formats": ["pdf", "docx", "txt", "md"]}
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            ErrorResponse(
                error=f"Unsupported file format: {extension}",
                error_code="UNSUPPORTED_FORMAT",
                details=safe_serialize(supported),
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
                details=safe_serialize({
                    "max_size_bytes": MAX_FILE_SIZE,
                    "actual_size_bytes": file_size,
                    "max_size_mb": max_mb,
                    "actual_size_mb": actual_mb,
                }),
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

        # Initialize summarizer (respect optional temperature)
        summarizer = DocumentSummarizer(
            provider=provider_id or "local",
            temperature=temperature if temperature is not None else 0.3,
        )

        # Generate summary
        if len(extracted_text) > 8192:
            result = summarizer.summarize_large_document(
                document, chunking_strategy="sentence",
            )
        else:
            result = summarizer.summarize_document(document)

        word_count = len(extracted_text.split())
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Defensive: sanitize all values coming from the summarizer to ensure
        # no third-party library objects (LLM internals) are passed into
        # Pydantic models which may trigger serializer warnings.
        return DocumentSummaryResponse(
            id=str(uuid4()),
            summary=safe_serialize(result.summary),
            key_points=safe_serialize(result.key_points),
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
    temperature: float | None,
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
                details=safe_serialize({
                    "max_length_bytes": MAX_TEXT_LENGTH,
                    "actual_length_bytes": text_length,
                    "max_length_mb": max_mb,
                    "actual_length_mb": actual_mb,
                }),
            ),
        )

    summarizer = DocumentSummarizer(
        provider=provider,
        temperature=temperature if temperature is not None else 0.3,
    )
    result = summarizer.summarize_text(text_content, title)

    word_count = len(text_content.split())
    processing_time_ms = int((time.time() - start_time) * 1000)

    return DocumentSummaryResponse(
        id=str(uuid4()),
        summary=safe_serialize(result.summary),
        key_points=safe_serialize(result.key_points),
        word_count=word_count,
        processing_time_ms=processing_time_ms,
        provider_used=provider,
        format="json",
    )


def _extract_meeting_items(text: str) -> tuple[list[str], list[str]]:
    """Extract action items and participants from meeting text.

    This is a simple, best-effort heuristic and is intentionally lightweight.
    """
    action_items: list[str] = []
    participants: list[str] = []

    for line in text.splitlines():
        low = line.lower()
        if any(k in low for k in ["action:", "todo:", "- [ ]", "* [ ]"]):
            action_items.append(line.strip())
            continue

        # crude heuristic: lines with 'will', 'needs to', 'should', 'to'
        if any(k in low for k in [" will ", " needs to ", " should ", " to "]) and len(
            line.strip(),
        ) > 5:
            action_items.append(line.strip())

        if low.startswith(("attendees:", "present:")):
            parts = line.split(":", 1)[1]
            participants = [
                p.strip()
                for p in parts.replace("(", "").replace(")", "").split(",")
                if p.strip()
            ]
            # One line is enough to determine participants
            break

    return action_items, participants



    # duplicate helper removed


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
    temperature: float | None = None,
) -> DocumentSummaryResponse:
    """Summarize a document from file upload.

    Supports PDF, DOCX, TXT, and MD files.
    """
    start_time = time.time()

    # Read the raw body once to detect whether JSON was sent alongside a file
    try:
        body_bytes = await request.body()
    except (RuntimeError, ValueError, OSError):
        body_bytes = b""

    has_json = False
    if body_bytes:
        try:
            _ = _json.loads(body_bytes)
            has_json = True
        except _json.JSONDecodeError:
            has_json = False

    try:
        if file is not None and file.filename and has_json:
            err = ErrorResponse(
                error="Provide either file upload or JSON body, not both",
                error_code="MULTIPLE_INPUTS",
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=safe_serialize(err.model_dump()),
            )

        if file is not None and file.filename:
            file_content = await file.read()
            resp = _process_file_upload(
                filename=file.filename,
                file_content=file_content,
                provider_id=provider_id,
                temperature=temperature,
                start_time=start_time,
            )
            resp.format = format_param or resp.format
            content = safe_serialize(resp.model_dump())
            return JSONResponse(status_code=status.HTTP_200_OK, content=content)

        # Expect JSON with text_content
        try:
            body = await request.json()
        except (ValueError, TypeError, _json.JSONDecodeError):
            body = {}

        text_content = body.get("text_content")
        if not text_content:
            error = ErrorResponse(
                error="Missing text_content in request",
                error_code="MISSING_TEXT_CONTENT",
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=safe_serialize(error.model_dump()),
            )

        text_length = len(text_content)
        if text_length > MAX_TEXT_LENGTH:
            max_mb = MAX_TEXT_LENGTH // (1024 * 1024)
            actual_mb = text_length // (1024 * 1024)
            error = ErrorResponse(
                error=f"Text content exceeds maximum length of {max_mb}MB",
                error_code="TEXT_TOO_LONG",
                details=safe_serialize({
                    "max_length_bytes": MAX_TEXT_LENGTH,
                    "actual_length_bytes": text_length,
                    "max_length_mb": max_mb,
                    "actual_length_mb": actual_mb,
                }),
            )
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content=safe_serialize(error.model_dump()),
            )

        title = body.get("title")
        provider = body.get("provider_id") or provider_id or "local"
        resp_format = body.get("format") or format_param or "json"
        body_temp = body.get("temperature")

        resp = _process_text_request(
            text_content=text_content,
            title=title,
            provider=provider,
            temperature=body_temp,
            start_time=start_time,
        )
        resp.format = resp_format
        content = safe_serialize(resp.model_dump())
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)

    except HTTPException:
        raise
    except Exception as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        logger.exception("Failed to process document upload/text")
        err = ErrorResponse(
            error="Failed to process document",
            error_code="PROCESSING_ERROR",
            details={
                "processing_time_ms": processing_time_ms,
                "error": str(e),
            },
        )
        detail = safe_serialize(err.model_dump())
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        ) from e


@router.post(
    "/document/upload",
    response_model=DocumentSummaryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        422: {"model": ErrorResponse, "description": "Processing error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def summarize_document_upload(
    file: UploadFile,
    provider_id: str | None = None,
    format_param: str | None = "json",
    temperature: float | None = None,
) -> DocumentSummaryResponse:
    """Summarize an uploaded document file only."""
    start_time = time.time()

    if not file or not file.filename:
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            ErrorResponse(error="No file uploaded", error_code="NO_FILE"),
        )

    file_content = await file.read()
    resp = _process_file_upload(
        filename=file.filename,
        file_content=file_content,
        provider_id=provider_id,
        temperature=temperature,
        start_time=start_time,
    )
    resp.format = format_param or resp.format
    content = safe_serialize(resp.model_dump())
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@router.post(
    "/document/text",
    response_model=DocumentSummaryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        422: {"model": ErrorResponse, "description": "Processing error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def summarize_document_text(
    request: SummarizeTextRequest,
) -> DocumentSummaryResponse:
    """Summarize raw text content only (JSON request)."""
    # Delegate to helper used by CLI and existing text endpoint
    start_time = time.time()
    response_obj = _process_text_request(
        text_content=request.text_content,
        title=request.title,
        provider=request.provider_id or "local",
        temperature=request.temperature,
        start_time=start_time,
    )
    response_obj.format = request.format or response_obj.format
    content = safe_serialize(response_obj.model_dump())
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)
async def summarize_text(request: SummarizeTextRequest) -> DocumentSummaryResponse:
    """Summarize raw text content."""
    start_time = time.time()

    try:
        # Validate and process via helper for consistency
        response_obj = _process_text_request(
            text_content=request.text_content,
            title=request.title,
            provider=request.provider_id or "local",
            temperature=request.temperature,
            start_time=start_time,
        )
        # Respect requested response format
        response_obj.format = request.format or response_obj.format

        # Return sanitized JSONResponse to guarantee only primitives are serialized
        content = safe_serialize(response_obj.model_dump())
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)

    except HTTPException:
        raise
    except Exception as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        logger.exception("Failed to process text summarization")
        err = ErrorResponse(
            error="Failed to process text",
            error_code="PROCESSING_ERROR",
            details={"processing_time_ms": processing_time_ms},
        )
        detail = safe_serialize(err.model_dump())
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        ) from e



@router.post(
    "/meeting",
    response_model=MeetingSummaryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        422: {"model": ErrorResponse, "description": "Processing error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def summarize_meeting_endpoint(request: Request) -> MeetingSummaryResponse:
    """Summarize meeting notes provided as JSON.

    Expected JSON body example:
    {
        "content": "...",
        "title": "...",
        "date": "...",
        "provider_id": "local",
        "temperature": 0.3,
    }
    """
    start_time = time.time()

    try:
        body = await request.json()
    except (ValueError, TypeError, _json.JSONDecodeError):
        body = {}

    content = body.get("content")
    title = body.get("title")
    provider = body.get("provider_id") or body.get("provider") or "local"
    temperature = body.get("temperature")

    # Missing content -> invalid request
    if content is None:
        err = ErrorResponse(
            error="Missing content in request",
            error_code="MISSING_CONTENT",
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=safe_serialize(err.model_dump()),
        )

    # Build overview (first non-empty line or minimal placeholder)
    if isinstance(content, str):
        overview = content.split("\n", 1)[0].strip() or "Meeting overview"
    else:
        overview = "Meeting overview"

    # Use DocumentSummarizer to extract summary + key points when possible
    key_points: list[str] = []
    try:
        summarizer = DocumentSummarizer(
            provider=provider,
            temperature=temperature if temperature is not None else 0.3,
        )

        if isinstance(content, str) and content.strip():
            summary_result = summarizer.summarize_text(content, title)
        else:
            summary_result = summarizer.summarize_text(overview)

        key_points = getattr(summary_result, "key_points", []) or []
    except Exception:
        # In case summarizer fails, fall back to simple heuristics
        logger.exception("Meeting summarization failed, using fallback heuristics")
        key_points = []

    # Simple heuristic extraction for action items and participants
    action_items, participants = ([], [])
    if isinstance(content, str):
        action_items, participants = _extract_meeting_items(content)

    processing_time_ms = int((time.time() - start_time) * 1000)

    resp = MeetingSummaryResponse(
        id=str(uuid4()),
        overview=safe_serialize(overview),
        key_points=safe_serialize(key_points),
        action_items=safe_serialize(action_items),
        participants=safe_serialize(participants),
        processing_time_ms=processing_time_ms,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=safe_serialize(resp.model_dump()),
    )
