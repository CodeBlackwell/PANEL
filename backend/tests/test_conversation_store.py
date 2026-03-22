"""Test conversation store."""

import os
import tempfile
import pytest

# Override storage before import
_tmp = tempfile.mkdtemp()
os.environ["STORAGE_PATH"] = _tmp

from app.services.conversation_store import ConversationStore
from app.models import SessionPhase


@pytest.fixture
def store(tmp_path):
    return ConversationStore(storage_path=str(tmp_path))


def test_create_session(store):
    session = store.create_session()
    assert session.phase == SessionPhase.CREATED
    assert store.session_exists(session.id)


def test_save_and_get_session(store):
    session = store.create_session()
    session.idea = "Build a test app"
    session.phase = SessionPhase.IDEA_SUBMITTED
    store.save_session(session)

    loaded = store.get_session(session.id)
    assert loaded.idea == "Build a test app"
    assert loaded.phase == SessionPhase.IDEA_SUBMITTED


def test_get_nonexistent_session(store):
    assert store.get_session("nonexistent") is None


def test_save_idea(store):
    session = store.create_session()
    store.save_idea(session.id, "A great idea for a project")
    loaded = store.get_session(session.id)
    assert loaded.idea == "A great idea for a project"
    assert loaded.phase == SessionPhase.IDEA_SUBMITTED

    # Check original_prompt.txt was created
    prompt_file = store.get_session_dir(session.id) / "original_prompt.txt"
    assert prompt_file.exists()
    assert prompt_file.read_text() == "A great idea for a project"


def test_append_transcripts(store):
    session = store.create_session()
    store.append_clarification(session.id, "Q: What is the goal?")
    store.append_debate(session.id, "Architect: I propose microservices")
    store.append_review(session.id, "Judge: Score 8/10")

    transcripts_dir = store.get_session_dir(session.id) / "transcripts"
    assert (transcripts_dir / "clarification.md").exists()
    assert (transcripts_dir / "debate.md").exists()
    assert (transcripts_dir / "review.md").exists()


def test_save_prd(store):
    session = store.create_session()
    store.save_prd(session.id, "# My PRD\n\nContent here")
    prd_file = store.get_session_dir(session.id) / "PRD.md"
    assert prd_file.exists()
    assert "My PRD" in prd_file.read_text()


def test_list_sessions(store):
    s1 = store.create_session()
    s2 = store.create_session()
    sessions = store.list_sessions()
    assert s1.id in sessions
    assert s2.id in sessions


def test_save_scores(store):
    session = store.create_session()
    scores = {"average_score": 7.5, "verdict": "Good"}
    store.save_scores(session.id, scores)

    scores_file = store.get_session_dir(session.id) / "metadata" / "scores.json"
    assert scores_file.exists()
