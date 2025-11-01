from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from db.database import get_db
from db.models import Hospital
from schemas import HospitalSchema
from marshmallow import ValidationError

router = APIRouter(prefix="/api/hospitals", tags=["hospitals"])
schema = HospitalSchema()
schemas = HospitalSchema(many=True)


@router.get("", response_model=dict)
def get_all_hospitals(db: Session = Depends(get_db)):
    """Get all hospitals"""
    hospitals = db.query(Hospital).all()
    return {"data": schemas.dump(hospitals)}


@router.get("/{hospital_id}", response_model=dict)
def get_hospital(hospital_id: int, db: Session = Depends(get_db)):
    """Get hospital by ID"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return {"data": schema.dump(hospital)}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_hospital(hospital_data: Dict[Any, Any] = Body(...), db: Session = Depends(get_db)):
    """Create a new hospital"""
    try:
        validated_data = schema.load(hospital_data)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=err.messages)
    
    hospital = Hospital(**validated_data)
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return {"data": schema.dump(hospital), "message": "Hospital created successfully"}


@router.put("/{hospital_id}", response_model=dict)
def update_hospital(hospital_id: int, hospital_data: Dict[Any, Any] = Body(...), db: Session = Depends(get_db)):
    """Update a hospital"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    try:
        validated_data = schema.load(hospital_data, partial=True)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=err.messages)
    
    for key, value in validated_data.items():
        setattr(hospital, key, value)
    
    db.commit()
    db.refresh(hospital)
    return {"data": schema.dump(hospital), "message": "Hospital updated successfully"}


@router.delete("/{hospital_id}", response_model=dict)
def delete_hospital(hospital_id: int, db: Session = Depends(get_db)):
    """Delete a hospital"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    db.delete(hospital)
    db.commit()
    return {"message": "Hospital deleted successfully"}

