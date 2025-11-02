import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
import re
import requests
import uuid
import logging
from typing import Dict, Any, List

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API securely
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env file")

genai.configure(api_key=API_KEY)

# Load ADK server URL
ADK_SERVER_URL = os.getenv("ADK_SERVER_URL", "http://localhost:5010")


def prep_image(image_path: str, display_name: str = "UploadedImage"):
    """
    Uploads a local file to Gemini file storage and returns the uploaded file object.
    """
    try:
        sample_file = genai.upload_file(path=image_path, display_name=display_name)
        logger.info(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
        return sample_file
    except Exception as e:
        logger.error(f"Error uploading file to Gemini: {e}")
        raise


def extract_text_from_image(uploaded_file, model_name: str = "gemini-2.0-flash-exp"):
    """
    Call Gemini to extract text verbatim from the uploaded image.
    Returns the extracted text as a string.
    """
    prompt = (
        "You are an assistant that extracts text from medical documents.\n\n"
        "Instructions:\n"
        "1) Extract the full text from the image verbatim.\n"
        "2) Preserve the structure and formatting as much as possible.\n"
        "3) Return ONLY the extracted text, no additional commentary.\n\n"
        "Attached file: (image). Now extract the text."
    )

    try:
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content([uploaded_file, prompt])

        # Extract text from response
        raw_text = None
        try:
            raw_text = getattr(response, "text", None)
        except Exception:
            raw_text = None

        if not raw_text:
            try:
                cand = getattr(response, "candidates", None)
                if cand and isinstance(cand, (list, tuple)) and len(cand) > 0:
                    raw_text = getattr(cand[0], "content", None) or str(cand[0])
            except Exception:
                raw_text = None

        if not raw_text:
            raw_text = str(response)

        logger.info("Successfully extracted text from image")
        return raw_text.strip()

    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        raise


def call_agent(agent_name: str, extracted_text: str) -> Dict[str, Any]:
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

        # Step 2: Run with extracted text
        payload = {
            "app_name": agent_name,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": extracted_text}]
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


def process_prescription(image_path: str) -> Dict[str, Any]:
    """
    Process a prescription image:
    1. Upload to Gemini and extract text via OCR
    2. Send extracted text to prescription_agent
    3. Return structured prescription data
    """
    try:
        logger.info(f"Processing prescription: {image_path}")

        # Step 1: OCR
        uploaded_file = prep_image(image_path, display_name="Prescription")
        extracted_text = extract_text_from_image(uploaded_file)

        logger.info(f"Extracted text length: {len(extracted_text)} characters")

        # Step 2: Call prescription agent
        agent_response = call_agent("prescription_agent", extracted_text)

        # Step 3: Extract structured JSON
        extracted_jsons = extract_json_from_text(agent_response)

        if not extracted_jsons:
            logger.warning("No structured JSON found in prescription agent response")
            return {
                "ocr_text": extracted_text,
                "structured_data": None,
                "raw_response": agent_response,
                "status": "no_json_found"
            }

        prescription_data = extracted_jsons[0]
        logger.info("Successfully extracted structured prescription data")

        return {
            "ocr_text": extracted_text,
            "structured_data": prescription_data,
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Error processing prescription: {e}")
        return {
            "error": str(e),
            "status": "failed"
        }


def process_lab_report(image_path: str) -> Dict[str, Any]:
    """
    Process a lab report image:
    1. Upload to Gemini and extract text via OCR
    2. Send extracted text to lab_report_agent
    3. Return structured lab report data with proper extraction from ADK response
    """
    try:
        logger.info(f"Processing lab report: {image_path}")

        # Step 1: OCR
        uploaded_file = prep_image(image_path, display_name="LabReport")
        extracted_text = extract_text_from_image(uploaded_file)

        logger.info(f"Extracted text length: {len(extracted_text)} characters")

        # Step 2: Call lab report agent
        agent_response = call_agent("lab_report_agent", extracted_text)

        # Step 3: Extract structured data from ADK response format
        # The agent_response is a list of agent outputs, each with stateDelta
        
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
                logger.warning("No structured JSON found in lab report agent response")
                return {
                    "ocr_text": extracted_text,
                    "structured_data": None,
                    "raw_response": agent_response,
                    "status": "no_json_found"
                }

        logger.info("Successfully extracted structured lab report data")
        
        # Extract the nested structures
        raw_lab_data = structured_data.get("raw_lab_data", {})
        lab_analysis = structured_data.get("lab_analysis", {})
        lab_risk_scores = structured_data.get("lab_risk_scores", {})
        lab_summary = structured_data.get("lab_summary", {})
        
        return {
            "ocr_text": extracted_text,
            "structured_data": {
                "report_date": raw_lab_data.get("report_date"),
                "report_time": raw_lab_data.get("report_time"),
                "metrics": raw_lab_data.get("metrics", [])
            },
            "lab_analysis": lab_analysis,
            "lab_risk_scores": lab_risk_scores,
            "lab_summary": lab_summary,
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Error processing lab report: {e}")
        return {
            "error": str(e),
            "status": "failed"
        }