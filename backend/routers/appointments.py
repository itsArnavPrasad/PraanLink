from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc
from db.database import SessionLocal
from db.models import CheckIn, Prescription, Report
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/appointments", tags=["appointments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/get-patient-context")
def get_patient_context():
    """
    Get complete patient medical context for pre-loading into agent.
    Returns the full medical profile from medical_data.json.
    """
    try:
        from utils.medical_rag import get_appointment_relevant_info, get_complete_medical_profile
        
        # Get appointment-relevant information
        medical_context = get_appointment_relevant_info()
        
        return {
            "success": True,
            "context": medical_context,
            "message": "Patient medical context retrieved successfully"
        }
    
    except Exception as e:
        import traceback
        logger.error(f"Error getting patient context: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error retrieving patient context: {str(e)}")

@router.post("/get-medical-history")
def get_medical_history(
    query: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    RAG tool: Get comprehensive medical history from medical_data.json and database.
    This is the primary tool for the appointment booking agent to understand patient's medical situation.
    """
    try:
        from utils.medical_rag import search_medical_data, get_appointment_relevant_info, get_complete_medical_profile
        
        search_query = query.get("query", "").lower().strip()
        
        # Use RAG to search medical_data.json
        if not search_query or search_query in ['all', 'everything', 'complete', 'full', 'summary', 'overview']:
            # Get complete profile for general queries
            if search_query in ['summary', 'overview']:
                medical_info = get_appointment_relevant_info()
            else:
                medical_info = get_complete_medical_profile()
        else:
            # Search based on specific query
            medical_info = search_medical_data(search_query)
        
        # Also get recent database entries for additional context
        checkins = db.query(CheckIn).order_by(desc(CheckIn.timestamp)).limit(5).all()
        prescriptions = db.query(Prescription).order_by(desc(Prescription.timestamp)).limit(5).all()
        reports = db.query(Report).order_by(desc(Report.timestamp)).limit(5).all()
        
        # Format database entries
        db_context = []
        
        if checkins:
            db_context.append("\n=== RECENT CHECK-INS FROM DATABASE ===")
            for c in checkins[:3]:
                summary_text = c.summary.get("summary", "") if isinstance(c.summary, dict) else (c.summary or "")
                db_context.append(f"- {c.timestamp.strftime('%Y-%m-%d') if c.timestamp else 'N/A'}: Mood: {c.mood or 'N/A'}, Symptoms: {c.symptoms if isinstance(c.symptoms, list) else 'N/A'}, Summary: {summary_text[:100]}")
        
        if prescriptions:
            db_context.append("\n=== RECENT PRESCRIPTIONS ===")
            for p in prescriptions[:3]:
                db_context.append(f"- {p.prescription_date or 'N/A'}: {p.doctor_name or 'Dr. Unknown'} - Diagnosis: {p.diagnosis or 'N/A'}, Medicines: {len(p.medicines) if isinstance(p.medicines, list) else 0} medications")
        
        if reports:
            db_context.append("\n=== RECENT LAB REPORTS ===")
            for r in reports[:3]:
                db_context.append(f"- {r.report_date or 'N/A'}: Risk: {r.overall_risk or 'N/A'}, Severity: {r.severity or 'N/A'}, Findings: {len(r.key_findings) if isinstance(r.key_findings, list) else 0} key findings")
        
        # Combine RAG results with database context
        combined_response = medical_info
        if db_context:
            combined_response += "\n\n" + "\n".join(db_context)
        
        return {
            "success": True,
            "data": combined_response,
            "summary": "Medical history retrieved from patient medical profile and recent database entries."
        }
    
    except Exception as e:
        import traceback
        logger.error(f"Error in get_medical_history: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error fetching medical history: {str(e)}")


@router.post("/send-email")
def send_email(email_data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """
    Send email via Gmail API with medical report PDF attachment.
    Automatically fetches and attaches the latest overall report PDF.
    """
    try:
        from utils.gmail_integration import send_email as send_gmail
        from db.models import OverallReport
        from sqlalchemy import desc
        import os
        
        # Use provided email or default to receiver email
        to = email_data.get("to") or os.getenv("GOOGLE_RECEIVER_EMAIL", "arnav.prasad999918@gmail.com")
        subject = email_data.get("subject", "")
        body = email_data.get("body", "")
        
        # Fetch the latest overall report from the database
        latest_report = db.query(OverallReport)\
            .order_by(desc(OverallReport.timestamp))\
            .first()
        
        # Prepare attachment list
        attachment_paths = []
        
        if latest_report and latest_report.pdf_file_path:
            # Check if the PDF file exists
            if os.path.exists(latest_report.pdf_file_path):
                attachment_paths.append(latest_report.pdf_file_path)
                logger.info(f"Including latest medical report PDF: {latest_report.pdf_file_path}")
            else:
                logger.warning(f"Latest report PDF not found at: {latest_report.pdf_file_path}")
        else:
            logger.warning("No overall report found in database or PDF path is missing")
        
        # Add any additional attachments specified in email_data (optional)
        additional_attachments = email_data.get("attachments", [])
        if additional_attachments:
            for att in additional_attachments:
                if os.path.exists(att) and att not in attachment_paths:
                    attachment_paths.append(att)
                    logger.info(f"Including additional attachment: {att}")
        
        # Send email
        result = send_gmail(
            to=to,
            subject=subject,
            body=body,
            attachment_paths=attachment_paths if attachment_paths else None
        )
        
        if result.get("success"):
            return {
                **result,
                "attachments_sent": [os.path.basename(path) for path in attachment_paths]
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to send email"))
            
    except ImportError:
        # Fallback if Gmail integration not set up
        return {
            "success": False,
            "error": "Gmail API not configured. Please set up Google OAuth2 credentials.",
            "to": email_data.get("to", ""),
            "subject": email_data.get("subject", "")
        }
    except Exception as e:
        import traceback
        logger.error(f"Error sending email: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")


@router.post("/create-calendar-event")
def create_calendar_event(event_data: Dict[str, Any] = Body(...)):
    """
    Create calendar event via Google Calendar API.
    """
    try:
        from utils.calendar_integration import create_calendar_event as create_event
        import os
        
        title = event_data.get("title", "")
        description = event_data.get("description", "")
        start_time = event_data.get("start_time", "")
        end_time = event_data.get("end_time", "")
        location = event_data.get("location", "")
        # Add default receiver email to attendees if not provided
        default_attendees = [os.getenv("GOOGLE_RECEIVER_EMAIL", "arnav.prasad999918@gmail.com")]
        attendees = event_data.get("attendees", default_attendees)
        
        result = create_event(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            attendees=attendees if attendees else None
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to create calendar event"))
            
    except ImportError:
        # Fallback if Calendar integration not set up
        return {
            "success": False,
            "error": "Google Calendar API not configured. Please set up Google OAuth2 credentials.",
            "event": {
                "title": title,
                "start_time": start_time,
                "end_time": end_time
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating calendar event: {str(e)}")