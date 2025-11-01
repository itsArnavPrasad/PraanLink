from google.adk.agents import LlmAgent
from google.genai import types

from .prompt import LAB_RISK_SCORER_INSTRUCTION
from lab_report_agent.models import LabRiskScores  # define this schema in models.py

lab_risk_scorer_agent = LlmAgent(
    name="lab_risk_scorer_agent",
    model="gemini-2.5-flash",
    description="Quantifies patient health risks based on analyzed lab data, computes risk scores per health category, and provides overall health severity assessment.",
    instruction=LAB_RISK_SCORER_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
    output_schema=LabRiskScores,
    output_key="lab_risk_scores",
)