from pydantic import BaseModel
from typing import List, Optional


# ---------- Lab Parser Agent Output ----------
class LabMetric(BaseModel):
    test_name: str                                # e.g., "LDL Cholesterol"
    category: Optional[str] = None                # e.g., "Lipid Profile"
    value: Optional[float] = None                 # numeric result value
    unit: Optional[str] = None                    # e.g., "mg/dL"
    reference_range: Optional[str] = None         # e.g., "0–130 mg/dL"
    interpretation: Optional[str] = None          # preliminary or parsed interpretation

class LabData(BaseModel):
    report_date: Optional[str] = None              # Date when the lab report was generated (e.g., "2024-01-15" or "15/01/2024")
    report_time: Optional[str] = None              # Time when the lab report was generated (e.g., "14:30" or "02:30 PM")
    metrics: List[LabMetric] = []


# ---------- Lab Analyzer Agent Output ----------
class AnalyzedMetric(BaseModel):
    test_name: str                                # e.g., "LDL Cholesterol"
    status: str                                   # low / normal / high / critical
    value: float
    unit: str
    reference_range: Optional[str] = None
    interpretation: str                           # e.g., "High LDL cholesterol indicates dyslipidemia risk"

class LabAnalysis(BaseModel):
    analyzed_metrics: List[AnalyzedMetric] = []
    pattern_insights: List[str] = []              # e.g., ["High LDL + Low HDL → possible dyslipidemia"]
    summary: Optional[str] = None                 # concise interpretation summary


# ---------- Lab Risk Scorer Agent Output ----------
class CategoryScore(BaseModel):
    category: str                                 # e.g., "Cardiovascular", "Metabolic"
    score: float                                  # 0.0 to 1.0

class LabRiskScores(BaseModel):
    category_scores: List[CategoryScore] = []    # e.g., [{"category": "Cardiovascular", "score": 0.72}, ...]
    overall_health_risk_index: float              # 0–1 scale
    severity: str                                 # Low / Moderate / High
    critical_flags: List[str] = []                # list of concerning findings
    summary: str                                  # clinical risk interpretation summary


# ---------- Lab Summary Agent Output ----------
class KeyFinding(BaseModel):
    metric: str                                   # e.g., "LDL Cholesterol"
    value: str                                    # e.g., "155 mg/dL"
    interpretation: str                           # e.g., "High"

class LabSummary(BaseModel):
    overview: str                                 # natural-language overview
    key_findings: List[KeyFinding] = []
    overall_risk: str                             # Low / Moderate / High
    tone: str                                     # Informative / Cautionary / Reassuring
    recommendations: List[str] = []               # lifestyle or follow-up advice
    critical_alerts: List[str] = []               # e.g., ["Very high LDL", "Low hemoglobin"]


# ---------- Final Aggregated Lab Report ----------
# This schema aggregates outputs from all sub-agents:
# - raw_lab_data: from lab_parser_agent (output_key: "raw_lab_data")
# - lab_analysis: from lab_analyzer_agent (output_key: "lab_analysis")
# - lab_risk_scores: from lab_risk_scorer_agent (output_key: "lab_risk_scores")
# - lab_summary: from lab_summary_agent (output_key: "lab_summary")
class FinalLabReport(BaseModel):
    raw_lab_data: LabData                  # Parsed lab metrics, report date, and time
    lab_analysis: LabAnalysis              # Analyzed metrics with status and interpretations
    lab_risk_scores: LabRiskScores         # Risk scores by category and overall health risk
    lab_summary: LabSummary                # Natural language overview and recommendations