"""File-based user storage."""

import json
import base64
from datetime import datetime
from typing import Optional
from pathlib import Path

from ..config import settings
from ..models import User


class UserStore:
    """File-based storage for users."""

    def __init__(self, storage_path: str = None):
        self.storage_path = Path(storage_path or settings.users_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._index_file = self.storage_path / "index.json"
        self._ensure_index()

    def _ensure_index(self):
        """Ensure the index file exists."""
        if not self._index_file.exists():
            self._save_index({})

    def _load_index(self) -> dict:
        """Load the user index (github_id -> user_id mapping)."""
        if not self._index_file.exists():
            return {}
        with open(self._index_file, "r") as f:
            return json.load(f)

    def _save_index(self, index: dict) -> None:
        """Save the user index."""
        with open(self._index_file, "w") as f:
            json.dump(index, f, indent=2)

    def _user_file(self, user_id: str) -> Path:
        """Get the user file path."""
        return self.storage_path / f"{user_id}.json"

    def _encode_token(self, token: str) -> str:
        """Simple base64 encoding for token storage."""
        return base64.b64encode(token.encode()).decode()

    def _decode_token(self, encoded: str) -> str:
        """Decode base64 encoded token."""
        return base64.b64decode(encoded.encode()).decode()

    def create_or_update_user(
        self,
        github_id: int,
        username: str,
        email: Optional[str],
        avatar_url: Optional[str],
        github_access_token: str,
    ) -> User:
        """Create a new user or update existing one."""
        index = self._load_index()
        github_id_str = str(github_id)

        existing_user_id = index.get(github_id_str)

        if existing_user_id:
            # Update existing user
            user = self.get_user(existing_user_id)
            if user:
                user.username = username
                user.email = email
                user.avatar_url = avatar_url
                user.github_access_token = self._encode_token(github_access_token)
                user.updated_at = datetime.utcnow()
                self._save_user(user)
                return user

        # Create new user
        user = User(
            github_id=github_id,
            username=username,
            email=email,
            avatar_url=avatar_url,
            github_access_token=self._encode_token(github_access_token),
        )

        # Update index
        index[github_id_str] = user.id
        self._save_index(index)

        # Save user
        self._save_user(user)
        return user

    def _save_user(self, user: User) -> None:
        """Save user to file."""
        user_file = self._user_file(user.id)
        with open(user_file, "w") as f:
            json.dump(user.model_dump(mode="json"), f, default=str, indent=2)

    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        user_file = self._user_file(user_id)
        if not user_file.exists():
            return None
        with open(user_file, "r") as f:
            data = json.load(f)
        return User(**data)

    def get_user_by_github_id(self, github_id: int) -> Optional[User]:
        """Get a user by GitHub ID."""
        index = self._load_index()
        user_id = index.get(str(github_id))
        if not user_id:
            return None
        return self.get_user(user_id)

    def get_github_token(self, user_id: str) -> Optional[str]:
        """Get decoded GitHub access token for a user."""
        user = self.get_user(user_id)
        if not user:
            return None
        return self._decode_token(user.github_access_token)

    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        user = self.get_user(user_id)
        if not user:
            return False

        # Remove from index
        index = self._load_index()
        github_id_str = str(user.github_id)
        if github_id_str in index:
            del index[github_id_str]
            self._save_index(index)

        # Remove user file
        user_file = self._user_file(user_id)
        if user_file.exists():
            user_file.unlink()

        return True


# Global store instance
user_store = UserStore()
