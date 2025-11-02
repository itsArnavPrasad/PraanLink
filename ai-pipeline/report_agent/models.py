from pydantic import BaseModel
from typing import List, Optional


# ---------- Timeline Builder output ----------
class TimelineEvent(BaseModel):
    date: Optional[str] = None
    event_type: str                 # symptom_onset / doctor_visit / lab_test / medication_update
    description: str
    source: Optional[str] = None    # conversation_transcript / lab_report


class Timeline(BaseModel):
    events: List[TimelineEvent] = []


# ---------- Clinical Trend Analyzer output ----------
class MetricTrend(BaseModel):
    metric: str                     # metric name (e.g., "Glucose")
    previous_value: Optional[float] = None
    current_value: Optional[float] = None
    trend: str                     # increasing / decreasing / stable / improving
    status: str                    # normal / abnormal_high / abnormal_low
    clinical_comment: Optional[str] = None


class ClinicalTrends(BaseModel):
    trends: List[MetricTrend] = []
    overall_summary: Optional[str] = None


# ---------- Risk Scoring and Severity output ----------
class DiseaseRisk(BaseModel):
    disease: str                    # disease name (e.g., "Diabetes")
    risk_score: float           # 0-100
    severity_level: str             # Low / Moderate / High


class RiskAndSeverity(BaseModel):
    disease_risks: List[DiseaseRisk] = []
    overall_health_index: float     # 0-100 (higher is better)
    overall_severity: str           # Low / Moderate / High
    clinical_comment: Optional[str] = None


# ---------- Disease Inference output ----------
class PossibleCondition(BaseModel):
    condition: str                  # condition name (e.g., "Type 2 Diabetes")
    confidence: float               # 0-100
    recommended_action: str         # single recommended action string


class PossibleConditions(BaseModel):
    conditions: List[PossibleCondition] = []
    summary_comment: Optional[str] = None


# ---------- Conversation Summarizer output ----------
class ConversationSummary(BaseModel):
    date: Optional[str] = None              # Date of the conversation (for chronological weighting)
    mood: Optional[str] = None
    symptoms: List[str] = []
    medications_taken: List[str] = []
    sleep_quality: Optional[str] = None
    energy_level: Optional[str] = None
    concerns: Optional[str] = None
    summary: Optional[str] = None
    ai_insights: List[str] = []
    overall_score: Optional[str] = None


# ---------- Medication Aggregator output ----------
class Medication(BaseModel):
    name: str                                # Medication name
    dosage: Optional[str] = None            # e.g., "5mg", "75mg"
    frequency: Optional[str] = None          # e.g., "once daily", "twice daily"
    duration: Optional[str] = None          # e.g., "30 days", "ongoing"
    start_date: Optional[str] = None        # When medication was started
    end_date: Optional[str] = None          # When medication was stopped (if applicable)
    special_instructions: Optional[str] = None
    source: Optional[str] = None            # "prescription" or "conversation_summary"

class MedicationOverview(BaseModel):
    current_medications: List[Medication] = []       # Active medications
    past_medications: List[Medication] = []          # Discontinued medications
    medication_timeline: List[Medication] = []        # Chronological list of all medications
    medication_summary: Optional[str] = None          # Summary of medication history


# ---------- Final aggregated medical report ----------
class FinalReport(BaseModel):
    patient_overview: str
    risk_level: str                  # Low / Moderate / High
    next_steps: List[str] = []
    summary_comment: Optional[str] = None


# ---------- Final aggregated health report ----------
# This schema aggregates outputs from all sub-agents:
# - timeline: from timeline_builder_agent (output_key: "timeline")
# - clinical_trends: from clinical_trend_analyzer_agent (output_key: "clinical_trends")
# - risk_and_severity: from risk_and_severity_agent (output_key: "risk_and_severity")
# - possible_conditions: from disease_inference_agent (output_key: "possible_conditions")
# - medication_overview: from medication_aggregator_agent (output_key: "medication_overview")
# - final_report: from patient_report_generator_agent (output_key: "final_report")
class PatientHealthReport(BaseModel):
    timeline: Timeline                          # Chronological medical events
    clinical_trends: ClinicalTrends            # Lab metric trends and changes
    risk_and_severity: RiskAndSeverity          # Disease risks and severity assessment
    possible_conditions: PossibleConditions    # Inferred conditions with confidence
    medication_overview: MedicationOverview     # Current and past medications
    final_report: FinalReport                   # Comprehensive patient health report
