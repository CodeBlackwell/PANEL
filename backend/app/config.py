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

    # Session
    session_timeout_minutes: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Ensure storage directory exists
os.makedirs(settings.storage_path, exist_ok=True)
