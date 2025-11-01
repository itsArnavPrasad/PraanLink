from google.adk.agents import LlmAgent
from google.genai import types

from .prompt import LAB_AGGREGATOR_INSTRUCTION
from lab_report_agent.models import FinalLabReport

lab_aggregator_agent = LlmAgent(
    name="lab_aggregator_agent",
    model="gemini-2.5-flash",
    description="Aggregates outputs from all previous lab report analysis sub-agents into a final comprehensive report.",
    instruction=LAB_AGGREGATOR_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
    output_schema=FinalLabReport,
    output_key="final_lab_report",
)

