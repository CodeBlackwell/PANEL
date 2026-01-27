"""User models for authentication."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class User(BaseModel):
    """User model stored in the database."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    github_id: int
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    github_access_token: str  # Encrypted in storage
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserPublic(BaseModel):
    """Public user information returned to frontend."""
    id: str
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # User ID
    exp: datetime
    iat: datetime


class TokenResponse(BaseModel):
    """Response containing JWT token."""
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
