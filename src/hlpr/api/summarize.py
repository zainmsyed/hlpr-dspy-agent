"""API endpoints for document summarization."""

import logging
import tempfile
import time
from pathlib import Path
from typing import Optional
from uuid import uuid4
import os

from fastapi import APIRouter, File, HTTPException, UploadFile, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from hlpr.document.parser import DocumentParser
from hlpr.document.summarizer import DocumentSummarizer
from hlpr.models.document import Document

logger = logging.getLogger(__name__)

router = APIRouter()


class SummarizeTextRequest(BaseModel):
    """Request model for text-based summarization."""

    text_content: str = Field(..., description="Raw text content to summarize")
    title: Optional[str] = Field(None, description="Document title")
    provider_id: Optional[str] = Field("local", description="AI provider to use")
    format: Optional[str] = Field("json", description="Output format", pattern="^(txt|md|json)$")


class DocumentSummaryResponse(BaseModel):
    """Response model for document summarization."""

    id: str = Field(..., description="Unique identifier for the summary")
    summary: str = Field(..., description="Generated summary")
    key_points: list[str] = Field(default_factory=list, description="Extracted key points")
    word_count: int = Field(..., description="Original document word count")
    processing_time_ms: int = Field(..., description="Time taken to process")
    provider_used: str = Field(..., description="AI provider that generated the summary")
    format: str = Field(..., description="Response format")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Machine-readable error code")
    details: Optional[dict] = Field(None, description="Additional error details")


@router.post(
    "/document",
    response_model=DocumentSummaryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        422: {"model": ErrorResponse, "description": "Processing error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def summarize_document(
    request: Request,
    file: UploadFile | None = File(None),
    provider_id: Optional[str] = None,
    format: Optional[str] = "json",
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
        except Exception:
            body_bytes = None

        has_json = False
        if body_bytes:
            try:
                import json as _json

                _ = _json.loads(body_bytes)
                has_json = True
            except Exception:
                has_json = False

        # If both file and JSON are provided, return error
        if file is not None and file.filename and has_json:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(
                    error="Provide either a file upload or JSON body with text_content, not both",
                    error_code="MULTIPLE_INPUTS",
                ).model_dump(),
            )

        # If a file was uploaded, process it
        if file is not None and file.filename:
            # Check file extension
            file_path = Path(file.filename)
            extension = file_path.suffix.lower().lstrip(".")
            if extension not in ["pdf", "docx", "txt", "md"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorResponse(
                        error=f"Unsupported file format: {extension}",
                        error_code="UNSUPPORTED_FORMAT",
                        details={"supported_formats": ["pdf", "docx", "txt", "md"]},
                    ).model_dump(),
                )

            # Save uploaded file temporarily and ensure robust cleanup
            temp_file_path = None
            try:
                # Create temp file inside the workspace to satisfy path validation
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}", dir=os.getcwd()) as temp_file:
                    content_stream = await file.read()
                    temp_file.write(content_stream)
                    temp_file_path = temp_file.name

                # Parse document
                extracted_text = DocumentParser.parse_file(temp_file_path)

                # Create document model
                document = Document.from_file(temp_file_path)
                document.extracted_text = extracted_text

                # Initialize summarizer
                summarizer = DocumentSummarizer(provider=provider_id or "local")

                # Generate summary
                if len(extracted_text) > 8192:  # Use chunking for large documents
                    result = summarizer.summarize_large_document(document)
                else:
                    result = summarizer.summarize_document(document)

                # Calculate word count
                word_count = len(extracted_text.split())

                processing_time_ms = int((time.time() - start_time) * 1000)

                return DocumentSummaryResponse(
                    id=str(uuid4()),
                    summary=result.summary,
                    key_points=result.key_points,
                    word_count=word_count,
                    processing_time_ms=processing_time_ms,
                    provider_used=provider_id or "local",
                    format=format or "json",
                )

            finally:
                # Clean up temporary file if it was created
                try:
                    if temp_file_path:
                        Path(temp_file_path).unlink(missing_ok=True)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temporary file {temp_file_path}: {e}")

        # Otherwise, expect JSON with text_content
        body = await request.json()
        text_content = body.get("text_content")
        if not text_content:
            # Return standardized ErrorResponse at top-level for missing content
            error = ErrorResponse(
                error="Missing text_content in request",
                error_code="MISSING_TEXT_CONTENT",
            )
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error.model_dump())

        title = body.get("title")
        provider = body.get("provider_id") or provider_id or "local"
        resp_format = body.get("format") or format or "json"

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
            format=resp_format,
        )

    except HTTPException:
        raise
    except Exception as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Failed to process document upload/text: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ErrorResponse(
                error="Failed to process document",
                error_code="PROCESSING_ERROR",
                details={"processing_time_ms": processing_time_ms, "error": str(e)},
            ).model_dump(),
        )


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
        # Validate text content
        if not request.text_content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error="Text content is empty",
                    error_code="EMPTY_CONTENT",
                ).model_dump(),
            )

        # Initialize summarizer
        summarizer = DocumentSummarizer(provider=request.provider_id or "local")

        # Generate summary
        result = summarizer.summarize_text(
            request.text_content,
            request.title,
        )

        # Calculate word count
        word_count = len(request.text_content.split())

        processing_time_ms = int((time.time() - start_time) * 1000)

        return DocumentSummaryResponse(
            id=str(uuid4()),
            summary=result.summary,
            key_points=result.key_points,
            word_count=word_count,
            processing_time_ms=processing_time_ms,
            provider_used=request.provider_id or "local",
            format=request.format or "json",
        )

    except HTTPException:
        raise
    except Exception as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Failed to process text summarization: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ErrorResponse(
                error="Failed to process text",
                error_code="PROCESSING_ERROR",
                details={"processing_time_ms": processing_time_ms},
            ).model_dump(),
        )