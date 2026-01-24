"""Agents package."""

from .definitions import (
    AgentDefinition,
    CLARIFIER_AGENT,
    MODERATOR_AGENT,
    SYNTHESIZER_AGENT,
    PRD_WRITER_AGENT,
    DEBATE_AGENTS,
    JUDGE_AGENTS,
    ALL_AGENTS,
)
from .teams import (
    ClarificationTeam,
    DebateTeam,
    DraftingTeam,
    JudgingTeam,
)
from .orchestrator import (
    run_clarification,
    process_answers,
    run_debate,
    run_judicial_review,
)

__all__ = [
    "AgentDefinition",
    "CLARIFIER_AGENT",
    "MODERATOR_AGENT",
    "SYNTHESIZER_AGENT",
    "PRD_WRITER_AGENT",
    "DEBATE_AGENTS",
    "JUDGE_AGENTS",
    "ALL_AGENTS",
    "ClarificationTeam",
    "DebateTeam",
    "DraftingTeam",
    "JudgingTeam",
    "run_clarification",
    "process_answers",
    "run_debate",
    "run_judicial_review",
]
