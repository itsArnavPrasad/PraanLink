from google.adk.agents import SequentialAgent

# Import sub-agents
from report_agent.subagents.TimelineBuilder.agent import timeline_builder_agent
from report_agent.subagents.ClinicalTrendAnalyser.agent import clinical_trend_analyzer_agent
from report_agent.subagents.RiskScoringandSeverity.agent import risk_and_severity_agent
from report_agent.subagents.DiseaseInference.agent import disease_inference_agent
from report_agent.subagents.MedicationAggregator.agent import medication_aggregator_agent
from report_agent.subagents.PatientReportGenerator.agent import patient_report_generator_agent
from report_agent.subagents.ReportAggregator.agent import report_aggregator_agent

# --- Root Sequential Orchestration Agent ---
# This agent orchestrates a sequential workflow that:
# 1. Builds chronological timeline (with date-weighted conversation summaries)
# 2. Analyzes clinical trends across multiple lab reports (prioritizing recent reports)
# 3. Calculates risk scores and severity (using recent data)
# 4. Infers possible conditions (based on symptoms, labs, medications)
# 5. Aggregates medications (from prescriptions and conversations, prioritizing recent)
# 6. Generates comprehensive patient health report
# 7. Aggregates all outputs into final PatientHealthReport
report_builder_root_agent = SequentialAgent(
    name="report_builder_root_agent",
    description=(
        "Unified patient health report generator that consolidates all available structured data "
        "(call transcripts, lab reports, prescriptions) into a comprehensive, chronological, "
        "clinically meaningful report. Processes data with date-based weighting, prioritizing "
        "recent information and analyzing trends across time."
    ),
    sub_agents=[
        timeline_builder_agent,          # Step 1: Build chronological timeline
        clinical_trend_analyzer_agent,   # Step 2: Analyze lab trends across time
        risk_and_severity_agent,         # Step 3: Calculate risk scores
        disease_inference_agent,         # Step 4: Infer possible conditions
        medication_aggregator_agent,     # Step 5: Aggregate medications
        patient_report_generator_agent,  # Step 6: Generate comprehensive report
        report_aggregator_agent,         # Step 7: Aggregate all outputs
    ],
)

root_agent = report_builder_root_agent