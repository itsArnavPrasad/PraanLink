from google.adk.agents import LlmAgent
from google.genai import types

from .prompt import CONVERSATION_SUMMARIZER_INSTRUCTION
from report_agent.models import ConversationSummary  # Define this in models.py as a Pydantic class

conversation_summarizer_agent = LlmAgent(
    name="conversation_summarizer_agent",
    model="gemini-2.5-flash",
    description="Summarize the conversation between a medical ai agent and a user patient conversations into concise structured notes with key health attributes.",
    instruction=CONVERSATION_SUMMARIZER_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
    output_schema=ConversationSummary,
    output_key="conversation_summary",
)

root_agent = conversation_summarizer_agent