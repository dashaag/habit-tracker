from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import IdBase # Use IdBase for the primary key

class Role(IdBase):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role {self.name}>"
