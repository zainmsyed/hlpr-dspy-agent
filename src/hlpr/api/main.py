"""Main FastAPI application for hlpr."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hlpr.api.summarize import router as summarize_router
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from hlpr.api.summarize import ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager."""
    # Startup
    yield
    # Shutdown


# Create FastAPI app
app = FastAPI(
    title="hlpr Document Summarization API",
    description="API for document summarization using AI",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(summarize_router, prefix="/summarize", tags=["summarize"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "hlpr Document Summarization API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # Convert FastAPI validation errors into our standardized ErrorResponse
    error = ErrorResponse(
        error="Invalid request",
        error_code="INVALID_REQUEST",
        details={"errors": exc.errors()},
    )
    return JSONResponse(status_code=422, content=error.model_dump())