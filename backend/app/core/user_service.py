from typing import Annotated, Optional

from fastapi import Depends

from app.crud.user import UserRepositoryDependency
from app.schemas.user import UserCreate, User


class UserService:
    def __init__(self, user_repository: UserRepositoryDependency):
        self.user_repository = user_repository

    async def create_user(self, user: UserCreate) -> User:
        db_user = await self.user_repository.create_user(user=user)
        return User.model_validate(db_user)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        db_user = await self.user_repository.get_user_by_email(email=email)
        if db_user:
            return User.model_validate(db_user)
        return None



UserServiceDependency = Annotated[UserService, Depends(UserService)]
