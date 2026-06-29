from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.Back_End.core.security import decode_access_token
from app.Back_End.db import models
from app.Back_End.db.session import get_db
from app.Back_End.db.vector_store import get_vector_store


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_retriever():
    vectorstore = get_vector_store()

    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,
            "fetch_k": 10
        }
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_error
        user_id = int(user_id)
    except Exception:
        raise credentials_error

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_error

    return user
