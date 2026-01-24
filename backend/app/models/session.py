"""Session and message models."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum
import uuid


class SessionPhase(str, Enum):
    """Current phase of the session."""
    CREATED = "created"
    IDEA_SUBMITTED = "idea_submitted"
    CONFIGURED = "configured"
    CLARIFYING = "clarifying"
    DEBATING = "debating"
    DRAFTING = "drafting"
    JUDGING = "judging"
    COMPLETED = "completed"
    ERROR = "error"


class AgentType(str, Enum):
    """Available debate agents."""
    ARCHITECT = "architect"
    DEVOPS = "devops"
    SECURITY = "security"
    UX = "ux"
    QA = "qa"
    PRODUCT_MANAGER = "product_manager"
    DATA_ENGINEER = "data_engineer"
    ML_ENGINEER = "ml_engineer"
    FRONTEND_DEV = "frontend_dev"
    BACKEND_DEV = "backend_dev"
    MOBILE_DEV = "mobile_dev"
    BUSINESS_ANALYST = "business_analyst"
    TECH_LEAD = "tech_lead"


class AgentInfo(BaseModel):
    """Information about an available agent."""
    id: AgentType
    name: str
    focus_area: str
    default_selected: bool = False


class SessionConfig(BaseModel):
    """Session configuration for debate."""
    selected_agents: list[AgentType] = Field(
        default=[AgentType.ARCHITECT, AgentType.DEVOPS, AgentType.SECURITY, AgentType.UX, AgentType.QA],
        min_length=2,
        max_length=6
    )
    debate_rounds: int = Field(default=5, ge=3, le=15)


class Session(BaseModel):
    """Session state."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    phase: SessionPhase = SessionPhase.CREATED
    idea: Optional[str] = None
    config: Optional[SessionConfig] = None
    clarification_round: int = 0
    debate_round: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None


class CreateSessionResponse(BaseModel):
    """Response for session creation."""
    session_id: str
    phase: SessionPhase


class SubmitIdeaRequest(BaseModel):
    """Request to submit project idea."""
    idea: str = Field(..., min_length=10, max_length=10000)


class SubmitAnswersRequest(BaseModel):
    """Request to submit answers to clarifying questions."""
    answers: list[str]


class SessionStatus(BaseModel):
    """Session status response."""
    id: str
    phase: SessionPhase
    clarification_round: int
    debate_round: int
    config: Optional[SessionConfig]
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str]
