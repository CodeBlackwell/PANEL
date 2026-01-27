"""File-based session and conversation storage."""

import json
import os
from datetime import datetime
from typing import Optional
from pathlib import Path

from ..config import settings
from ..models import Session, SessionPhase, AgentMessage


class ConversationStore:
    """File-based storage for sessions and conversations."""

    def __init__(self, storage_path: str = None):
        self.storage_path = Path(storage_path or settings.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _session_dir(self, session_id: str) -> Path:
        """Get the directory for a session."""
        return self.storage_path / session_id

    def _session_file(self, session_id: str) -> Path:
        """Get the session state file path."""
        return self._session_dir(session_id) / "session.json"

    def _transcripts_dir(self, session_id: str) -> Path:
        """Get the transcripts directory for a session."""
        return self._session_dir(session_id) / "transcripts"

    def _metadata_dir(self, session_id: str) -> Path:
        """Get the metadata directory for a session."""
        return self._session_dir(session_id) / "metadata"

    def create_session(self, user_id: Optional[str] = None) -> Session:
        """Create a new session, optionally linked to a user."""
        session = Session(user_id=user_id)
        session_dir = self._session_dir(session.id)
        session_dir.mkdir(parents=True, exist_ok=True)
        self._transcripts_dir(session.id).mkdir(exist_ok=True)
        self._metadata_dir(session.id).mkdir(exist_ok=True)
        self.save_session(session)
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        session_file = self._session_file(session_id)
        if not session_file.exists():
            return None
        with open(session_file, "r") as f:
            data = json.load(f)
        return Session(**data)

    def save_session(self, session: Session) -> None:
        """Save session state."""
        session.updated_at = datetime.utcnow()
        session_file = self._session_file(session.id)
        with open(session_file, "w") as f:
            json.dump(session.model_dump(mode="json"), f, default=str, indent=2)

    def update_phase(self, session_id: str, phase: SessionPhase) -> Optional[Session]:
        """Update session phase."""
        session = self.get_session(session_id)
        if session:
            session.phase = phase
            self.save_session(session)
        return session

    def save_idea(self, session_id: str, idea: str) -> Optional[Session]:
        """Save the project idea."""
        session = self.get_session(session_id)
        if session:
            session.idea = idea
            session.phase = SessionPhase.IDEA_SUBMITTED
            self.save_session(session)
            # Also save to original_prompt.txt
            prompt_file = self._session_dir(session_id) / "original_prompt.txt"
            with open(prompt_file, "w") as f:
                f.write(idea)
        return session

    def append_clarification(self, session_id: str, content: str) -> None:
        """Append to clarification transcript."""
        transcript_file = self._transcripts_dir(session_id) / "clarification.md"
        with open(transcript_file, "a") as f:
            f.write(content + "\n\n")

    def append_debate(self, session_id: str, content: str) -> None:
        """Append to debate transcript."""
        transcript_file = self._transcripts_dir(session_id) / "debate.md"
        with open(transcript_file, "a") as f:
            f.write(content + "\n\n")

    def append_review(self, session_id: str, content: str) -> None:
        """Append to review transcript."""
        transcript_file = self._transcripts_dir(session_id) / "review.md"
        with open(transcript_file, "a") as f:
            f.write(content + "\n\n")

    def save_messages(self, session_id: str, phase: str, messages: list[AgentMessage]) -> None:
        """Save messages for a phase."""
        messages_file = self._metadata_dir(session_id) / f"{phase}_messages.json"
        existing = []
        if messages_file.exists():
            with open(messages_file, "r") as f:
                existing = json.load(f)
        existing.extend([m.model_dump(mode="json") for m in messages])
        with open(messages_file, "w") as f:
            json.dump(existing, f, default=str, indent=2)

    def get_messages(self, session_id: str, phase: str) -> list[AgentMessage]:
        """Get messages for a phase."""
        messages_file = self._metadata_dir(session_id) / f"{phase}_messages.json"
        if not messages_file.exists():
            return []
        with open(messages_file, "r") as f:
            data = json.load(f)
        return [AgentMessage(**m) for m in data]

    def save_scores(self, session_id: str, scores: dict) -> None:
        """Save judge scores."""
        scores_file = self._metadata_dir(session_id) / "scores.json"
        with open(scores_file, "w") as f:
            json.dump(scores, f, indent=2)

    def save_prd(self, session_id: str, prd_content: str) -> None:
        """Save the generated PRD."""
        prd_file = self._session_dir(session_id) / "PRD.md"
        with open(prd_file, "w") as f:
            f.write(prd_content)

    def save_readme(self, session_id: str, readme_content: str) -> None:
        """Save the README."""
        readme_file = self._session_dir(session_id) / "README.md"
        with open(readme_file, "w") as f:
            f.write(readme_content)

    def get_session_dir(self, session_id: str) -> Path:
        """Get the session directory path."""
        return self._session_dir(session_id)

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        return self._session_file(session_id).exists()

    def list_sessions(self) -> list[str]:
        """List all session IDs."""
        return [
            d.name for d in self.storage_path.iterdir()
            if d.is_dir() and (d / "session.json").exists()
        ]


# Global store instance
conversation_store = ConversationStore()
