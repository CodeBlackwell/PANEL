"""FastAPI application entry point for PANEL."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import settings
from .api.routes import sessions, clarify, debate, judge, artifacts, auth, github
from .services.cleanup import cleanup_expired_sessions

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup/shutdown tasks."""
    # Startup: clean up old sessions
    cleanup_expired_sessions()
    # Start periodic cleanup (every 30 minutes)
    cleanup_task = asyncio.create_task(_periodic_cleanup())
    yield
    # Shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


async def _periodic_cleanup():
    """Run session cleanup every 30 minutes."""
    while True:
        await asyncio.sleep(1800)
        cleanup_expired_sessions()


app = FastAPI(
    title="PANEL",
    description="PRD from Agent Negotiation & Expert Logic",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "PANEL",
        "description": "PRD from Agent Negotiation & Expert Logic",
        "docs": "/docs",
    }


# Include routers
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(github.router, prefix=settings.api_prefix)
app.include_router(sessions.router, prefix=settings.api_prefix)
app.include_router(clarify.router, prefix=settings.api_prefix)
app.include_router(debate.router, prefix=settings.api_prefix)
app.include_router(judge.router, prefix=settings.api_prefix)
app.include_router(artifacts.router, prefix=settings.api_prefix)
