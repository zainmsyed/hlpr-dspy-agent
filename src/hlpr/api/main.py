"""Main FastAPI application for hlpr."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from hlpr.api import email as email_router
from hlpr.api import jobs as jobs_router
from hlpr.api import providers as providers_router
from hlpr.api.summarize import ErrorResponse
from hlpr.api.summarize import router as summarize_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
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
app.include_router(email_router.router, prefix="/email", tags=["email"])
app.include_router(providers_router.router, prefix="/providers", tags=["providers"])
app.include_router(jobs_router.router, prefix="/jobs", tags=["jobs"])


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        Welcome message.

    """
    return {"message": "Hello World"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Convert FastAPI validation errors into standardized ErrorResponse."""
    # Convert FastAPI validation errors into our standardized ErrorResponse
    error = ErrorResponse(
        error="Invalid request",
        error_code="INVALID_REQUEST",
        details={"errors": exc.errors()},
    )
    return JSONResponse(status_code=422, content=error.model_dump())
