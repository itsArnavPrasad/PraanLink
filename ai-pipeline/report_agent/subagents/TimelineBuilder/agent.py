from google.adk.agents import LlmAgent
from google.genai import types

from .prompt import TIMELINE_BUILDER_INSTRUCTION
from report_agent.models import Timeline  # You can define this in models.py as a Pydantic class

timeline_builder_agent = LlmAgent(
    name="timeline_builder_agent",
    model="gemini-2.5-flash",
    description="Builds or updates a chronological medical timeline for the patient using conversation transcripts and lab data.",
    instruction=TIMELINE_BUILDER_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
    output_schema=Timeline,
    output_key="timeline",
)