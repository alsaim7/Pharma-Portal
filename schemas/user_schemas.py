from sqlmodel import SQLModel
from typing import Optional

class LoginSchema(SQLModel):
    username: str
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(SQLModel):
    username: Optional[str] = None
    user_id: Optional[int] = None

class UserPublic(SQLModel):
    id: int
    username: str