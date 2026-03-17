from typing import List, Optional
from sqlmodel import Relationship, SQLModel, Field

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.request_models import MedicineRequestItem

class medicine_model(SQLModel, table=True):
    __tablename__ = "medicines"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    request_items: List["MedicineRequestItem"] = Relationship(back_populates="medicine")
