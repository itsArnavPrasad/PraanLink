import os
from dotenv import load_dotenv
import json
import re
import requests
import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from db.models import CheckIn, Prescription, Report, OverallReport

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load ADK server URL
ADK_SERVER_URL = os.getenv("ADK_SERVER_URL", "http://localhost:5010")


def call_agent(agent_name: str, input_data: str) -> Dict[str, Any]:
    """
    Call a single ADK agent API (session creation + /run request).
    """
    try:
        logger.info(f"Calling {agent_name} at {ADK_SERVER_URL}")

        user_id = "u_backend"
        session_id = f"s_{uuid.uuid4().hex[:8]}"

        # Step 1: Create session
        session_endpoint = f"{ADK_SERVER_URL}/apps/{agent_name}/users/{user_id}/sessions/{session_id}"
        session_payload = {"state": {}}

        session_resp = requests.post(
            session_endpoint,
            json=session_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if session_resp.status_code != 200:
            return {
                "error": f"Session creation failed for {agent_name}",
                "details": session_resp.text
            }

        logger.info(f"Session created for {agent_name}: {session_id}")

        # Step 2: Run with input data
        payload = {
            "app_name": agent_name,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": input_data}]
            }
        }

        run_response = requests.post(
            f"{ADK_SERVER_URL}/run",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=600
        )

        if run_response.status_code != 200:
            return {
                "error": f"{agent_name} run failed",
                "details": run_response.text
            }

        logger.info(f"{agent_name} completed successfully")
        return run_response.json()

    except requests.exceptions.Timeout:
        return {"error": f"{agent_name} request timed out"}

    except requests.exceptions.RequestException as e:
        return {"error": f"{agent_name} request failed: {str(e)}"}

    except json.JSONDecodeError:
        return {"error": f"{agent_name} returned invalid JSON"}


def extract_json_from_text(data: Any) -> List[Dict[str, Any]]:
    """
    Recursively extract JSON objects from the agent response.
    """
    extracted_jsons = []

    def recursive_search(obj):
        if isinstance(obj, dict):
            if 'text' in obj and isinstance(obj['text'], str):
                text_content = obj['text']

                # Try parsing direct JSON
                try:
                    parsed_direct = json.loads(text_content)
                    extracted_jsons.append(parsed_direct)
                except json.JSONDecodeError:
                    # Look for code blocks
                    json_pattern = r'```json\s*\n(.*?)\n```'
                    matches = re.findall(json_pattern, text_content, re.DOTALL)
                    for match in matches:
                        try:
                            parsed_json = json.loads(match)
                            extracted_jsons.append(parsed_json)
                        except json.JSONDecodeError:
                            logger.warning("Failed to parse a JSON block")

            for value in obj.values():
                recursive_search(value)

        elif isinstance(obj, list):
            for item in obj:
                recursive_search(item)

    recursive_search(data)
    return extracted_jsons


def safe_parse_json(data, default=None):
    """Safely parse JSON data"""
    if default is None:
        default = [] if not isinstance(data, dict) else {}
    
    if data is None:
        return default
    if isinstance(data, (list, dict)):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except (json.JSONDecodeError, ValueError):
            return default
    return default


def retrieve_all_medical_data(db: Session) -> Dict[str, Any]:
    """
    Retrieve all check-ins, prescriptions, and lab reports from the database
    and format them as JSON for the report agent.
    """
    try:
        # Retrieve check-ins
        checkins = db.query(CheckIn).order_by(desc(CheckIn.timestamp)).all()
        prescriptions = db.query(Prescription).order_by(desc(Prescription.timestamp)).all()
        reports = db.query(Report).order_by(desc(Report.timestamp)).all()

        logger.info(f"Retrieved {len(checkins)} check-ins, {len(prescriptions)} prescriptions, {len(reports)} lab reports")

        # Format check-ins
        checkins_data = []
        for checkin in checkins:
            checkins_data.append({
                "id": checkin.id,
                "timestamp": checkin.timestamp.isoformat() if checkin.timestamp else None,
                "summary": safe_parse_json(checkin.summary, {}),
                "mood": checkin.mood or "",
                "symptoms": safe_parse_json(checkin.symptoms, []),
                "medications_taken": safe_parse_json(checkin.medications_taken, []),
                "sleep_quality": checkin.sleep_quality or "",
                "energy_level": checkin.energy_level or "",
                "concerns": safe_parse_json(checkin.concerns, []),
                "ai_insights": safe_parse_json(checkin.ai_insights, []),
                "overall_score": checkin.overall_score or ""
            })

        # Format prescriptions
        prescriptions_data = []
        for prescription in prescriptions:
            prescriptions_data.append({
                "id": prescription.id,
                "timestamp": prescription.timestamp.isoformat() if prescription.timestamp else None,
                "prescription_date": prescription.prescription_date or "",
                "doctor_name": prescription.doctor_name or "",
                "doctor_qualification": prescription.doctor_qualification or "",
                "hospital": prescription.hospital or "",
                "patient_name": prescription.patient_name or "",
                "patient_age": prescription.patient_age or "",
                "patient_gender": prescription.patient_gender or "",
                "medicines": safe_parse_json(prescription.medicines, []),
                "diagnosis": prescription.diagnosis or "",
                "symptoms": prescription.symptoms or "",
                "advice": prescription.advice or "",
                "follow_up": prescription.follow_up or "",
                "prescription_summary": prescription.prescription_summary or "",
                "structured_data": safe_parse_json(prescription.structured_data, {})
            })

        # Format lab reports
        reports_data = []
        for report in reports:
            reports_data.append({
                "id": report.id,
                "timestamp": report.timestamp.isoformat() if report.timestamp else None,
                "report_date": report.report_date or "",
                "report_time": report.report_time or "",
                "raw_lab_data": safe_parse_json(report.raw_lab_data, {}),
                "lab_analysis": safe_parse_json(report.lab_analysis, {}),
                "lab_risk_scores": safe_parse_json(report.lab_risk_scores, {}),
                "overall_health_risk_index": report.overall_health_risk_index or 0,
                "severity": report.severity or "",
                "critical_flags": safe_parse_json(report.critical_flags, []),
                "lab_summary_overview": report.lab_summary_overview or "",
                "key_findings": safe_parse_json(report.key_findings, []),
                "overall_risk": report.overall_risk or "",
                "recommendations": safe_parse_json(report.recommendations, []),
                "critical_alerts": safe_parse_json(report.critical_alerts, []),
                "structured_data": safe_parse_json(report.structured_data, {})
            })

        # Combine all data
        combined_data = {
            "checkins": checkins_data,
            "prescriptions": prescriptions_data,
            "lab_reports": reports_data
        }

        logger.info("Successfully formatted all medical data")
        return combined_data

    except Exception as e:
        logger.error(f"Error retrieving medical data: {e}")
        raise


def process_overall_report(db: Session, output_dir: str = "uploads/overall_reports") -> Dict[str, Any]:
    """
    Process an overall medical report:
    1. Retrieve all check-ins, prescriptions, and lab reports
    2. Format as JSON
    3. Send to report_agent
    4. Extract structured response
    5. Generate PDF
    6. Save OverallReport to database
    
    Returns the OverallReport database record.
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "charts"), exist_ok=True)

        logger.info("Starting overall report generation")

        # Step 1: Retrieve all medical data
        medical_data = retrieve_all_medical_data(db)

        # Step 2: Format as JSON string for the agent
        medical_data_json = json.dumps(medical_data, indent=2, default=str)
        logger.info(f"Prepared medical data JSON ({len(medical_data_json)} characters)")

        # Step 3: Call report agent
        agent_response = call_agent("report_agent", medical_data_json)

        if "error" in agent_response:
            logger.error(f"Agent error: {agent_response['error']}")
            return {
                "error": agent_response.get("error", "Unknown error"),
                "details": agent_response.get("details", ""),
                "status": "failed"
            }

        # Step 4: Extract structured data from ADK response format
        structured_data = {}
        
        # Parse through the agent response to extract all state deltas
        if isinstance(agent_response, list):
            for entry in agent_response:
                if isinstance(entry, dict) and 'actions' in entry:
                    state_delta = entry.get('actions', {}).get('stateDelta', {})
                    
                    # Merge all state deltas into structured_data
                    for key, value in state_delta.items():
                        structured_data[key] = value
        
        # If no data extracted, try the old method as fallback
        if not structured_data:
            extracted_jsons = extract_json_from_text(agent_response)
            if extracted_jsons:
                structured_data = extracted_jsons[0]
            else:
                logger.warning("No structured JSON found in report agent response")
                return {
                    "error": "No structured data found in agent response",
                    "raw_response": agent_response,
                    "status": "no_json_found"
                }

        logger.info("Successfully extracted structured report data")

        # Step 5: Generate PDF
        from utils.pdf_generator import generate_medical_report_pdf
        
        # Create a temporary JSON file for the PDF generator
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(structured_data, temp_file, indent=2, default=str)
            temp_json_path = temp_file.name

        try:
            # Generate PDF
            pdf_filename = f"OverallReport_{uuid.uuid4().hex[:8]}.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            generate_medical_report_pdf(
                json_data=structured_data,
                output_pdf=pdf_path,
                charts_dir=os.path.join(output_dir, "charts")
            )
            
            logger.info(f"PDF generated successfully: {pdf_path}")

        finally:
            # Clean up temporary JSON file
            if os.path.exists(temp_json_path):
                os.unlink(temp_json_path)

        # Step 6: Save to database
        # Extract sections from structured_data
        timeline = structured_data.get("timeline", {})
        clinical_trends = structured_data.get("clinical_trends", {})
        risk_and_severity = structured_data.get("risk_and_severity", {})
        possible_conditions = structured_data.get("possible_conditions", {})
        medication_overview = structured_data.get("medication_overview", {})
        final_report = structured_data.get("final_report", {})

        # Extract individual fields from final_report
        patient_overview = final_report.get("patient_overview", "")
        risk_level = final_report.get("risk_level", "")
        next_steps = final_report.get("next_steps", [])
        summary_comment = final_report.get("summary_comment", "")

        # Extract overall health metrics
        overall_health_index = risk_and_severity.get("overall_health_index")
        overall_severity = risk_and_severity.get("overall_severity", "")

        overall_report = OverallReport(
            pdf_file_path=pdf_path,
            timeline=timeline,
            clinical_trends=clinical_trends,
            risk_and_severity=risk_and_severity,
            overall_health_index=overall_health_index,
            overall_severity=overall_severity,
            possible_conditions=possible_conditions,
            medication_overview=medication_overview,
            final_report=final_report,
            patient_overview=patient_overview,
            risk_level=risk_level,
            next_steps=next_steps,
            summary_comment=summary_comment,
            structured_data=structured_data
        )

        db.add(overall_report)
        db.commit()
        db.refresh(overall_report)

        logger.info(f"Overall report saved to database with ID: {overall_report.id}")

        return {
            "id": overall_report.id,
            "pdf_file_path": pdf_path,
            "status": "success",
            "structured_data": structured_data
        }

    except Exception as e:
        logger.error(f"Error processing overall report: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "error": str(e),
            "status": "failed"
        }

