"""Authentication service for JWT handling."""

from datetime import datetime, timedelta
from typing import Optional
import jwt

from ..config import settings
from ..models import User, UserPublic, TokenPayload


class AuthService:
    """Service for JWT token creation and verification."""

    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.expire_hours = settings.jwt_expire_hours

    def create_access_token(self, user: User) -> str:
        """Create a JWT access token for a user."""
        now = datetime.utcnow()
        expire = now + timedelta(hours=self.expire_hours)

        payload = {
            "sub": user.id,
            "iat": now,
            "exp": expire,
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[TokenPayload]:
        """Verify a JWT token and return the payload."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            return TokenPayload(
                sub=payload["sub"],
                exp=datetime.fromtimestamp(payload["exp"]),
                iat=datetime.fromtimestamp(payload["iat"]),
            )
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def get_user_public(self, user: User) -> UserPublic:
        """Convert User to UserPublic."""
        return UserPublic(
            id=user.id,
            username=user.username,
            email=user.email,
            avatar_url=user.avatar_url,
        )


# Global service instance
auth_service = AuthService()
