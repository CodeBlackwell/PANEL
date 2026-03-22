"""Debate phase endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import json

from ...models import SessionPhase
from ...services.conversation_store import conversation_store

router = APIRouter(prefix="/sessions", tags=["debate"])


async def debate_stream(session_id: str) -> AsyncGenerator[str, None]:
    """Stream debate messages via SSE."""
    from ...agents.orchestrator import run_debate

    session = conversation_store.get_session(session_id)
    if not session:
        yield f"event: error\ndata: {json.dumps({'error': 'Session not found'})}\n\n"
        return

    # Update phase
    session.phase = SessionPhase.DEBATING
    conversation_store.save_session(session)

    try:
        async for event in run_debate(session_id):
            yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


@router.get("/{session_id}/debate/stream")
async def stream_debate(session_id: str):
    """Stream expert debate."""
    session = conversation_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Allow starting debate after configuration or clarification
    if session.phase not in [SessionPhase.CONFIGURED, SessionPhase.CLARIFYING, SessionPhase.DEBATING]:
        raise HTTPException(status_code=400, detail="Cannot start debate in current phase")

    return StreamingResponse(
        debate_stream(session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
