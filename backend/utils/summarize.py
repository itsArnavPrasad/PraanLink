# summarize.py
import requests
import json
import re
from typing import Dict, Any, List
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ADK_SERVER_URL = "http://localhost:5010"


def call_agent(agent_name: str, transcript: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call a single ADK agent API (session creation + /run request).
    """
    try:
        print("-----" * 10)
        print(f"Calling {agent_name} at {ADK_SERVER_URL}")

        user_id = "u_backend"
        session_id = f"s_{uuid.uuid4().hex[:8]}"

        # Step 1️⃣: Create session
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

        print(f"Session created for {agent_name}: {session_id}")

        # Step 2️⃣: Run transcript
        payload = {
            "app_name": agent_name,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": json.dumps(transcript, indent=2)}]
            }
        }

        print(f"Payload for {agent_name}: {json.dumps(payload, indent=2)}")

        run_response = requests.post(
            f"{ADK_SERVER_URL}/run",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=600
        )
        print("\n")
        print("This is the run_response:", run_response)
        print("\n")

        if run_response.status_code != 200:
            return {
                "error": f"{agent_name} run failed",
                "details": run_response.text
            }

        print(f"{agent_name} completed successfully")
        return run_response.json()

    except requests.exceptions.Timeout:
        return {"error": f"{agent_name} request timed out"}

    except requests.exceptions.RequestException as e:
        return {"error": f"{agent_name} request failed: {str(e)}"}

    except json.JSONDecodeError:
        return {"error": f"{agent_name} returned invalid JSON"}


def extract_json_from_text(data: Any) -> List[Dict[str, Any]]:
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
                    # If that fails, look for code blocks
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



def summarize_checkin_text(transcript: Dict[str, Any]) -> Dict[str, Any]:
    """
    Summarize check-in text using the conversation_summarizer_agent only.
    Extract and return structured JSON output if present.
    """
    logger.info("Starting summarization with conversation_summarizer_agent")

    response = call_agent("conversation_summarizer_agent", transcript)
    print("This is the response: ", response)
    extracted_jsons = extract_json_from_text(response)

    if not extracted_jsons:
        print("No structured JSON found in summarizer response")
        return {
            "summary": None,
            "raw_response": response,
            "status": "no_json_found"
        }

    summary_data = extracted_jsons[0]
    print("Successfully extracted structured summary JSON")

    return {
        "summary": summary_data,
        "status": "success"
    }


def save_summary_to_file(summary: Dict[str, Any], output_path: str = "summary_output.json") -> None:
    """
    Save the summarization result to a JSON file.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        logger.info(f"Summary saved to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save summary: {e}")
