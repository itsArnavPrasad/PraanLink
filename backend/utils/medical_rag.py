# medical_rag.py
"""
RAG (Retrieval-Augmented Generation) utility for medical data.
Provides intelligent search and retrieval from database OverallReport
"""
from typing import Dict, Any, List, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc
from db.models import OverallReport
from db.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_session() -> Session:
    """Get a database session."""
    return SessionLocal()


def load_medical_data(db: Optional[Session] = None) -> Dict[str, Any]:
    """
    Load medical data from the latest OverallReport in the database.
    
    Args:
        db: Optional SQLAlchemy session. If not provided, creates a new one.
    
    Returns:
        Dictionary containing the structured medical data from the latest report
    """
    close_db = False
    if db is None:
        db = get_db_session()
        close_db = True
    
    try:
        # Get the latest overall report
        latest_report = db.query(OverallReport)\
            .order_by(desc(OverallReport.timestamp))\
            .first()
        
        if not latest_report:
            logger.warning("No overall report found in database")
            return {}
        
        logger.info(f"Successfully loaded medical data from OverallReport ID: {latest_report.id}")
        
        # Construct the medical data dictionary from the database model
        medical_data = {
            "report_id": latest_report.id,
            "report_timestamp": latest_report.timestamp.isoformat() if latest_report.timestamp else None,
            "timeline": latest_report.timeline or {},
            "clinical_trends": latest_report.clinical_trends or {},
            "risk_and_severity": latest_report.risk_and_severity or {},
            "possible_conditions": latest_report.possible_conditions or {},
            "medication_overview": latest_report.medication_overview or {},
            "final_report": latest_report.final_report or {}
        }
        
        # Add top-level fields to final_report for easier access
        if latest_report.patient_overview:
            medical_data["final_report"]["patient_overview"] = latest_report.patient_overview
        if latest_report.risk_level:
            medical_data["final_report"]["risk_level"] = latest_report.risk_level
        if latest_report.next_steps:
            medical_data["final_report"]["next_steps"] = latest_report.next_steps
        if latest_report.summary_comment:
            medical_data["final_report"]["summary_comment"] = latest_report.summary_comment
        
        # Add top-level fields to risk_and_severity for easier access
        if latest_report.overall_health_index is not None:
            medical_data["risk_and_severity"]["overall_health_index"] = latest_report.overall_health_index
        if latest_report.overall_severity:
            medical_data["risk_and_severity"]["overall_severity"] = latest_report.overall_severity
        
        return medical_data
    
    except Exception as e:
        logger.error(f"Error loading medical data from database: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {}
    
    finally:
        if close_db:
            db.close()


def search_medical_data(query: str, medical_data: Optional[Dict[str, Any]] = None, db: Optional[Session] = None) -> str:
    """
    Intelligent search through medical data based on query.
    Returns relevant information in a structured format.
    
    Args:
        query: Search query string
        medical_data: Optional pre-loaded medical data. If not provided, loads from DB
        db: Optional database session
    """
    if medical_data is None:
        medical_data = load_medical_data(db)
    
    if not medical_data:
        return "No medical data available. Please generate an overall report first."
    
    query_lower = query.lower()
    
    # Build comprehensive response
    response_parts = []
    
    # Add report metadata
    if medical_data.get("report_timestamp"):
        response_parts.append(f"MEDICAL REPORT (as of {medical_data['report_timestamp']})")
        response_parts.append("")
    
    # Check timeline/events
    if 'timeline' in medical_data and 'events' in medical_data['timeline']:
        relevant_events = []
        for event in medical_data['timeline']['events']:
            event_text = f"{event.get('description', '')} {event.get('date', '')} {event.get('event_type', '')}".lower()
            if any(term in event_text for term in query_lower.split()) or query_lower in ['all', 'everything', 'complete', 'full']:
                relevant_events.append(event)
        
        if relevant_events:
            response_parts.append("MEDICAL TIMELINE:")
            for event in relevant_events:
                response_parts.append(f"- {event.get('date', 'N/A')} ({event.get('event_type', 'unknown')}): {event.get('description', '')}")
            response_parts.append("")
    
    # Check clinical trends
    if 'clinical_trends' in medical_data:
        trends = medical_data['clinical_trends'].get('trends', [])
        if trends and (any(term in query_lower for term in ['trend', 'test', 'lab', 'result', 'value', 'cholesterol', 'lipid']) or query_lower in ['all', 'everything']):
            response_parts.append("CLINICAL TRENDS & LAB RESULTS:")
            for trend in trends:
                metric = trend.get('metric', '')
                value = trend.get('current_value', 'N/A')
                status = trend.get('status', 'N/A')
                comment = trend.get('clinical_comment', '')
                response_parts.append(f"- {metric}: {value} (Status: {status}) - {comment}")
            
            summary = medical_data['clinical_trends'].get('overall_summary', '')
            if summary:
                response_parts.append(f"\nSummary: {summary}")
            response_parts.append("")
    
    # Check risk and severity
    if 'risk_and_severity' in medical_data:
        risk_data = medical_data['risk_and_severity']
        if any(term in query_lower for term in ['risk', 'severity', 'health', 'overall', 'condition']) or query_lower in ['all', 'everything']:
            response_parts.append("HEALTH RISK ASSESSMENT:")
            response_parts.append(f"Overall Health Index: {risk_data.get('overall_health_index', 'N/A')}")
            response_parts.append(f"Overall Severity: {risk_data.get('overall_severity', 'N/A')}")
            
            diseases = risk_data.get('disease_risks', [])
            if diseases:
                response_parts.append("\nDisease Risk Scores:")
                for disease in diseases:
                    response_parts.append(f"- {disease.get('disease', '')}: Risk Score {disease.get('risk_score', 'N/A')} ({disease.get('severity_level', 'N/A')})")
            
            comment = risk_data.get('clinical_comment', '')
            if comment:
                response_parts.append(f"\nClinical Assessment: {comment}")
            response_parts.append("")
    
    # Check possible conditions
    if 'possible_conditions' in medical_data:
        conditions = medical_data['possible_conditions'].get('conditions', [])
        if any(term in query_lower for term in ['condition', 'diagnosis', 'symptom', 'issue', 'problem']) or query_lower in ['all', 'everything']:
            response_parts.append("POSSIBLE CONDITIONS & RECOMMENDATIONS:")
            for condition in conditions:
                name = condition.get('condition', '')
                confidence = condition.get('confidence', 'N/A')
                action = condition.get('recommended_action', '')
                response_parts.append(f"- {name} (Confidence: {confidence}%): {action}")
            
            summary = medical_data['possible_conditions'].get('summary_comment', '')
            if summary:
                response_parts.append(f"\nNote: {summary}")
            response_parts.append("")
    
    # Check medications
    if 'medication_overview' in medical_data:
        med_data = medical_data['medication_overview']
        if any(term in query_lower for term in ['medication', 'medicine', 'prescription', 'drug', 'med']) or query_lower in ['all', 'everything']:
            response_parts.append("MEDICATION OVERVIEW:")
            
            current_meds = med_data.get('current_medications', [])
            if current_meds:
                response_parts.append("\nCurrent Medications:")
                for med in current_meds:
                    response_parts.append(f"- {med.get('name', '')} ({med.get('dosage', '')}) - {med.get('frequency', '')}")
            else:
                response_parts.append("\nCurrent Medications: None")
            
            past_meds = med_data.get('past_medications', [])
            if past_meds:
                response_parts.append("\nPast Medications:")
                for med in past_meds[:5]:  # Limit to recent 5
                    response_parts.append(f"- {med.get('name', '')} ({med.get('dosage', '')}) - Date: {med.get('start_date', 'N/A')}")
            
            summary = med_data.get('medication_summary', '')
            if summary:
                response_parts.append(f"\n{summary}")
            response_parts.append("")
    
    # Check final report
    if 'final_report' in medical_data:
        final = medical_data['final_report']
        if query_lower in ['all', 'everything', 'summary', 'overview', 'complete']:
            response_parts.append("PATIENT OVERVIEW:")
            response_parts.append(final.get('patient_overview', ''))
            response_parts.append(f"\nRisk Level: {final.get('risk_level', 'N/A')}")
            
            next_steps = final.get('next_steps', [])
            if next_steps:
                response_parts.append("\nRecommended Next Steps:")
                for i, step in enumerate(next_steps[:5], 1):  # Limit to top 5
                    response_parts.append(f"{i}. {step}")
            
            summary_comment = final.get('summary_comment', '')
            if summary_comment:
                response_parts.append(f"\nClinical Summary: {summary_comment}")
    
    if not response_parts or (len(response_parts) == 2 and response_parts[1] == ""):
        # If no specific matches, return overview
        if 'final_report' in medical_data:
            final = medical_data['final_report']
            return f"PATIENT MEDICAL OVERVIEW:\n{final.get('patient_overview', 'No overview available.')}\n\nRisk Level: {final.get('risk_level', 'N/A')}"
        return "No specific medical information found for your query. Please try asking about symptoms, medications, lab results, conditions, or risk assessment."
    
    return "\n".join(response_parts)


def get_complete_medical_profile(db: Optional[Session] = None) -> str:
    """
    Get complete medical profile summary.
    
    Args:
        db: Optional database session
    """
    medical_data = load_medical_data(db)
    if not medical_data:
        return "No medical data available. Please generate an overall report first."
    
    return search_medical_data("all", medical_data, db)


def get_appointment_relevant_info(db: Optional[Session] = None) -> str:
    """
    Get information specifically relevant for appointment booking:
    - Current symptoms and concerns
    - Recent diagnoses
    - Medications
    - Risk factors
    - Follow-up needs
    
    Args:
        db: Optional database session
    """
    medical_data = load_medical_data(db)
    if not medical_data:
        return "No medical data available. Please generate an overall report first."
    
    response_parts = []
    
    # Get recent symptoms and concerns from timeline
    if 'timeline' in medical_data and 'events' in medical_data['timeline']:
        recent_events = [e for e in medical_data['timeline']['events'] 
                        if e.get('event_type') in ['patient_update', 'doctor_visit']]
        if recent_events:
            response_parts.append("RECENT HEALTH EVENTS & SYMPTOMS:")
            for event in recent_events[-3:]:  # Last 3 events
                response_parts.append(f"- {event.get('date', 'N/A')}: {event.get('description', '')}")
            response_parts.append("")
    
    # Get possible conditions
    if 'possible_conditions' in medical_data:
        conditions = medical_data['possible_conditions'].get('conditions', [])
        if conditions:
            response_parts.append("CURRENT CONDITIONS & CONCERNS:")
            for condition in conditions:
                response_parts.append(f"- {condition.get('condition', '')}: {condition.get('recommended_action', '')}")
            response_parts.append("")
    
    # Get risk assessment
    if 'risk_and_severity' in medical_data:
        risk = medical_data['risk_and_severity']
        response_parts.append("HEALTH STATUS:")
        response_parts.append(f"Overall Risk: {risk.get('overall_severity', 'N/A')} (Index: {risk.get('overall_health_index', 'N/A')})")
        
        diseases = risk.get('disease_risks', [])
        if diseases:
            for disease in diseases:
                if disease.get('risk_score', 0) > 50:  # Only show significant risks
                    response_parts.append(f"- {disease.get('disease', '')}: {disease.get('severity_level', 'N/A')} risk")
        response_parts.append("")
    
    # Get medications
    if 'medication_overview' in medical_data:
        meds = medical_data['medication_overview']
        current = meds.get('current_medications', [])
        if current:
            response_parts.append("CURRENT MEDICATIONS:")
            for med in current:
                response_parts.append(f"- {med.get('name', '')} ({med.get('dosage', '')})")
            response_parts.append("")
    
    # Get next steps
    if 'final_report' in medical_data:
        next_steps = medical_data['final_report'].get('next_steps', [])
        if next_steps:
            response_parts.append("RECOMMENDED FOLLOW-UP:")
            for step in next_steps[:3]:  # Top 3
                response_parts.append(f"- {step}")
    
    if not response_parts:
        return get_complete_medical_profile(db)
    
    return "\n".join(response_parts)


def check_medical_data_exists(db: Optional[Session] = None) -> bool:
    """
    Check if medical data exists in the database.
    
    Args:
        db: Optional database session
        
    Returns:
        True if at least one OverallReport exists, False otherwise
    """
    close_db = False
    if db is None:
        db = get_db_session()
        close_db = True
    
    try:
        count = db.query(OverallReport).count()
        return count > 0
    except Exception as e:
        logger.error(f"Error checking medical data existence: {e}")
        return False
    finally:
        if close_db:
            db.close()