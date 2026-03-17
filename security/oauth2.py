# security/security.py
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
import jwt

from security.token_jwt import SECRET_KEY, ALGORITHM
from models.user_models import User
from database import get_session




# ──────────────────────────────
# Bearer auth (only token in docs)
# ──────────────────────────────
bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Session = Depends(get_session),
) -> User:
    token = credentials.credentials  # the raw JWT string: "eyJhbGciOiJIUzI1NiIsInR5cCI6..."

    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise cred_exc
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise cred_exc

    user = db.exec(select(User).where(User.username == username)).first()
    if not user:
        raise cred_exc

    # you can also check if user.is_active here again if you want
    return user