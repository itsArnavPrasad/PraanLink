from google.adk.agents import LlmAgent
from google.genai import types

from .prompt import RISK_AND_SEVERITY_INSTRUCTION
from report_agent.models import RiskAndSeverity  # Define this in models.py as a Pydantic class

risk_and_severity_agent = LlmAgent(
    name="risk_and_severity_agent",
    model="gemini-2.5-flash",
    description="Calculates disease-specific risk scores, overall health index, and assigns severity levels.",
    instruction=RISK_AND_SEVERITY_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
    output_schema=RiskAndSeverity,
    output_key="risk_and_severity",
)