from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from app.db import models
from app.db.session import get_db


router = APIRouter()


class CompanyCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CompanyOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("/", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_company(data: CompanyCreate, db: Session = Depends(get_db)):
    company = models.Company(name=data.name, description=data.description)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/", response_model=List[CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    return db.query(models.Company).all()


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
