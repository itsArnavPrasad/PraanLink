from google.adk.agents import LlmAgent
from google.genai import types

from .prompt import MEDICATION_AGGREGATOR_INSTRUCTION
from report_agent.models import MedicationOverview

medication_aggregator_agent = LlmAgent(
    name="medication_aggregator_agent",
    model="gemini-2.5-flash",
    description="Aggregates medication information from prescriptions and conversation summaries, prioritizing recent data and creating a comprehensive medication overview.",
    instruction=MEDICATION_AGGREGATOR_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
    output_schema=MedicationOverview,
    output_key="medication_overview",
)

