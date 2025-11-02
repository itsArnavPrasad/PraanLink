#/routers/checkins.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from db.database import SessionLocal
from db.models import CheckIn
from typing import List
import json
import traceback

router = APIRouter(prefix="/checkins", tags=["checkins"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@router.get("/summaries")
def get_checkin_summaries(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all check-in summaries, ordered by most recent first
    """
    try:
        print("Fetching check-ins from database...")
        checkins = db.query(CheckIn).order_by(desc(CheckIn.timestamp)).limit(limit).all()
        print(f"Found {len(checkins)} check-ins")
        
        summaries = []
        for i, checkin in enumerate(checkins):
            try:
                print(f"\nProcessing check-in {i+1}/{len(checkins)} (ID: {checkin.id})")
                
                # Safely parse each field
                symptoms = safe_parse_json(checkin.symptoms, [])
                medications = safe_parse_json(checkin.medications_taken, [])
                concerns = safe_parse_json(checkin.concerns, [])
                ai_insights = safe_parse_json(checkin.ai_insights, [])
                
                # Handle summary - it might be a dict or string
                summary_text = ""
                if isinstance(checkin.summary, dict):
                    summary_text = checkin.summary.get("summary", "") or str(checkin.summary)
                elif isinstance(checkin.summary, str):
                    summary_text = checkin.summary
                elif checkin.summary:
                    summary_text = str(checkin.summary)
                
                print(f"Check-in {checkin.id} - Mood: {checkin.mood}, Score: {checkin.overall_score}")
                
                summaries.append({
                    "id": checkin.id,
                    "timestamp": checkin.timestamp.isoformat() if checkin.timestamp else None,
                    "summary": summary_text,
                    "mood": checkin.mood or "",
                    "symptoms": symptoms,
                    "medications_taken": medications,
                    "sleep_quality": checkin.sleep_quality or "",
                    "energy_level": checkin.energy_level or "",
                    "concerns": concerns,
                    "ai_insights": ai_insights,
                    "overall_score": checkin.overall_score or ""
                })
                
            except Exception as e:
                print(f"Error processing check-in {checkin.id}: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                # Continue processing other check-ins instead of failing completely
                continue
        
        print(f"\nSuccessfully processed {len(summaries)} check-ins")
        
        return {
            "success": True,
            "count": len(summaries),
            "checkins": summaries
        }
    
    except Exception as e:
        print(f"Error in get_checkin_summaries: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error fetching check-ins: {str(e)}")

@router.get("/{checkin_id}")
def get_checkin_detail(
    checkin_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific check-in including transcript
    """
    try:
        checkin = db.query(CheckIn).filter(CheckIn.id == checkin_id).first()
        
        if not checkin:
            raise HTTPException(status_code=404, detail="Check-in not found")
        
        # Safely parse JSON fields
        symptoms = safe_parse_json(checkin.symptoms, [])
        medications = safe_parse_json(checkin.medications_taken, [])
        concerns = safe_parse_json(checkin.concerns, [])
        ai_insights = safe_parse_json(checkin.ai_insights, [])
        transcript = safe_parse_json(checkin.transcript, {})
        
        # Handle summary
        summary_text = ""
        if isinstance(checkin.summary, dict):
            summary_text = checkin.summary.get("summary", "") or str(checkin.summary)
        elif isinstance(checkin.summary, str):
            summary_text = checkin.summary
        elif checkin.summary:
            summary_text = str(checkin.summary)
        
        return {
            "id": checkin.id,
            "timestamp": checkin.timestamp.isoformat() if checkin.timestamp else None,
            "audio_path": checkin.audio_path,
            "transcript": transcript,
            "summary": summary_text,
            "mood": checkin.mood or "",
            "symptoms": symptoms,
            "medications_taken": medications,
            "sleep_quality": checkin.sleep_quality or "",
            "energy_level": checkin.energy_level or "",
            "concerns": concerns,
            "ai_insights": ai_insights,
            "overall_score": checkin.overall_score or ""
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_checkin_detail: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error fetching check-in: {str(e)}")