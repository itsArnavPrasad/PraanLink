from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from db.database import get_db
from db.models import Prescription
from schemas import PrescriptionSchema
from marshmallow import ValidationError

router = APIRouter(prefix="/api/prescriptions", tags=["prescriptions"])
schema = PrescriptionSchema()
schemas = PrescriptionSchema(many=True)


@router.get("", response_model=dict)
def get_all_prescriptions(db: Session = Depends(get_db)):
    """Get all prescriptions"""
    prescriptions = db.query(Prescription).all()
    return {"data": schemas.dump(prescriptions)}


@router.get("/{prescription_id}", response_model=dict)
def get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    """Get prescription by ID"""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return {"data": schema.dump(prescription)}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_prescription(prescription_data: Dict[Any, Any] = Body(...), db: Session = Depends(get_db)):
    """Create a new prescription"""
    try:
        validated_data = schema.load(prescription_data)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=err.messages)
    
    prescription = Prescription(**validated_data)
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    return {"data": schema.dump(prescription), "message": "Prescription created successfully"}


@router.put("/{prescription_id}", response_model=dict)
def update_prescription(prescription_id: int, prescription_data: Dict[Any, Any] = Body(...), db: Session = Depends(get_db)):
    """Update a prescription"""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    try:
        validated_data = schema.load(prescription_data, partial=True)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=err.messages)
    
    for key, value in validated_data.items():
        setattr(prescription, key, value)
    
    db.commit()
    db.refresh(prescription)
    return {"data": schema.dump(prescription), "message": "Prescription updated successfully"}


@router.delete("/{prescription_id}", response_model=dict)
def delete_prescription(prescription_id: int, db: Session = Depends(get_db)):
    """Delete a prescription"""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    db.delete(prescription)
    db.commit()
    return {"message": "Prescription deleted successfully"}

