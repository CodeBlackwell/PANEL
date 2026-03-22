"""Configuration settings for PANEL backend."""

import secrets
from pydantic_settings import BaseSettings
from typing import Literal
import os


def _generate_default_secret() -> str:
    """Generate a random secret key if none is configured."""
    return secrets.token_urlsafe(32)


class Settings(BaseSettings):
    """Application settings."""

    # API
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Rate limiting
    rate_limit_per_minute: int = 30

    # LLM — strong model for high-leverage tasks (PRD drafting, moderator)
    model_provider: Literal["openai", "azure", "anthropic"] = "openai"
    model_name: str = "gpt-4o"
    # Fast model for bulk tasks (clarification, debate agents, judges)
    model_name_fast: str = "gpt-4o-mini"
    openai_api_key: str = ""

    # Debate Configuration
    default_debate_rounds: int = 5
    min_debate_rounds: int = 3
    max_debate_rounds: int = 15
    max_clarification_rounds: int = 10

    # Storage
    storage_path: str = "./sessions"
    users_storage_path: str = "./users"

    # Session
    session_timeout_minutes: int = 60

    # GitHub OAuth
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://localhost:8000/api/v1/auth/github/callback"

    # JWT Settings — auto-generates a secure key if not set via env
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24

    # Token encryption key for GitHub access tokens (Fernet)
    token_encryption_key: str = ""

    # Frontend URL (for OAuth redirect)
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def model_post_init(self, __context) -> None:
        """Generate secrets at startup if not provided."""
        if not self.jwt_secret_key:
            self.jwt_secret_key = _generate_default_secret()
        if not self.token_encryption_key:
            from cryptography.fernet import Fernet
            self.token_encryption_key = Fernet.generate_key().decode()


settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.storage_path, exist_ok=True)
os.makedirs(settings.users_storage_path, exist_ok=True)
