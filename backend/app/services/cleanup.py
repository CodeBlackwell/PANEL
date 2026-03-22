"""Session cleanup service for expired sessions."""

import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from ..config import settings

logger = logging.getLogger(__name__)


def cleanup_expired_sessions() -> int:
    """Remove sessions older than session_timeout_minutes. Returns count of removed sessions."""
    storage = Path(settings.storage_path)
    if not storage.exists():
        return 0

    cutoff = datetime.utcnow() - timedelta(minutes=settings.session_timeout_minutes)
    removed = 0

    for session_dir in storage.iterdir():
        if not session_dir.is_dir():
            continue
        session_file = session_dir / "session.json"
        if not session_file.exists():
            continue
        try:
            mtime = datetime.utcfromtimestamp(session_file.stat().st_mtime)
            if mtime < cutoff:
                shutil.rmtree(session_dir)
                removed += 1
        except Exception as e:
            logger.warning(f"Failed to clean up session {session_dir.name}: {e}")

    if removed:
        logger.info(f"Cleaned up {removed} expired session(s)")

    # Also clean up in-memory session contexts
    try:
        from ..agents.orchestrator import cleanup_stale_contexts
        cleanup_stale_contexts(settings.session_timeout_minutes)
    except ImportError:
        pass

    return removed
