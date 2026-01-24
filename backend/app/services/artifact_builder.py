"""Artifact builder for generating ZIP packages."""

import json
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional

from ..config import settings
from .conversation_store import conversation_store


async def build_artifact_zip(session_id: str) -> str:
    """Build a ZIP file with all session artifacts.

    Returns the path to the generated ZIP file.
    """
    session = conversation_store.get_session(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")

    session_dir = conversation_store.get_session_dir(session_id)

    # Create a temporary file for the ZIP
    zip_path = session_dir / f"prd_{session_id}.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add README.md
        readme_path = session_dir / "README.md"
        if readme_path.exists():
            zf.write(readme_path, "README.md")
        else:
            # Generate a basic README if missing
            zf.writestr("README.md", _generate_basic_readme(session_id))

        # Add PRD.md
        prd_path = session_dir / "PRD.md"
        if prd_path.exists():
            zf.write(prd_path, "PRD.md")

        # Add original_prompt.txt
        prompt_path = session_dir / "original_prompt.txt"
        if prompt_path.exists():
            zf.write(prompt_path, "original_prompt.txt")

        # Add transcripts
        transcripts_dir = session_dir / "transcripts"
        if transcripts_dir.exists():
            for transcript_file in transcripts_dir.glob("*.md"):
                zf.write(transcript_file, f"transcripts/{transcript_file.name}")

        # Add metadata
        metadata_dir = session_dir / "metadata"
        if metadata_dir.exists():
            for meta_file in metadata_dir.glob("*.json"):
                zf.write(meta_file, f"metadata/{meta_file.name}")

        # Add session.json
        session_file = session_dir / "session.json"
        if session_file.exists():
            zf.write(session_file, "metadata/session.json")

        # Generate exports
        exports = _generate_exports(session_id)
        zf.writestr("exports/requirements.json", json.dumps(exports["requirements"], indent=2))
        zf.writestr("exports/decisions.json", json.dumps(exports["decisions"], indent=2))

    return str(zip_path)


def _generate_basic_readme(session_id: str) -> str:
    """Generate a basic README if one doesn't exist."""
    return f"""# PRD Package

Session ID: {session_id}
Generated: {datetime.utcnow().isoformat()}

## Contents

- PRD.md - Product Requirements Document
- original_prompt.txt - Original project idea
- transcripts/ - Conversation transcripts
- metadata/ - Session data
- exports/ - Structured data exports
"""


def _generate_exports(session_id: str) -> dict:
    """Generate structured exports from session data."""
    session_dir = conversation_store.get_session_dir(session_id)

    # Try to load scores
    scores_file = session_dir / "metadata" / "scores.json"
    scores = {}
    if scores_file.exists():
        with open(scores_file, "r") as f:
            scores = json.load(f)

    # Try to load PRD content
    prd_path = session_dir / "PRD.md"
    prd_content = ""
    if prd_path.exists():
        with open(prd_path, "r") as f:
            prd_content = f.read()

    # Extract requirements from PRD
    requirements = _extract_requirements(prd_content)

    # Extract decisions
    decisions = _extract_decisions(session_id)

    return {
        "requirements": requirements,
        "decisions": decisions,
    }


def _extract_requirements(prd_content: str) -> dict:
    """Extract structured requirements from PRD content."""
    requirements = {
        "functional": [],
        "non_functional": [],
        "constraints": [],
        "assumptions": [],
    }

    if not prd_content:
        return requirements

    # Simple extraction based on common patterns
    lines = prd_content.split('\n')
    current_section = None

    for line in lines:
        line_lower = line.lower()

        # Detect sections
        if 'functional requirement' in line_lower:
            current_section = 'functional'
        elif 'non-functional' in line_lower or 'nfr' in line_lower:
            current_section = 'non_functional'
        elif 'constraint' in line_lower:
            current_section = 'constraints'
        elif 'assumption' in line_lower:
            current_section = 'assumptions'
        elif line.startswith('##'):
            current_section = None

        # Extract bullet points
        if current_section and line.strip().startswith(('-', '*', '•')):
            item = line.strip().lstrip('-*• ').strip()
            if item and len(item) > 5:
                requirements[current_section].append(item)

    return requirements


def _extract_decisions(session_id: str) -> dict:
    """Extract key decisions from debate transcript."""
    session_dir = conversation_store.get_session_dir(session_id)
    debate_file = session_dir / "transcripts" / "debate.md"

    decisions = {
        "architecture": [],
        "technology": [],
        "security": [],
        "other": [],
    }

    if not debate_file.exists():
        return decisions

    with open(debate_file, "r") as f:
        content = f.read()

    # Simple pattern matching for decisions
    lines = content.split('\n')
    for line in lines:
        line_lower = line.lower()

        if '[agreement]' in line_lower or 'decided' in line_lower or 'agreed' in line_lower:
            decision = line.strip()
            if 'architect' in line_lower or 'design' in line_lower:
                decisions["architecture"].append(decision)
            elif 'tech' in line_lower or 'stack' in line_lower or 'framework' in line_lower:
                decisions["technology"].append(decision)
            elif 'security' in line_lower or 'auth' in line_lower:
                decisions["security"].append(decision)
            else:
                decisions["other"].append(decision)

    return decisions


async def get_artifact_preview(session_id: str, artifact_name: str) -> Optional[str]:
    """Get a preview of a specific artifact."""
    session_dir = conversation_store.get_session_dir(session_id)

    artifact_paths = {
        "prd": session_dir / "PRD.md",
        "readme": session_dir / "README.md",
        "prompt": session_dir / "original_prompt.txt",
        "clarification": session_dir / "transcripts" / "clarification.md",
        "debate": session_dir / "transcripts" / "debate.md",
        "review": session_dir / "transcripts" / "review.md",
    }

    path = artifact_paths.get(artifact_name)
    if path and path.exists():
        with open(path, "r") as f:
            return f.read()

    return None
