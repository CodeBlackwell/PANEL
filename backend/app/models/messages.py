"""Message models for agent communication."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """Type of agent message."""
    QUESTION = "question"
    ANSWER = "answer"
    PROPOSAL = "proposal"
    CRITIQUE = "critique"
    AGREEMENT = "agreement"
    SUMMARY = "summary"
    EVALUATION = "evaluation"
    SYSTEM = "system"


class AgentMessage(BaseModel):
    """Message from an agent."""
    agent_name: str
    agent_type: str
    content: str
    message_type: MessageType
    round_number: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)


class ClarificationQuestion(BaseModel):
    """A clarifying question from the ClarifierAgent."""
    question: str
    context: Optional[str] = None
    round_number: int


class ClarificationQuestions(BaseModel):
    """Set of clarifying questions for a round."""
    questions: list[ClarificationQuestion]
    round_number: int
    is_complete: bool = False


class DebateMessage(BaseModel):
    """A message in the expert debate."""
    agent_name: str
    agent_type: str
    content: str
    message_type: Literal["proposal", "critique", "agreement", "summary"]
    round_number: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class JudgeScore(BaseModel):
    """Score from a single judge."""
    judge_name: str
    judge_type: Literal["business", "technical", "feasibility"]
    scores: dict[str, int]  # criterion -> score (1-10)
    reasoning: str
    overall_score: float


class JudgeEvaluation(BaseModel):
    """Complete evaluation from all judges."""
    business: JudgeScore
    technical: JudgeScore
    feasibility: JudgeScore
    overall_verdict: str
    recommendations: list[str]


class SSEEvent(BaseModel):
    """Server-Sent Event payload."""
    event: str
    data: dict
    id: Optional[str] = None
