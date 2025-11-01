from google.adk.agents import SequentialAgent

# Import sub-agents
from .subagents.LabParser.agent import lab_parser_agent
from .subagents.LabAnalyser.agent import lab_analyzer_agent
from .subagents.LabRiskScorer.agent import lab_risk_scorer_agent
from .subagents.LabSummarizer.agent import lab_summary_agent
from .subagents.LabAggregator.agent import lab_aggregator_agent

# --- Root Sequential Orchestration Agent ---
lab_report_main_agent = SequentialAgent(
    name="lab_report_main_agent",
    description="Executes a sequential workflow for complete lab report analysis: parsing, analysis, risk scoring, summarization, and final aggregation of all outputs.",
    sub_agents=[
        lab_parser_agent,
        lab_analyzer_agent,
        lab_risk_scorer_agent,
        lab_summary_agent,
        lab_aggregator_agent,  # Final agent that aggregates all outputs
    ],
)

root_agent = lab_report_main_agent