# utils/analyze.py
import requests
import json
import re
from typing import Dict, Any, List
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Single unified ADK server endpoint
ADK_SERVER_URL = "http://localhost:5010"

def call_agent(agent_name: str, transcript: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call a single ADK agent API (session creation + /run request)
    All agents are hosted on the same server with different app names.
    
    Args:
        agent_name: Name of the agent app (e.g., "emotion_agent", "compliance_agent", "strategy_agent")
        transcript: The transcript data to analyze
    
    Returns:
        Agent response as a dictionary
    """
    try:
        print("-----"*10)
        print(f"Calling {agent_name} at {ADK_SERVER_URL}")

        # Generate unique IDs for user + session
        user_id = "u_backend"
        session_id = f"s_{uuid.uuid4().hex[:8]}"
        
        # Step 1️⃣: Create a session (no pre-existing state)
        session_endpoint = f"{ADK_SERVER_URL}/apps/{agent_name}/users/{user_id}/sessions/{session_id}"
        session_payload = {"state": {}}  # empty, per your request

        session_resp = requests.post(
            session_endpoint,
            json=session_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if session_resp.status_code != 200:
            logger.error(f"Session creation failed: {session_resp.text}")
            return {
                "error": f"Session creation failed for {agent_name}",
                "details": session_resp.text,
                "agent": agent_name,
            }

        print(f"Session created for {agent_name}: {session_id}")

        # Step 2️⃣: Send the transcript message to /run
        transcript_message = json.dumps(transcript, indent=2)
        payload = {
            "app_name": agent_name,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": transcript_message}]
            }
        }

        # print(f"Payload for {agent_name}: {json.dumps(payload, indent=2)}")

        run_response = requests.post(
            f"{ADK_SERVER_URL}/run",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=600  # since agent calls can take 1–2 minutes
        )

        if run_response.status_code != 200:
            print(f"{agent_name} returned {run_response.status_code}: {run_response.text}")
            return {
                "error": f"{agent_name} run failed",
                "details": run_response.text,
                "agent": agent_name
            }

        print(f"{agent_name} completed successfully")
        print(f"Response from {agent_name}:")
        print(run_response.json())
        return run_response.json()

    except requests.exceptions.Timeout:
        logger.error(f"{agent_name} timed out")
        return {"error": f"{agent_name} request timed out", "agent": agent_name}

    except requests.exceptions.RequestException as e:
        logger.error(f"{agent_name} request failed: {str(e)}")
        return {"error": str(e), "agent": agent_name}

    except json.JSONDecodeError as e:
        logger.error(f"{agent_name} returned invalid JSON: {str(e)}")
        return {"error": "Invalid JSON response", "agent": agent_name}


def extract_json_from_text(data: Any) -> List[Dict[str, Any]]:
    """
    Recursively search through the response and extract JSON content from 'text' fields
    that contain ```json code blocks.
    
    Args:
        data: The response data (can be dict, list, or primitive)
    
    Returns:
        List of extracted and parsed JSON objects
    """
    extracted_jsons = []
    
    def recursive_search(obj):
        if isinstance(obj, dict):
            # Check if this dict has a 'text' key with ```json content
            if 'text' in obj and isinstance(obj['text'], str):
                text_content = obj['text']
                # Look for ```json blocks
                json_pattern = r'```json\s*\n(.*?)\n```'
                matches = re.findall(json_pattern, text_content, re.DOTALL)
                
                for match in matches:
                    try:
                        parsed_json = json.loads(match)
                        extracted_jsons.append(parsed_json)
                        logger.info(f"Successfully extracted JSON block")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON block: {e}")
            
            # Continue searching in nested dicts
            for value in obj.values():
                recursive_search(value)
                
        elif isinstance(obj, list):
            # Search in list items
            for item in obj:
                recursive_search(item)
    
    recursive_search(data)
    return extracted_jsons


def merge_agent_responses(
    emotion_response: Dict[str, Any],
    compliance_response: Dict[str, Any],
    strategy_response: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge responses from all three agents into a single clean JSON structure.
    Extracts the actual JSON content from 'text' fields containing ```json blocks.
    
    Args:
        emotion_response: Response from emotion agent
        compliance_response: Response from compliance agent
        strategy_response: Response from strategy agent
        
    Returns:
        Clean merged analysis result
    """
    logger.info("Extracting clean JSON from agent responses...")
    
    # Extract JSON blocks from each response
    emotion_jsons = extract_json_from_text(emotion_response)
    compliance_jsons = extract_json_from_text(compliance_response)
    strategy_jsons = extract_json_from_text(strategy_response)
    
    # Take the first (and typically only) JSON block from each
    emotion_data = emotion_jsons[0] if emotion_jsons else {"error": "No JSON found in emotion_agent response"}
    compliance_data = compliance_jsons[0] if compliance_jsons else {"error": "No JSON found in compliance_agent response"}
    strategy_data = strategy_jsons[0] if strategy_jsons else {"error": "No JSON found in strategy_agent response"}
    
    # Create clean merged structure
    merged = {
        "emotion_analysis": emotion_data,
        "compliance_analysis": compliance_data,
        "strategy_analysis": strategy_data,
        "overall_status": "success" if all(
            "error" not in data for data in [emotion_data, compliance_data, strategy_data]
        ) else "partial_failure"
    }
    
    # Add summary of any errors
    errors = []
    if "error" in emotion_data:
        errors.append(f"emotion_agent: {emotion_data['error']}")
    if "error" in compliance_data:
        errors.append(f"compliance_agent: {compliance_data['error']}")
    if "error" in strategy_data:
        errors.append(f"strategy_agent: {strategy_data['error']}")
    
    if errors:
        merged["errors"] = errors
    
    logger.info(f"Extracted {len(emotion_jsons)} JSON blocks from emotion_agent")
    logger.info(f"Extracted {len(compliance_jsons)} JSON blocks from compliance_agent")
    logger.info(f"Extracted {len(strategy_jsons)} JSON blocks from strategy_agent")
    
    return merged


def summarize_checkin_text(transcript: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze transcript using three AI agents and merge results.
    All agents are hosted on the same ADK server (localhost:5010) with different app names.
    
    Args:
        transcript: The full transcript JSON from WhisperX
        
    Returns:
        Clean merged analysis from all three agents
    """
    logger.info("Summarizing conversation...")
    
    summarize_checkin_result = call_agent(
        "conversation_summarizer_agent",
        transcript
    )
    
    
    logger.info("Analysis pipeline completed")
    
    # Log the clean formatted JSON
    try:
        formatted_json = json.dumps(summarize_checkin_result, indent=2, ensure_ascii=False)
        logger.info(f"Clean analysis output:\n{formatted_json}")
    except Exception as e:
        logger.warning(f"Could not format JSON for logging: {e}")
    
    return summarize_checkin_result


def save_analysis_to_file(analysis: Dict[str, Any], output_path: str = "analysis_output.json") -> None:
    """
    Save the clean analysis output to a JSON file with proper formatting.
    
    Args:
        analysis: The merged analysis result
        output_path: Path where to save the JSON file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        logger.info(f"Clean analysis saved to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save analysis to file: {e}")