from google.adk.agents import LlmAgent
from google.genai import types

from .prompt import REPORT_AGGREGATOR_INSTRUCTION
from report_agent.models import PatientHealthReport

report_aggregator_agent = LlmAgent(
    name="report_aggregator_agent",
    model="gemini-2.5-flash",
    description="Aggregates outputs from all previous patient health report analysis sub-agents into a final comprehensive PatientHealthReport.",
    instruction=REPORT_AGGREGATOR_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
    output_schema=PatientHealthReport,
    output_key="patient_health_report",
)

