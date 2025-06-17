from fastapi import APIRouter, HTTPException, status
from pydantic import EmailStr

from app.core.user_service import UserServiceDependency
from app.schemas.user import User, UserCreate

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user: UserCreate, user_service: UserServiceDependency
) -> User:
    user_response = await user_service.get_user_by_email(email=user.email)
    if user_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    return await user_service.create_user(user=user)


@router.get("", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(
    user_service: UserServiceDependency, email: EmailStr
) -> User:
    user_response = await user_service.get_user_by_email(email=email)
    if not user_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user_response
