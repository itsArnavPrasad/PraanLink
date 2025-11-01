from google.adk.agents import LlmAgent
from google.genai import types

from .prompt import LAB_SUMMARY_INSTRUCTION
from lab_report_agent.models import LabSummary  # define this schema in models.py

lab_summary_agent = LlmAgent(
    name="lab_summary_agent",
    model="gemini-2.5-flash",
    description="Generates an interpretive lab summary and health recommendations based on parsed values, analysis insights, and quantified risk scores.",
    instruction=LAB_SUMMARY_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
    output_schema=LabSummary,
    output_key="lab_summary",
)