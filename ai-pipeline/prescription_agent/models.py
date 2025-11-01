from pydantic import BaseModel
from typing import List, Optional

class DoctorInfo(BaseModel):
    name: Optional[str] = None
    qualification: Optional[str] = None
    registration_number: Optional[str] = None
    hospital: Optional[str] = None
    contact_info: Optional[str] = None
    date: Optional[str] = None

class PatientInfo(BaseModel):
    name: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None

class Medicine(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    special_instructions: Optional[str] = None

class PrescriptionSummary(BaseModel):
    diagnosis: Optional[str] = None
    symptoms: Optional[str] = None
    advice: Optional[str] = None
    follow_up: Optional[str] = None

class PrescriptionData(BaseModel):
    doctor_info: DoctorInfo
    patient_info: PatientInfo
    medicines: List[Medicine]
    summary: PrescriptionSummary
    prescription_summary: Optional[str] = None  # Natural language overview of the entire prescription