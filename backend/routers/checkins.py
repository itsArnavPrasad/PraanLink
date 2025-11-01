from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from db.database import get_db
from db.models import CheckIn
from schemas import CheckInSchema
from marshmallow import ValidationError

router = APIRouter(prefix="/api/checkins", tags=["checkins"])
schema = CheckInSchema()
schemas = CheckInSchema(many=True)


@router.get("", response_model=dict)
def get_all_checkins(db: Session = Depends(get_db)):
    """Get all check-ins"""
    checkins = db.query(CheckIn).all()
    return {"data": schemas.dump(checkins)}


@router.get("/{checkin_id}", response_model=dict)
def get_checkin(checkin_id: int, db: Session = Depends(get_db)):
    """Get check-in by ID"""
    checkin = db.query(CheckIn).filter(CheckIn.id == checkin_id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
    return {"data": schema.dump(checkin)}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_checkin(checkin_data: Dict[Any, Any] = Body(...), db: Session = Depends(get_db)):
    """Create a new check-in"""
    try:
        validated_data = schema.load(checkin_data)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=err.messages)
    
    checkin = CheckIn(**validated_data)
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return {"data": schema.dump(checkin), "message": "Check-in created successfully"}


@router.put("/{checkin_id}", response_model=dict)
def update_checkin(checkin_id: int, checkin_data: Dict[Any, Any] = Body(...), db: Session = Depends(get_db)):
    """Update a check-in"""
    checkin = db.query(CheckIn).filter(CheckIn.id == checkin_id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
    
    try:
        validated_data = schema.load(checkin_data, partial=True)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=err.messages)
    
    for key, value in validated_data.items():
        setattr(checkin, key, value)
    
    db.commit()
    db.refresh(checkin)
    return {"data": schema.dump(checkin), "message": "Check-in updated successfully"}


@router.delete("/{checkin_id}", response_model=dict)
def delete_checkin(checkin_id: int, db: Session = Depends(get_db)):
    """Delete a check-in"""
    checkin = db.query(CheckIn).filter(CheckIn.id == checkin_id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
    
    db.delete(checkin)
    db.commit()
    return {"message": "Check-in deleted successfully"}

