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
    mood: Optional[str] = None
    symptoms: List[str] = []
    medications_taken: List[str] = []
    sleep_quality: Optional[str] = None
    energy_level: Optional[str] = None
    concerns: Optional[str] = None
    summary: Optional[str] = None
    ai_insights: List[str] = []
    overall_score: Optional[str] = None



# ---------- Final aggregated medical report ----------
class FinalReport(BaseModel):
    patient_overview: str
    risk_level: str                  # Low / Moderate / High
    next_steps: List[str] = []
    summary_comment: Optional[str] = None


# ---------- Final aggregated health report ----------
class PatientHealthReport(BaseModel):
    timeline: Timeline = Timeline()
    clinical_trends: ClinicalTrends = ClinicalTrends()
    risk_and_severity: RiskAndSeverity = RiskAndSeverity(overall_health_index=0.0, overall_severity="Low")
    possible_conditions: PossibleConditions = PossibleConditions()
    conversation_summary: ConversationSummary = ConversationSummary()
    final_report: FinalReport = FinalReport(patient_overview="", risk_level="Low", next_steps=[])
