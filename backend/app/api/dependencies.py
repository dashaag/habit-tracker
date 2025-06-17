from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

from app.core.config import settings
from app.crud.user import UserRepositoryDependency
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import SessionLocal # Assuming SessionLocal is your async session maker
from app.schemas import TokenData, User

# This tells FastAPI where to look for the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    user_repo: UserRepositoryDependency,
    token: str = Depends(oauth2_scheme),
) -> User:
    """Dependency to get the current user from a JWT token."""
    print(f"[DEBUG] Received token in get_current_user: {token[:20]}...{token[-20:] if len(token) > 40 else ''}") # Log snippet
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        print(f"[DEBUG] Decoded payload: {payload}")
        user_id_from_sub: str = payload.get("sub")
        print(f"[DEBUG] User ID from 'sub' claim (str): '{user_id_from_sub}'")
        if user_id_from_sub is None:
            print("[DEBUG] 'sub' claim is None. Raising credentials_exception.")
            raise credentials_exception
        
        # Pydantic will attempt to convert user_id_from_sub (str) to int for TokenData.user_id.
        # If conversion fails, a ValidationError is raised.
        print(f"[DEBUG] Attempting to create TokenData with user_id_from_sub: '{user_id_from_sub}'")
        token_data = TokenData(user_id=user_id_from_sub)
        print(f"[DEBUG] TokenData created: user_id={token_data.user_id}, type={type(token_data.user_id)}")

    except JWTError as exc:
        print(f"[DEBUG] JWTError during token decoding: {exc}. Raising credentials_exception.")
        raise credentials_exception from exc
    except ValidationError as exc:
        print(f"[DEBUG] ValidationError creating TokenData (user_id='{user_id_from_sub}'): {exc}. Raising credentials_exception.")
        raise credentials_exception from exc
    except Exception as exc: # Catch any other unexpected error during token processing
        print(f"[DEBUG] Unexpected error during token processing: {exc}. Raising credentials_exception.")
        raise credentials_exception from exc
    
    print(f"[DEBUG] Attempting to fetch user from DB with ID: {token_data.user_id} (type: {type(token_data.user_id)})")
    user = await user_repo.get_user_by_id(user_id=token_data.user_id)
    print(f"[DEBUG] User fetched from DB: {'User object' if user else 'None'}") # Avoid printing sensitive user data
    if user is None:
        print("[DEBUG] User not found in DB for ID. Raising credentials_exception.")
        raise credentials_exception
    
    return user

async def get_db_session() -> AsyncSession:
    """Dependency to get an async database session."""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to get the current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
