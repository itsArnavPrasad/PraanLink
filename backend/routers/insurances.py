from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from db.database import get_db
from db.models import Insurance
from schemas import InsuranceSchema
from marshmallow import ValidationError

router = APIRouter(prefix="/api/insurances", tags=["insurances"])
schema = InsuranceSchema()
schemas = InsuranceSchema(many=True)


@router.get("", response_model=dict)
def get_all_insurances(db: Session = Depends(get_db)):
    """Get all insurances"""
    insurances = db.query(Insurance).all()
    return {"data": schemas.dump(insurances)}


@router.get("/{insurance_id}", response_model=dict)
def get_insurance(insurance_id: int, db: Session = Depends(get_db)):
    """Get insurance by ID"""
    insurance = db.query(Insurance).filter(Insurance.id == insurance_id).first()
    if not insurance:
        raise HTTPException(status_code=404, detail="Insurance not found")
    return {"data": schema.dump(insurance)}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_insurance(insurance_data: Dict[Any, Any] = Body(...), db: Session = Depends(get_db)):
    """Create a new insurance"""
    try:
        validated_data = schema.load(insurance_data)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=err.messages)
    
    insurance = Insurance(**validated_data)
    db.add(insurance)
    db.commit()
    db.refresh(insurance)
    return {"data": schema.dump(insurance), "message": "Insurance created successfully"}


@router.put("/{insurance_id}", response_model=dict)
def update_insurance(insurance_id: int, insurance_data: Dict[Any, Any] = Body(...), db: Session = Depends(get_db)):
    """Update an insurance"""
    insurance = db.query(Insurance).filter(Insurance.id == insurance_id).first()
    if not insurance:
        raise HTTPException(status_code=404, detail="Insurance not found")
    
    try:
        validated_data = schema.load(insurance_data, partial=True)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=err.messages)
    
    for key, value in validated_data.items():
        setattr(insurance, key, value)
    
    db.commit()
    db.refresh(insurance)
    return {"data": schema.dump(insurance), "message": "Insurance updated successfully"}


@router.delete("/{insurance_id}", response_model=dict)
def delete_insurance(insurance_id: int, db: Session = Depends(get_db)):
    """Delete an insurance"""
    insurance = db.query(Insurance).filter(Insurance.id == insurance_id).first()
    if not insurance:
        raise HTTPException(status_code=404, detail="Insurance not found")
    
    db.delete(insurance)
    db.commit()
    return {"message": "Insurance deleted successfully"}

