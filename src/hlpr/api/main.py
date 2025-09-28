"""Main FastAPI application for hlpr."""

import os
import warnings
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

# Local routers (keep top-level imports together)
from hlpr.api import email as email_router
from hlpr.api import jobs as jobs_router
from hlpr.api import providers as providers_router
from hlpr.api.summarize import ErrorResponse
from hlpr.api.summarize import router as summarize_router
from hlpr.api.utils import safe_serialize

# Suppress known noisy warnings from dependencies that are not actionable
# in our code path during tests (these originate from third-party adapters
# and Pydantic's serializer). Use regex matching and module targeting to
# avoid accidentally hiding unrelated warnings.
#
# - Pydantic emits a UserWarning with the prefix 'Pydantic serializer warnings'
#   when it encounters unexpected/third-party objects during serialization.
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=r".*Pydantic serializer warnings.*",
    module=r"pydantic.*",
)

# - httpx currently emits a DeprecationWarning about using `content=` to upload
#   raw bytes/text in some versions; silence that specific message from httpx
#   internals during tests.
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=r".*Use 'content=.*' to upload raw bytes/text content.*",
    module=r"httpx.*",
)

# As a final fallback for test environments, also ignore these warnings
# globally so they don't clutter CI logs while we finish auditing the
# DSPy integration for any remaining object leaks.
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=r".*Pydantic serializer warnings.*",
)
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=r".*Use 'content=.*' to upload raw bytes/text content.*",
)


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
def _get_allowed_origins() -> list[str]:
    """Return allowed CORS origins from environment or sane defaults.

    - HLPR_ALLOWED_ORIGINS can be set to a comma-separated list of origins.
    - If set to '*' (single character), all origins are allowed (useful
      for development only).
    - Default is limited to localhost addresses to avoid accidental
      wide-open CORS in production.
    """
    env = os.getenv("HLPR_ALLOWED_ORIGINS")
    if env is None:
        return ["http://localhost", "http://127.0.0.1"]
    env = env.strip()
    if env == "*":
        return ["*"]
    # Split comma-separated list and strip whitespace
    origins = [o.strip() for o in env.split(",") if o.strip()]
    return origins or ["http://localhost", "http://127.0.0.1"]


allowed_origins = _get_allowed_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
        details=safe_serialize({"errors": exc.errors()}),
    )
    return JSONResponse(status_code=422, content=safe_serialize(error.model_dump()))
