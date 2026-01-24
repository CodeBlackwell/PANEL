"""Clarification phase endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import json
import asyncio

from ...models import SessionPhase, SubmitAnswersRequest, SessionStatus
from ...services.conversation_store import conversation_store

router = APIRouter(prefix="/sessions", tags=["clarification"])


async def clarification_stream(session_id: str) -> AsyncGenerator[str, None]:
    """Stream clarification questions via SSE."""
    from ...agents.orchestrator import run_clarification

    session = conversation_store.get_session(session_id)
    if not session:
        yield f"event: error\ndata: {json.dumps({'error': 'Session not found'})}\n\n"
        return

    # Update phase
    session.phase = SessionPhase.CLARIFYING
    conversation_store.save_session(session)

    try:
        async for event in run_clarification(session_id):
            yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


@router.get("/{session_id}/clarify/stream")
async def stream_clarification(session_id: str):
    """Stream clarifying questions."""
    session = conversation_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.phase not in [SessionPhase.CONFIGURED, SessionPhase.CLARIFYING]:
        raise HTTPException(status_code=400, detail="Cannot start clarification in current phase")

    return StreamingResponse(
        clarification_stream(session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{session_id}/answers", response_model=SessionStatus)
async def submit_answers(session_id: str, request: SubmitAnswersRequest):
    """Submit answers to clarifying questions."""
    from ...agents.orchestrator import process_answers

    session = conversation_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.phase != SessionPhase.CLARIFYING:
        raise HTTPException(status_code=400, detail="Not in clarification phase")

    # Process answers through the agent
    await process_answers(session_id, request.answers)

    session = conversation_store.get_session(session_id)
    return SessionStatus(
        id=session.id,
        phase=session.phase,
        clarification_round=session.clarification_round,
        debate_round=session.debate_round,
        config=session.config,
        created_at=session.created_at,
        updated_at=session.updated_at,
        error_message=session.error_message,
    )
