from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import uuid

# Import the User model from data_analysis models
from app.Back_End.models.data_analysis.user import User as DataAnalysisUser
from app.Back_End.core.security import create_access_token, hash_password, verify_password, decode_access_token
from app.Back_End.db.session import get_db
from app.Back_End.dependencies import get_current_user
from app.Back_End.schemas.auth import Token, UserCreate, UserOut, RoleUpdate, ForgotPasswordRequest, ResetPasswordRequest
from app.Back_End.services.email_service import send_password_reset_email
from app.Back_End.core.config import settings


router = APIRouter(tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Email already registered"},
    }
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with email and password.
    
    - **email**: User's email address (must be unique)
    - **password**: User's password
    - **full_name**: User's full name (optional)
    - **role**: User role - 'employee' (default), 'manager', or 'admin'
    - **company_id**: Associated company ID (optional)
    """
    existing_user = (
        db.query(DataAnalysisUser) # Use DataAnalysisUser
        .filter(DataAnalysisUser.email == user_data.email)
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = DataAnalysisUser( # Use DataAnalysisUser
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=(user_data.role or "employee"),
        # company_id is not part of DataAnalysisUser, removed
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    responses={
        200: {"description": "Login successful, returns JWT token"},
        401: {"description": "Incorrect email or password"},
    }
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password to get JWT access token.
    
    Returns a Bearer token that must be included in Authorization header for protected endpoints.
    
    - **username**: User's email address
    - **password**: User's password
    """
    user = (
        db.query(DataAnalysisUser) # Use DataAnalysisUser
        .filter(DataAnalysisUser.email == form_data.username)
        .first()
    )
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": str(user.id)})

    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user profile",
    responses={
        200: {"description": "Current user information"},
        401: {"description": "Not authenticated"},
    }
)
def me(current_user: DataAnalysisUser = Depends(get_current_user)): # Use DataAnalysisUser
    """
    Get the profile of the currently logged-in user.
    
    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.patch(
    "/role",
    response_model=UserOut,
    summary="Update user role",
    responses={
        200: {"description": "User role updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Only admins can change roles"},
        404: {"description": "User not found"},
    }
)
def update_role(
    data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: DataAnalysisUser = Depends(get_current_user), # Use DataAnalysisUser
):
    """
    Update a user's role (admin only).
    
    Only users with 'admin' role can update other users' roles.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can change roles")

    user = db.query(DataAnalysisUser).filter(DataAnalysisUser.id == data.user_id).first() # Use DataAnalysisUser
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = data.role
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/forgot-password",
    summary="Request password reset email",
    responses={
        200: {"description": "Reset link sent if email is registered"},
    }
)
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request a password reset link. If the email is registered,
    a reset link is sent. Always returns the same message to
    avoid revealing whether an email is registered.
    """
    user = db.query(DataAnalysisUser).filter(DataAnalysisUser.email == data.email).first()
    if user:
        reset_token = create_access_token(
            {"sub": str(user.id)},
            expires_minutes=30,
            token_type="password_reset",
        )
        frontend_url = getattr(settings, "base_url", "http://localhost:5173").replace(":8000", ":5173")
        reset_link = f"{frontend_url}/?reset_token={reset_token}"
        send_password_reset_email(data.email, reset_link)

    return {"message": "If the email is registered, a password reset link has been sent."}


@router.post(
    "/reset-password",
    summary="Reset password using token",
    responses={
        200: {"description": "Password reset successfully"},
        400: {"description": "Invalid or expired token"},
    }
)
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset the password using a valid reset token received via email.
    The token expires after 30 minutes or once used.
    """
    try:
        payload = decode_access_token(data.token)
        if payload.get("type") != "password_reset":
            raise ValueError("Invalid token type")
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, Exception):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user = db.query(DataAnalysisUser).filter(DataAnalysisUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user.hashed_password = hash_password(data.password)
    db.commit()

    return {"message": "Password reset successfully."}


# ---------------------------------------------------------------------
# Admin endpoints for user management
# ---------------------------------------------------------------------

from pydantic import BaseModel


class UserAdminOut(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    role: str
    is_active: bool
    session_count: int = 0

    class Config:
        from_attributes = True


class SessionAdminOut(BaseModel):
    id: str
    title: str
    created_at: str | None = None
    message_count: int = 0

    class Config:
        from_attributes = True


@router.get(
    "/admin/users",
    response_model=list[UserAdminOut],
    summary="List all users (admin only)",
)
def admin_list_users(
    db: Session = Depends(get_db),
    current_user: DataAnalysisUser = Depends(get_current_user),
):
    if current_user.role not in ("admin", "COMPANY_ADMIN"):
        raise HTTPException(status_code=403, detail="Admin access required")
    users = db.query(DataAnalysisUser).all()
    result = []
    for u in users:
        result.append(UserAdminOut(
            id=str(u.id),
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            is_active=u.is_active,
            session_count=len(u.sessions),
        ))
    return result


@router.get(
    "/admin/data",
    response_model=dict,
    summary="View all users and their chat data (admin only)",
)
def admin_view_all_data(
    db: Session = Depends(get_db),
    current_user: DataAnalysisUser = Depends(get_current_user),
):
    if current_user.role not in ("admin", "COMPANY_ADMIN"):
        raise HTTPException(status_code=403, detail="Admin access required")

    from app.Back_End.models.data_analysis.chat_session import ChatSession
    from app.Back_End.models.data_analysis.message import Message

    users_data = []
    users = db.query(DataAnalysisUser).all()
    for u in users:
        sessions = db.query(ChatSession).filter(ChatSession.user_id == u.id).all()
        sessions_data = []
        for s in sessions:
            messages = db.query(Message).filter(Message.session_id == s.id).order_by(Message.seq).all()
            sessions_data.append({
                "session_id": str(s.id),
                "title": s.title,
                "created_at": str(s.created_at) if s.created_at else None,
                "message_count": len(messages),
                "messages": [
                    {
                        "seq": m.seq,
                        "role": m.role,
                        "content_preview": m.content[:200] if m.content else None,
                        "created_at": str(m.created_at) if m.created_at else None,
                    }
                    for m in messages
                ],
            })
        users_data.append({
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "session_count": len(sessions),
            "sessions": sessions_data,
        })

    return {"users": users_data}


@router.delete(
    "/admin/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user and all their data (admin only)",
)
def admin_delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: DataAnalysisUser = Depends(get_current_user),
):
    if current_user.role not in ("admin", "COMPANY_ADMIN"):
        raise HTTPException(status_code=403, detail="Admin access required")
    user = db.query(DataAnalysisUser).filter(DataAnalysisUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()


@router.get(
    "/admin/users/{user_id}/sessions",
    response_model=list[SessionAdminOut],
    summary="View a user's chat sessions (admin only)",
)
def admin_user_sessions(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: DataAnalysisUser = Depends(get_current_user),
):
    if current_user.role not in ("admin", "COMPANY_ADMIN"):
        raise HTTPException(status_code=403, detail="Admin access required")
    user = db.query(DataAnalysisUser).filter(DataAnalysisUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = []
    for s in user.sessions:
        result.append(SessionAdminOut(
            id=str(s.id),
            title=s.title,
            created_at=str(s.created_at) if s.created_at else None,
            message_count=len(s.messages),
        ))
    return result