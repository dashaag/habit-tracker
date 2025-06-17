from typing import Optional

from pydantic import EmailStr, Field

from app.schemas.base import CustomBaseModel, IdSchema, TimestampSchema
from app.schemas.role import Role  # For nesting in User response

# Base schema for User, common attributes
class UserBase(CustomBaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

# Schema for creating a User (inherits from UserBase)
class UserCreate(UserBase):
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    role_id: Optional[int] = None # Optional: assign a default role if not provided

# Schema for updating a User (all fields optional)
class UserUpdate(CustomBaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None
    # Password updates should be handled by a separate dedicated endpoint for security

# Schema for representing a User in API responses (includes ID, timestamps, and Role info)
class User(UserBase, IdSchema, TimestampSchema):
    role: Optional[Role] = None # Nested Role schema

# Schema for user in DB (includes password_hash)
class UserInDB(UserBase, IdSchema, TimestampSchema):
    password_hash: str
    role_id: Optional[int] = None
