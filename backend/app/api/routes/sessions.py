"""Session management endpoints."""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from pydantic import BaseModel

from ...models import (
    Session,
    SessionPhase,
    SessionConfig,
    AgentType,
    AgentInfo,
    CreateSessionResponse,
    SubmitIdeaRequest,
    SessionStatus,
    RepoContext,
    User,
)
from ...services.conversation_store import conversation_store
from ..dependencies import get_current_user_optional

router = APIRouter(prefix="/sessions", tags=["sessions"])


class CreateSessionRequest(BaseModel):
    """Request to create a new session with optional repo context."""
    repo_context: Optional[RepoContext] = None

# Available agents with their metadata
AVAILABLE_AGENTS: List[AgentInfo] = [
    AgentInfo(id=AgentType.ARCHITECT, name="Architect", focus_area="System design, scalability, patterns, tech stack", default_selected=True),
    AgentInfo(id=AgentType.DEVOPS, name="DevOps", focus_area="CI/CD, infrastructure, containers, monitoring", default_selected=True),
    AgentInfo(id=AgentType.SECURITY, name="Security", focus_area="Auth, encryption, compliance, threat modeling", default_selected=True),
    AgentInfo(id=AgentType.UX, name="UX", focus_area="User experience, accessibility, mobile-first", default_selected=True),
    AgentInfo(id=AgentType.QA, name="QA", focus_area="Testing strategies, quality gates, automation", default_selected=True),
    AgentInfo(id=AgentType.PRODUCT_MANAGER, name="Product Manager", focus_area="User stories, roadmap, prioritization, stakeholders", default_selected=False),
    AgentInfo(id=AgentType.DATA_ENGINEER, name="Data Engineer", focus_area="Data pipelines, storage, ETL, analytics", default_selected=False),
    AgentInfo(id=AgentType.ML_ENGINEER, name="ML Engineer", focus_area="ML models, training, inference, MLOps", default_selected=False),
    AgentInfo(id=AgentType.FRONTEND_DEV, name="Frontend Dev", focus_area="UI frameworks, state management, performance", default_selected=False),
    AgentInfo(id=AgentType.BACKEND_DEV, name="Backend Dev", focus_area="APIs, databases, caching, microservices", default_selected=False),
    AgentInfo(id=AgentType.MOBILE_DEV, name="Mobile Dev", focus_area="iOS/Android, cross-platform, app stores", default_selected=False),
    AgentInfo(id=AgentType.BUSINESS_ANALYST, name="Business Analyst", focus_area="Requirements, ROI, market analysis, KPIs", default_selected=False),
    AgentInfo(id=AgentType.TECH_LEAD, name="Tech Lead", focus_area="Code quality, team practices, technical debt", default_selected=False),
]


@router.post("", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: Optional[CreateSessionRequest] = None,
    user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Create a new session.
    If user is authenticated, session will be linked to the user.
    If repo_context is provided, it will be attached to the session.
    """
    user_id = user.id if user else None
    session = conversation_store.create_session(user_id=user_id)

    # Attach repo context if provided
    if request and request.repo_context:
        session.repo_context = request.repo_context
        conversation_store.save_session(session)

    return CreateSessionResponse(session_id=session.id, phase=session.phase)


@router.get("/{session_id}", response_model=SessionStatus)
async def get_session(session_id: str):
    """Get session status."""
    session = conversation_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionStatus(
        id=session.id,
        phase=session.phase,
        clarification_round=session.clarification_round,
        debate_round=session.debate_round,
        config=session.config,
        created_at=session.created_at,
        updated_at=session.updated_at,
        error_message=session.error_message,
        user_id=session.user_id,
        repo_context=session.repo_context,
    )


@router.post("/{session_id}/idea", response_model=SessionStatus)
async def submit_idea(session_id: str, request: SubmitIdeaRequest):
    """Submit project idea."""
    session = conversation_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.phase != SessionPhase.CREATED:
        raise HTTPException(status_code=400, detail="Idea already submitted")

    session = conversation_store.save_idea(session_id, request.idea)
    return SessionStatus(
        id=session.id,
        phase=session.phase,
        clarification_round=session.clarification_round,
        debate_round=session.debate_round,
        config=session.config,
        created_at=session.created_at,
        updated_at=session.updated_at,
        error_message=session.error_message,
        user_id=session.user_id,
        repo_context=session.repo_context,
    )


@router.post("/{session_id}/config", response_model=SessionStatus)
async def configure_session(session_id: str, config: SessionConfig):
    """Configure session with selected agents and debate rounds."""
    session = conversation_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.phase not in [SessionPhase.IDEA_SUBMITTED, SessionPhase.CONFIGURED]:
        raise HTTPException(status_code=400, detail="Cannot configure session in current phase")

    # Validate agent selection
    if len(config.selected_agents) < 2:
        raise HTTPException(status_code=400, detail="Must select at least 2 agents")
    if len(config.selected_agents) > 6:
        raise HTTPException(status_code=400, detail="Cannot select more than 6 agents")

    session.config = config
    session.phase = SessionPhase.CONFIGURED
    conversation_store.save_session(session)

    return SessionStatus(
        id=session.id,
        phase=session.phase,
        clarification_round=session.clarification_round,
        debate_round=session.debate_round,
        config=session.config,
        created_at=session.created_at,
        updated_at=session.updated_at,
        error_message=session.error_message,
        user_id=session.user_id,
        repo_context=session.repo_context,
    )


@router.get("", response_model=List[AgentInfo])
async def list_agents():
    """List available agents for debate."""
    return AVAILABLE_AGENTS
