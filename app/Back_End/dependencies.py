import uuid # Import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.Back_End.core.security import decode_access_token
# Import the User model from data_analysis models
from app.Back_End.models.data_analysis.user import User as DataAnalysisUser 
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
) -> DataAnalysisUser: # Update return type hint
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id_str = payload.get("sub")
        print(f"DEBUG: get_current_user - payload['sub']: {user_id_str}") # DEBUG
        if user_id_str is None:
            raise credentials_error
        user_id = uuid.UUID(user_id_str) # Parse as UUID
        print(f"DEBUG: get_current_user - user_id (UUID): {user_id}") # DEBUG
    except Exception as e:
        print(f"DEBUG: get_current_user - Error decoding token or parsing user_id: {e}") # DEBUG
        raise credentials_error

    user = db.query(DataAnalysisUser).filter(DataAnalysisUser.id == user_id).first() # Use DataAnalysisUser
    if user is None:
        print(f"DEBUG: get_current_user - User with ID {user_id} not found in DB.") # DEBUG
        raise credentials_error
    print(f"DEBUG: get_current_user - User found: {user.email}") # DEBUG

    return user


def require_roles(roles):
    def role_checker(current_user: DataAnalysisUser = Depends(get_current_user)): # Update type hint
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker