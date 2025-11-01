from google.adk.agents import LlmAgent
from google.genai import types

from .prompt import LAB_ANALYZER_INSTRUCTION
from lab_report_agent.models import LabAnalysis  # define this schema in your models.py

lab_analyzer_agent = LlmAgent(
    name="lab_analyzer_agent",
    model="gemini-2.5-flash",
    description="Analyzes structured lab report data to detect abnormal values, classify results, and identify correlated clinical patterns.",
    instruction=LAB_ANALYZER_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
    output_schema=LabAnalysis,
    output_key="lab_analysis",
)