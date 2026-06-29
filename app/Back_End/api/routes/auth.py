from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.Back_End.core.security import create_access_token, hash_password, verify_password
from app.Back_End.db import models
from app.Back_End.db.session import get_db
from app.Back_End.dependencies import get_current_user
from app.Back_End.schemas.auth import Token, UserCreate, UserOut, RoleUpdate


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
        db.query(models.User)
        .filter(models.User.email == user_data.email)
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = models.User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=(user_data.role or "employee"),
        company_id=user_data.company_id,
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
        db.query(models.User)
        .filter(models.User.email == form_data.username)
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
def me(current_user: models.User = Depends(get_current_user)):
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
    current_user: models.User = Depends(get_current_user),
):
    """
    Update a user's role (admin only).
    
    Only users with 'admin' role can update other users' roles.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can change roles")

    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = data.role
    db.commit()
    db.refresh(user)
    return user
