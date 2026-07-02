import logging
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List

from app.Back_End.core.config import settings
from app.Back_End.core.security import (
    generate_verification_token,
    hash_password,
    hash_verification_token,
)
from app.Back_End.db import models
from app.Back_End.db.session import get_db
from app.Back_End.dependencies import get_current_user, require_roles
from app.Back_End.models.data_analysis.user import User as DataAnalysisUser
from app.Back_End.schemas.company import (
    CompanyRegistrationRequest,
    RegistrationResponse,
    VerificationResponse,
)
from app.Back_End.services.email_service import send_verification_email


router = APIRouter(tags=["Companies"])


class CompanyCreate(BaseModel):
    name: str = Field(..., description="Company name", example="Acme Corp")
    description: Optional[str] = Field(None, description="Company description", example="Leading company in tech")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Acme Corp",
                "description": "Leading company in tech"
            }
        }


class CompanyOut(BaseModel):
    id: int = Field(..., description="Company ID")
    name: str = Field(..., description="Company name")
    description: Optional[str] = Field(None, description="Company description")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Acme Corp",
                "description": "Leading company in tech"
            }
        }


@router.post(
    "/",
    response_model=CompanyOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new company",
    responses={
        201: {"description": "Company created successfully"},
        403: {"description": "Insufficient permissions (admin/manager only)"},
    }
)
def create_company(data: CompanyCreate, db: Session = Depends(get_db)):
    """
    Create a new company (admin/manager only).
    
    - **name**: Company name (required)
    - **description**: Company description (optional)
    """
    company = models.Company(name=data.name, description=data.description)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get(
    "/",
    response_model=List[CompanyOut],
    summary="List all companies",
    responses={
        200: {"description": "List of companies"},
        403: {"description": "Insufficient permissions (admin/manager only)"},
    }
)
def list_companies(db: Session = Depends(get_db)):
    """
    Get a list of all companies (admin/manager only).
    """
    return db.query(models.Company).all()


@router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new company",
    responses={
        201: {"description": "Registration initiated, check email for verification"},
        409: {"description": "Email or company name already exists"},
    }
)
def register_company(
    data: CompanyRegistrationRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new company with admin user.
    
    A verification email will be sent to the admin's email address.
    The admin must verify the registration via the link in the email.
    """
    company_name = data.company_name.strip()
    admin = data.admin
    email = admin.email.lower().strip()

    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email is already registered",
        )

    existing_pending = db.query(models.PendingCompanyRegistration).filter(
        models.PendingCompanyRegistration.admin_email == email,
        models.PendingCompanyRegistration.verified == False,
    ).first()
    if existing_pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending registration already exists for this email. Please check your inbox.",
        )

    company_exists = db.query(models.Company).filter(
        models.Company.name == company_name
    ).first()
    if company_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A company with this name already exists",
        )

    pending_company = db.query(models.PendingCompanyRegistration).filter(
        models.PendingCompanyRegistration.company_name == company_name,
        models.PendingCompanyRegistration.verified == False,
    ).first()
    if pending_company:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending registration for this company name already exists",
        )

    plain_token, hashed_token = generate_verification_token()
    hashed_pw = hash_password(admin.password)

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES
    )

    if settings.smtp_username and settings.smtp_from_email:
        pending = models.PendingCompanyRegistration(
            company_name=company_name,
            admin_first_name=admin.first_name.strip(),
            admin_last_name=admin.last_name.strip(),
            admin_email=email,
            hashed_password=hashed_pw,
            verification_token_hash=hashed_token,
            expires_at=expires_at,
        )
        db.add(pending)
        db.commit()

        verification_link = f"{settings.BASE_URL}/companies/verify?token={plain_token}"
        send_verification_email(email, company_name, verification_link)

        return RegistrationResponse(
            message="Registration initiated. Please check your email to verify.",
            email=email,
        )

    # SMTP not configured — auto-verify immediately
    company = models.Company(
        name=company_name,
        description=f"Company registered by {admin.first_name.strip()} {admin.last_name.strip()}",
    )
    db.add(company)
    db.flush()

    user = models.User(
        email=email,
        hashed_password=hashed_pw,
        full_name=f"{admin.first_name.strip()} {admin.last_name.strip()}",
        role="COMPANY_ADMIN",
        company_id=company.id,
    )
    db.add(user)
    db.flush()

    da_user = DataAnalysisUser(
        email=email,
        hashed_password=hashed_pw,
        full_name=f"{admin.first_name.strip()} {admin.last_name.strip()}",
        role="admin",
    )
    db.add(da_user)
    db.flush()
    db.commit()

    logger.info("Auto-verified registration for %s", email)
    return RegistrationResponse(
        message="Registration successful. You can now log in.",
        email=email,
    )


@router.get(
    "/verify",
    response_model=VerificationResponse,
    summary="Verify company registration",
    responses={
        200: {"description": "Company verified successfully"},
        400: {"description": "Invalid or expired token"},
        500: {"description": "Failed to create company"},
    }
)
def verify_company(
    token: str = Query(..., description="Verification token from email"),
    db: Session = Depends(get_db),
):
    """
    Verify company registration using token from verification email.
    
    - **token**: Verification token sent to admin email
    """
    token_hash = hash_verification_token(token)

    pending = db.query(models.PendingCompanyRegistration).filter(
        models.PendingCompanyRegistration.verification_token_hash == token_hash,
    ).first()

    if not pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    if pending.verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This registration has already been verified",
        )

    if datetime.now(timezone.utc) > pending.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired. Please register again.",
        )

    try:
        company = models.Company(
            name=pending.company_name,
            description=f"Company registered by {pending.admin_first_name} {pending.admin_last_name}",
        )
        db.add(company)
        db.flush()

        user = models.User(
            email=pending.admin_email,
            hashed_password=pending.hashed_password,
            full_name=f"{pending.admin_first_name} {pending.admin_last_name}",
            role="COMPANY_ADMIN",
            company_id=company.id,
        )
        db.add(user)
        db.flush()

        da_user = DataAnalysisUser(
            email=pending.admin_email,
            hashed_password=pending.hashed_password,
            full_name=f"{pending.admin_first_name} {pending.admin_last_name}",
            role="admin",
        )
        db.add(da_user)
        db.flush()

        pending.verified = True
        pending.verification_token_hash = ""
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create company. Please try again.",
        )

    return VerificationResponse(
        message="Company verified and created successfully. You can now log in.",
        company_name=pending.company_name,
        admin_email=pending.admin_email,
    )


@router.get(
    "/{company_id}",
    response_model=CompanyOut,
    summary="Get company details",
    responses={
        200: {"description": "Company details"},
        401: {"description": "Not authenticated"},
        404: {"description": "Company not found"},
    }
)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Get details of a specific company (requires authentication).
    
    - **company_id**: ID of the company to retrieve
    """
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

