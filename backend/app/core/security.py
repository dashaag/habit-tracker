from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# It's recommended to use a robust hashing algorithm like bcrypt.
# The 'schemes' list defines the hashing algorithms to be used.
# 'deprecated="auto"' will automatically mark older hashes for re-hashing upon verification.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hashes a password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def _create_token(subject: Union[str, Any], expires_delta: timedelta, token_type: str = "access") -> str:
    """Helper function to create a token."""
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": token_type}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_access_token(subject: Union[str, Any]) -> str:
    """Creates a JWT access token."""
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(subject, expires_delta, token_type="access")

def create_refresh_token(subject: Union[str, Any]) -> str:
    """Creates a JWT refresh token."""
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(subject, expires_delta, token_type="refresh")

def verify_token(token: str) -> dict | None:
    """Verifies a JWT token and returns its payload if valid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
