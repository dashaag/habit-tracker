from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.crud.user import UserRepositoryDependency
from app.crud.role import RoleRepositoryDependency
from app.schemas import User, UserCreate, Token
from app.core.security import create_access_token, create_refresh_token, verify_password, verify_token
from app.core.config import settings
from app.api.dependencies import get_current_active_user
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") # tokenUrl can be any valid path for token acquisition

router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    user_repo: UserRepositoryDependency,
    role_repo: RoleRepositoryDependency,
):
    """Register a new user."""
    # Check if user already exists
    existing_user = await user_repo.get_user_by_email(email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    
    # Assign default 'User' role if not specified
    if user_in.role_id is None:
        user_role = await role_repo.get_role_by_name(name="User")
        if not user_role:
            # This case should ideally not happen if seeder runs correctly
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default user role not found. Please contact an administrator.",
            )
        user_in.role_id = user_role.id

    user = await user_repo.create_user(user_data=user_in)
    return user

@router.post("/login", response_model=Token)
async def login_for_access_token(
    user_repo: UserRepositoryDependency,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """Authenticate user and return a JWT access token."""
    user = await user_repo.get_user_by_email(email=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Fetch the current logged in user."""
    return current_user


@router.post("/refresh_token", response_model=Token)
async def refresh_access_token(token: str = Depends(oauth2_scheme)):
    """Refresh an access token using a refresh token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token)
    if not payload or payload.get("type") != "refresh":
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Generate new access token (refresh token remains the same for this flow)
    new_access_token = create_access_token(subject=user_id)
    
    # For simplicity, we return the original refresh token. 
    # A more robust system might issue a new refresh token and invalidate the old one (rotation).
    return {
        "access_token": new_access_token,
        "refresh_token": token, # Returning the same refresh token
        "token_type": "bearer",
    }
