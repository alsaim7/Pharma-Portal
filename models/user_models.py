from typing import List, Optional
from sqlmodel import Relationship, SQLModel, UniqueConstraint, Field


from typing import TYPE_CHECKING



if TYPE_CHECKING:
    from models.request_models import MedicineRequest


class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint("username", name="uq_user_username"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None)
    username: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)
    role: str = Field(nullable=False)
    is_active: bool = Field(default=True)

    # 🔥 Reverse relationships
    created_requests: List["MedicineRequest"] = Relationship(
        back_populates="created_by",
        sa_relationship_kwargs={"foreign_keys": "[MedicineRequest.created_by_user_id]"}
    )

    cancelled_requests: List["MedicineRequest"] = Relationship(
        back_populates="cancelled_by",
        sa_relationship_kwargs={"foreign_keys": "[MedicineRequest.cancelled_by_user_id]"}
    )

    updated_requests: List["MedicineRequest"] = Relationship(
        back_populates="status_updated_by",
        sa_relationship_kwargs={"foreign_keys": "[MedicineRequest.status_updated_by_user_id]"}
    )