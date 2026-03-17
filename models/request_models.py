from sqlmodel import JSON, Column, Relationship, SQLModel, Field
from typing import List, Optional
from datetime import datetime
import pytz

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.pharmacy_models import medicine_model


def india_datetime():
    return datetime.now(pytz.timezone("Asia/Kolkata"))




class MedicineRequest(SQLModel, table=True):
    __tablename__ = "medicine_requests"

    id: Optional[int] = Field(default=None, primary_key=True)

    patient_id: int
    patient_name: str
    department: str
    bed_no: Optional[str] = None

    notes: Optional[str] = None

    # Status handled by pharmacy later
    status: str = Field(default="pending")
    out_of_stock_items: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSON)
    )

    created_at: datetime = Field(default_factory=india_datetime)

    # Temporary fixed user id
    created_by_user_id: int = Field(default=1)

    items: List["MedicineRequestItem"] = Relationship(back_populates="request")


class MedicineRequestItem(SQLModel, table=True):
    __tablename__ = "medicine_request_items"

    id: Optional[int] = Field(default=None, primary_key=True)

    request_id: int = Field(foreign_key="medicine_requests.id")

    medicine_id: int = Field(foreign_key="medicines.id")

    quantity: int

    frequency: Optional[str] = None

    request: Optional["MedicineRequest"] = Relationship(back_populates="items")

    medicine: Optional["medicine_model"] = Relationship(back_populates="request_items")