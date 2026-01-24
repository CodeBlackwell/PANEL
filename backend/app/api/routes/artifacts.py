"""Artifact download endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os

from ...models import SessionPhase
from ...services.conversation_store import conversation_store

router = APIRouter(prefix="/sessions", tags=["artifacts"])


@router.get("/{session_id}/download")
async def download_artifacts(session_id: str):
    """Download session artifacts as ZIP."""
    from ...services.artifact_builder import build_artifact_zip

    session = conversation_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.phase != SessionPhase.COMPLETED:
        raise HTTPException(status_code=400, detail="Session not completed yet")

    try:
        zip_path = await build_artifact_zip(session_id)
        return FileResponse(
            path=zip_path,
            filename=f"prd_{session_id}.zip",
            media_type="application/zip",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build artifacts: {str(e)}")
