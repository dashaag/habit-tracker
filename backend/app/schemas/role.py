from typing import Optional

from app.schemas.base import CustomBaseModel, IdSchema

# Base schema for Role, common attributes
class RoleBase(CustomBaseModel):
    name: str

# Schema for creating a Role (inherits from RoleBase)
class RoleCreate(RoleBase):
    pass

# Schema for updating a Role (inherits from RoleBase, all fields optional)
# For roles, updates might not be common, or might be restricted.
class RoleUpdate(CustomBaseModel):
    name: Optional[str] = None

# Schema for representing a Role in API responses (includes ID)
class Role(RoleBase, IdSchema):
    pass
