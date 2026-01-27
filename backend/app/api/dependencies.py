"""API dependencies for authentication."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..models import User, UserPublic
from ..services.auth_service import auth_service
from ..services.user_store import user_store

# Optional bearer token scheme (doesn't require auth)
optional_bearer = HTTPBearer(auto_error=False)

# Required bearer token scheme (returns 401 if missing)
required_bearer = HTTPBearer(auto_error=True)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
) -> Optional[User]:
    """
    Get the current user from JWT token if provided.
    Returns None if no token is provided (guest mode).
    """
    if not credentials:
        return None

    token = credentials.credentials
    payload = auth_service.verify_token(token)

    if not payload:
        # Invalid/expired token - treat as guest
        return None

    user = user_store.get_user(payload.sub)
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(required_bearer),
) -> User:
    """
    Get the current user from JWT token.
    Raises 401 if token is missing, invalid, or user not found.
    """
    token = credentials.credentials
    payload = auth_service.verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_store.get_user(payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_public(
    user: User = Depends(get_current_user),
) -> UserPublic:
    """Get the current user's public information."""
    return auth_service.get_user_public(user)
