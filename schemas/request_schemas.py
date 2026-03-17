from typing import Optional, List
from pydantic import BaseModel, field_validator
from datetime import datetime

from sqlmodel import SQLModel


# -------------------- BASE VALIDATOR --------------------

class EmptyStringToNoneModel(SQLModel):

    @field_validator("*", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

class MedicineItemCreate(EmptyStringToNoneModel):
    medicine_id: int
    quantity: int
    frequency: Optional[str] = None


class MedicineRequestCreate(EmptyStringToNoneModel):
    patient_id: int
    patient_name: str
    department: str
    bed_no: Optional[str] = None
    notes: Optional[str] = None
    medicines: List[MedicineItemCreate]


class MedicineItemResponse(EmptyStringToNoneModel):
    medicine_id: int
    quantity: int
    frequency: Optional[str]

class UserResponseForBackPopulates(EmptyStringToNoneModel):
    name: Optional[str]

class MedicineRequestResponse(EmptyStringToNoneModel):
    id: int
    patient_id: int
    patient_name: str
    department: str
    bed_no: Optional[str]
    status: str
    out_of_stock_items: Optional[List[str]] = None
    created_at: datetime
    items: List[MedicineItemResponse]
    created_by: Optional[UserResponseForBackPopulates]
    cancelled_by: Optional[UserResponseForBackPopulates]
    status_updated_by: Optional[UserResponseForBackPopulates]


    class Config:
        from_attributes = True



class MedicineRequestResponseCancel(EmptyStringToNoneModel):
    status: str
    out_of_stock_items: Optional[List[str]] = None



class MedicineRequestPaginatedResponse(SQLModel):
    data: List[MedicineRequestResponse]
    total: int