"""Configuration settings for ArchitX backend."""

from pydantic_settings import BaseSettings
from typing import Literal
import os


class Settings(BaseSettings):
    """Application settings."""

    # API
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # LLM
    model_provider: Literal["openai", "azure", "anthropic"] = "openai"
    model_name: str = "gpt-4o"
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

    # JWT Settings
    jwt_secret_key: str = "your-secure-32-char-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24

    # Frontend URL (for OAuth redirect)
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.storage_path, exist_ok=True)
os.makedirs(settings.users_storage_path, exist_ok=True)
