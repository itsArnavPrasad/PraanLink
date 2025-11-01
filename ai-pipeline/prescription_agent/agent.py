from google.adk.agents import LlmAgent
from google.genai import types

from .prompt import PRESCRIPTION_EXTRACTION_INSTRUCTION
from prescription_agent.models import PrescriptionData  # define this schema in models.py

prescription_agent = LlmAgent(
    name="prescription_agent",
    model="gemini-2.5-flash",
    description=(
        "Extracts structured prescription information from raw OCR text, including "
        "doctor details, patient information, prescribed medicines, and clinical summary."
    ),
    instruction=PRESCRIPTION_EXTRACTION_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
    output_schema=PrescriptionData,
    output_key="prescription_data",
)

root_agent = prescription_agent