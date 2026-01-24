"""Judge phase endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import json

from ...models import SessionPhase
from ...services.conversation_store import conversation_store

router = APIRouter(prefix="/sessions", tags=["judge"])


async def judge_stream(session_id: str) -> AsyncGenerator[str, None]:
    """Stream judge evaluations via SSE."""
    from ...agents.orchestrator import run_judicial_review

    session = conversation_store.get_session(session_id)
    if not session:
        yield f"event: error\ndata: {json.dumps({'error': 'Session not found'})}\n\n"
        return

    # Update phase
    session.phase = SessionPhase.JUDGING
    conversation_store.save_session(session)

    try:
        async for event in run_judicial_review(session_id):
            yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


@router.get("/{session_id}/judge/stream")
async def stream_judge(session_id: str):
    """Stream judicial review."""
    session = conversation_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Allow starting judge after debate or drafting
    if session.phase not in [SessionPhase.DEBATING, SessionPhase.DRAFTING, SessionPhase.JUDGING]:
        raise HTTPException(status_code=400, detail="Cannot start judicial review in current phase")

    return StreamingResponse(
        judge_stream(session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
