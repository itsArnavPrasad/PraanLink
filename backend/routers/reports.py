from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from db.database import get_db
from db.models import Report
from schemas import ReportSchema
from marshmallow import ValidationError

router = APIRouter(prefix="/api/reports", tags=["reports"])
schema = ReportSchema()
schemas = ReportSchema(many=True)


@router.get("", response_model=dict)
def get_all_reports(db: Session = Depends(get_db)):
    """Get all reports"""
    reports = db.query(Report).all()
    return {"data": schemas.dump(reports)}


@router.get("/{report_id}", response_model=dict)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get report by ID"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"data": schema.dump(report)}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_report(report_data: Dict[Any, Any] = Body(...), db: Session = Depends(get_db)):
    """Create a new report"""
    try:
        validated_data = schema.load(report_data)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=err.messages)
    
    report = Report(**validated_data)
    db.add(report)
    db.commit()
    db.refresh(report)
    return {"data": schema.dump(report), "message": "Report created successfully"}


@router.put("/{report_id}", response_model=dict)
def update_report(report_id: int, report_data: Dict[Any, Any] = Body(...), db: Session = Depends(get_db)):
    """Update a report"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    try:
        validated_data = schema.load(report_data, partial=True)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=err.messages)
    
    for key, value in validated_data.items():
        setattr(report, key, value)
    
    db.commit()
    db.refresh(report)
    return {"data": schema.dump(report), "message": "Report updated successfully"}


@router.delete("/{report_id}", response_model=dict)
def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a report"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(report)
    db.commit()
    return {"message": "Report deleted successfully"}

