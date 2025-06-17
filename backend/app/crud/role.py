from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionContext # Assuming SessionContext is your AsyncSession
from app.models.role import Role
# We'll define RoleCreate and Role schemas later
# from app.schemas.role import RoleCreate

class RoleRepository:
    def __init__(self, session: SessionContext):
        self.session = session

    async def create_role(self, role_name: str) -> Role:
        db_role = Role(name=role_name)
        self.session.add(db_role)
        await self.session.commit()
        await self.session.refresh(db_role)
        return db_role

    async def get_role_by_id(self, role_id: int) -> Role | None:
        query = select(Role).filter(Role.id == role_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_role_by_name(self, name: str) -> Role | None:
        query = select(Role).filter(Role.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create_role(self, role_name: str) -> Role:
        role = await self.get_role_by_name(name=role_name)
        if not role:
            role = await self.create_role(role_name=role_name)
        return role


RoleRepositoryDependency = Annotated[RoleRepository, Depends(RoleRepository)]
