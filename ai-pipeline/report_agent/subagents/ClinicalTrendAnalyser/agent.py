from google.adk.agents import LlmAgent
from google.genai import types

from .prompt import CLINICAL_TREND_ANALYZER_INSTRUCTION
from report_agent.models import ClinicalTrends

clinical_trend_analyzer_agent = LlmAgent(
    name="clinical_trend_analyzer_agent",
    model="gemini-2.5-flash",
    description="Analyzes lab reports to detect clinical trends, flag abnormalities, and summarize changes in patient metrics.",
    instruction=CLINICAL_TREND_ANALYZER_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
    output_schema=ClinicalTrends,
    output_key="clinical_trends",
)

