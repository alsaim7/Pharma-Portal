from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models.user_models import User
from schemas.user_schemas import LoginSchema, Token
from security.token_jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from security.hashing import verify_password



router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=Token, status_code=status.HTTP_202_ACCEPTED)
def login(req: LoginSchema, db: Session = Depends(get_session)):
    # ✅ Use username instead of email
    user = db.exec(select(User).where(User.username == req.username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Incorrect username or password,  Please contact SDC.")

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password, Please contact SDC.")
    

    # 🚫 Check if the user is deactivated
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated, Please contact SDC."
        )

    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role, "name": user.name},
        expires_delta=expires
    )

    return Token(access_token=token)