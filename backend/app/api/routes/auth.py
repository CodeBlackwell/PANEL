"""Authentication routes for GitHub OAuth."""

import json
import secrets
import logging
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
import httpx

from ...config import settings
from ...models import User, UserPublic, TokenResponse
from ...services.user_store import user_store
from ...services.auth_service import auth_service
from ..dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

# File-based OAuth state store (survives restarts)
_OAUTH_STATE_FILE = Path(settings.storage_path) / ".oauth_states.json"
_STATE_TTL_MINUTES = 10


def _load_oauth_states() -> dict[str, str]:
    """Load OAuth states from disk, pruning expired entries."""
    if not _OAUTH_STATE_FILE.exists():
        return {}
    try:
        with open(_OAUTH_STATE_FILE, "r") as f:
            states = json.load(f)
        cutoff = (datetime.utcnow() - timedelta(minutes=_STATE_TTL_MINUTES)).isoformat()
        return {k: v for k, v in states.items() if v > cutoff}
    except Exception:
        return {}


def _save_oauth_states(states: dict[str, str]) -> None:
    """Save OAuth states to disk."""
    _OAUTH_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_OAUTH_STATE_FILE, "w") as f:
        json.dump(states, f)


@router.get("/github/login")
async def github_login():
    """
    Initiate GitHub OAuth flow.
    Redirects user to GitHub authorization page.
    """
    if not settings.github_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth not configured",
        )

    # Generate state for CSRF protection (persisted to disk)
    state = secrets.token_urlsafe(32)
    states = _load_oauth_states()
    states[state] = datetime.utcnow().isoformat()
    _save_oauth_states(states)

    # Build GitHub authorization URL
    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": settings.github_redirect_uri,
        "scope": "read:user repo",
        "state": state,
    }

    github_auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(url=github_auth_url)


@router.get("/github/callback")
async def github_callback(code: str, state: str):
    """
    Handle GitHub OAuth callback.
    Exchanges code for access token and creates/updates user.
    Redirects to frontend with JWT token.
    """
    # Verify state for CSRF protection (from disk)
    states = _load_oauth_states()
    if state not in states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter",
        )
    del states[state]
    _save_oauth_states(states)

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": settings.github_redirect_uri,
            },
            headers={"Accept": "application/json"},
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token",
            )

        token_data = token_response.json()
        if "error" in token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=token_data.get("error_description", "OAuth error"),
            )

        github_access_token = token_data["access_token"]

        # Get user info from GitHub
        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {github_access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from GitHub",
            )

        github_user = user_response.json()

        # Get user email if not public
        email = github_user.get("email")
        if not email:
            emails_response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {github_access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            if emails_response.status_code == 200:
                emails = emails_response.json()
                primary_email = next(
                    (e["email"] for e in emails if e.get("primary")),
                    None,
                )
                email = primary_email

    # Create or update user
    user = user_store.create_or_update_user(
        github_id=github_user["id"],
        username=github_user["login"],
        email=email,
        avatar_url=github_user.get("avatar_url"),
        github_access_token=github_access_token,
    )

    # Create JWT token
    jwt_token = auth_service.create_access_token(user)

    # Redirect to frontend with token
    frontend_callback_url = f"{settings.frontend_url}/auth/callback?token={jwt_token}"
    return RedirectResponse(url=frontend_callback_url)


@router.get("/me", response_model=UserPublic)
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get the current authenticated user's information."""
    return auth_service.get_user_public(user)


@router.post("/logout")
async def logout(user: User = Depends(get_current_user)):
    """
    Logout the current user.
    Note: JWT tokens are stateless, so this is mostly symbolic.
    The frontend should clear the token from storage.
    """
    return {"message": "Logged out successfully"}
