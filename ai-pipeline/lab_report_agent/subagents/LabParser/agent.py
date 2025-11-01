from google.adk.agents import LlmAgent
from google.genai import types

from .prompt import LAB_PARSER_INSTRUCTION
from lab_report_agent.models import LabData  # reference to your models.py

lab_parser_agent = LlmAgent(
    name="lab_parser_agent",
    model="gemini-2.5-flash",
    description="Parses raw lab report text into structured test data, identifying test names, values, units, and reference ranges.",
    instruction=LAB_PARSER_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
    output_schema=LabData,
    output_key="raw_lab_data",
)