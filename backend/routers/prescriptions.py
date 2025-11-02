# routers/prescriptions.py
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Dict, Any
from db.database import get_db
from db.models import Prescription
from schemas import PrescriptionSchema
from marshmallow import ValidationError
import json
import traceback

router = APIRouter(prefix="/api/prescriptions", tags=["prescriptions"])
schema = PrescriptionSchema()
schemas = PrescriptionSchema(many=True)


def safe_parse_json(data, default=None):
    """Safely parse JSON data"""
    if default is None:
        default = []
    
    if data is None:
        return default
    if isinstance(data, list):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except (json.JSONDecodeError, ValueError):
            return default
    if isinstance(data, dict):
        return data
    return default


# IMPORTANT: /summaries must be defined BEFORE /{prescription_id} to avoid route conflicts
@router.get("/summaries")
def get_prescription_summaries(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all prescription summaries, ordered by most recent first
    """
    try:
        print("Fetching prescriptions from database...")
        prescriptions = db.query(Prescription).order_by(desc(Prescription.timestamp)).limit(limit).all()
        print(f"Found {len(prescriptions)} prescriptions")
        
        summaries = []
        for i, prescription in enumerate(prescriptions):
            try:
                print(f"\nProcessing prescription {i+1}/{len(prescriptions)} (ID: {prescription.id})")
                
                # Safely parse JSON fields
                medicines = safe_parse_json(prescription.medicines, [])
                structured_data = safe_parse_json(prescription.structured_data, {})
                
                # Extract summary text
                summary_text = prescription.prescription_summary or ""
                
                print(f"Prescription {prescription.id} - Doctor: {prescription.doctor_name}, Date: {prescription.prescription_date}")
                
                summaries.append({
                    "id": prescription.id,
                    "timestamp": prescription.timestamp.isoformat() if prescription.timestamp else None,
                    "prescription_date": prescription.prescription_date or "",
                    "doctor_name": prescription.doctor_name or "",
                    "doctor_qualification": prescription.doctor_qualification or "",
                    "doctor_registration_number": prescription.doctor_registration_number or "",
                    "hospital": prescription.hospital or "",
                    "doctor_contact_info": prescription.doctor_contact_info or "",
                    "patient_name": prescription.patient_name or "",
                    "patient_age": prescription.patient_age or "",
                    "patient_gender": prescription.patient_gender or "",
                    "medicines": medicines,
                    "diagnosis": prescription.diagnosis or "",
                    "symptoms": prescription.symptoms or "",
                    "advice": prescription.advice or "",
                    "follow_up": prescription.follow_up or "",
                    "prescription_summary": summary_text,
                    "file_path": prescription.file_path or ""
                })
                
            except Exception as e:
                print(f"Error processing prescription {prescription.id}: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                continue
        
        print(f"\nSuccessfully processed {len(summaries)} prescriptions")
        
        return {
            "success": True,
            "count": len(summaries),
            "prescriptions": summaries
        }
    
    except Exception as e:
        print(f"Error in get_prescription_summaries: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error fetching prescriptions: {str(e)}")


@router.get("", response_model=dict)
def get_all_prescriptions(db: Session = Depends(get_db)):
    """Get all prescriptions"""
    prescriptions = db.query(Prescription).all()
    return {"data": schemas.dump(prescriptions)}


@router.get("/{prescription_id}")
def get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    """Get prescription by ID with full details"""
    try:
        prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")
        
        # Safely parse JSON fields
        medicines = safe_parse_json(prescription.medicines, [])
        structured_data = safe_parse_json(prescription.structured_data, {})
        
        return {
            "id": prescription.id,
            "timestamp": prescription.timestamp.isoformat() if prescription.timestamp else None,
            "file_path": prescription.file_path or "",
            "ocr_text": prescription.ocr_text or "",
            "prescription_date": prescription.prescription_date or "",
            "doctor_name": prescription.doctor_name or "",
            "doctor_qualification": prescription.doctor_qualification or "",
            "doctor_registration_number": prescription.doctor_registration_number or "",
            "hospital": prescription.hospital or "",
            "doctor_contact_info": prescription.doctor_contact_info or "",
            "patient_name": prescription.patient_name or "",
            "patient_age": prescription.patient_age or "",
            "patient_gender": prescription.patient_gender or "",
            "medicines": medicines,
            "diagnosis": prescription.diagnosis or "",
            "symptoms": prescription.symptoms or "",
            "advice": prescription.advice or "",
            "follow_up": prescription.follow_up or "",
            "prescription_summary": prescription.prescription_summary or "",
            "structured_data": structured_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_prescription: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error fetching prescription: {str(e)}")


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