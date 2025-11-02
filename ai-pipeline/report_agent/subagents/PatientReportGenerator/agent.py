from google.adk.agents import LlmAgent
from google.genai import types

from .prompt import PATIENT_REPORT_GENERATOR_INSTRUCTION
from report_agent.models import FinalReport

patient_report_generator_agent = LlmAgent(
    name="patient_report_generator_agent",
    model="gemini-2.5-flash",
    description="Generates comprehensive patient health reports by synthesizing timeline, clinical trends, risk assessments, possible conditions, and medication overview into actionable insights.",
    instruction=PATIENT_REPORT_GENERATOR_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
    output_schema=FinalReport,
    output_key="final_report",
)

