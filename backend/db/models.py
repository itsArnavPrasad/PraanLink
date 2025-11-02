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

    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Prescription(Base):
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
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

