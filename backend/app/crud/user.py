from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import SessionContext
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

class UserRepository:
    def __init__(self, session: SessionContext):
        self.session = session

    async def create_user(self, user_data: UserCreate) -> User:
        db_user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            is_active=user_data.is_active if user_data.is_active is not None else True,
            role_id=user_data.role_id,
            full_name=user_data.full_name
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        # Re-fetch the user to ensure all relationships, like role, are eagerly loaded
        if db_user.id is not None:
            loaded_user = await self.get_user_by_id(db_user.id)
            if loaded_user:
                return loaded_user
        return db_user # Fallback, though ideally loaded_user is always found

    async def get_user_by_id(self, user_id: int) -> User | None:
        query = select(User).options(selectinload(User.role)).filter(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).options(selectinload(User.role)).filter(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


UserRepositoryDependency = Annotated[UserRepository, Depends(UserRepository)]

