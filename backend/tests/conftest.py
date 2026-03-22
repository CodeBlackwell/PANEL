"""Shared test fixtures."""

import os
import tempfile
import pytest
from pathlib import Path

# Set test env vars before importing app code
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("STORAGE_PATH", tempfile.mkdtemp())
os.environ.setdefault("USERS_STORAGE_PATH", tempfile.mkdtemp())


@pytest.fixture
def tmp_storage(tmp_path):
    """Provide a temporary storage directory."""
    return tmp_path


@pytest.fixture
def app_client():
    """Create a FastAPI test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)
