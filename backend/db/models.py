from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.sql import func
from db.database import Base


class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    audio_path = Column(String)
    transcript = Column(JSON) 
    summary = Column(JSON)     
    mood = Column(String)
    symptoms = Column(JSON)    
    medications_taken = Column(JSON)
    sleep_quality = Column(String)
    energy_level = Column(String)
    concerns = Column(JSON)
    ai_insights = Column(JSON)
    overall_score = Column(String)


class Prescription(Base):
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    ocr_text = Column(Text, nullable=True)
    
    # Doctor information
    doctor_name = Column(String, nullable=True)
    doctor_qualification = Column(String, nullable=True)
    doctor_registration_number = Column(String, nullable=True)
    hospital = Column(String, nullable=True)
    doctor_contact_info = Column(String, nullable=True)
    prescription_date = Column(String, nullable=True)
    
    # Patient information
    patient_name = Column(String, nullable=True)
    patient_age = Column(String, nullable=True)
    patient_gender = Column(String, nullable=True)
    
    # Medicines (stored as JSON array)
    # Each medicine: {name, dosage, frequency, duration, special_instructions}
    medicines = Column(JSON, nullable=True)
    
    # Summary information
    diagnosis = Column(Text, nullable=True)
    symptoms = Column(Text, nullable=True)
    advice = Column(Text, nullable=True)
    follow_up = Column(String, nullable=True)
    prescription_summary = Column(Text, nullable=True)
    
    # Full structured data as JSON backup
    structured_data = Column(JSON, nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    ocr_text = Column(Text, nullable=True)
    
    # Report metadata
    report_date = Column(String, nullable=True)
    report_time = Column(String, nullable=True)
    
    # Raw lab data (stored as JSON)
    # Structure: {report_date, report_time, metrics: [{test_name, category, value, unit, reference_range, interpretation}]}
    raw_lab_data = Column(JSON, nullable=True)
    
    # Lab analysis (analyzed metrics with interpretations)
    # Structure: {analyzed_metrics: [{test_name, status, value, unit, reference_range, interpretation}], pattern_insights: [], summary}
    lab_analysis = Column(JSON, nullable=True)
    
    # Risk scores
    # Structure: {category_scores: [{category, score}], overall_health_risk_index, severity, critical_flags, summary}
    lab_risk_scores = Column(JSON, nullable=True)
    
    # Overall health risk index
    overall_health_risk_index = Column(Float, nullable=True)
    severity = Column(String, nullable=True)
    critical_flags = Column(JSON, nullable=True)
    
    # Lab summary
    # Structure: {overview, key_findings: [{metric, value, interpretation}], overall_risk, tone, recommendations: [], critical_alerts: []}
    lab_summary_overview = Column(Text, nullable=True)
    key_findings = Column(JSON, nullable=True)
    overall_risk = Column(String, nullable=True)
    tone = Column(String, nullable=True)
    recommendations = Column(JSON, nullable=True)
    critical_alerts = Column(JSON, nullable=True)
    
    # Full structured data as JSON backup
    structured_data = Column(JSON, nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class Hospital(Base):
    __tablename__ = "hospitals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    speciality = Column(String, nullable=False)
    location = Column(String, nullable=False)
    reviews = Column(Float, nullable=True)
    contact_info = Column(String, nullable=True)
    description = Column(Text, nullable=True)


class Insurance(Base):
    __tablename__ = "insurances"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    coverage = Column(String, nullable=False)
    premium = Column(Float, nullable=False)
    key_features = Column(JSON, nullable=True)
    provider = Column(String, nullable=False)