from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

from .prompt import AGENT_INSTRUCTION

# --- Import Sub-Agents ---
from report_agent.subagents.TimelineBuilder.agent import timeline_builder_agent
from report_agent.subagents.ClinicalTrendAnalyser.agent import clinical_trend_analyzer_agent
from report_agent.subagents.RiskScoringandSeverity.agent import risk_and_severity_agent
from report_agent.subagents.DiseaseInference.agent import disease_inference_agent
from report_agent.subagents.ConversationSummarizer.agent import conversation_summarizer_agent


# --- Root Orchestration Agent ---
report_builder_root_agent = LlmAgent(
    name="report_builder_root_agent",
    model="gemini-2.5-flash",
    description=(
        "Root orchestrator agent that ingests conversation transcripts and lab reports, invokes specialized sub-agents for clinical timeline, trend analysis, risk scoring, disease inference, and conversation summarization, and merges results into a unified JSON report"
    ),
    instruction=AGENT_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
    tools=[
        AgentTool(agent=timeline_builder_agent),
        AgentTool(agent=clinical_trend_analyzer_agent),
        AgentTool(agent=risk_and_severity_agent),
        AgentTool(agent=disease_inference_agent),
        AgentTool(agent=conversation_summarizer_agent),
    ],
)

root_agent = report_builder_root_agent