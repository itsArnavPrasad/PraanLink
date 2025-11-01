from google.adk.agents import LlmAgent
from google.genai import types

from .prompt import DISEASE_INFERENCE_INSTRUCTION
from report_agent.models import PossibleConditions  # Define this in models.py as a Pydantic class

disease_inference_agent = LlmAgent(
    name="disease_inference_agent",
    model="gemini-2.5-flash",
    description="Infers possible diseases or conditions from clinical context and suggests next diagnostic steps.",
    instruction=DISEASE_INFERENCE_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
    output_schema=PossibleConditions,
    output_key="possible_conditions",
)