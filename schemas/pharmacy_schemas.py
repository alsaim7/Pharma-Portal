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



class MedicineRequestResponseStatusChange(EmptyStringToNoneModel):
    status: str
    out_of_stock_items: Optional[List[str]] = None
