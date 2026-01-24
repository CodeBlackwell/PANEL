"""FastAPI application entry point for ArchitX."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.routes import sessions, clarify, debate, judge, artifacts

app = FastAPI(
    title="ArchitX",
    description="Multi-Agent PRD Generator using AutoGen",
    version="1.0.0",
)

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
        "name": "ArchitX",
        "description": "Multi-Agent PRD Generator",
        "docs": "/docs",
    }


# Include routers
app.include_router(sessions.router, prefix=settings.api_prefix)
app.include_router(clarify.router, prefix=settings.api_prefix)
app.include_router(debate.router, prefix=settings.api_prefix)
app.include_router(judge.router, prefix=settings.api_prefix)
app.include_router(artifacts.router, prefix=settings.api_prefix)
