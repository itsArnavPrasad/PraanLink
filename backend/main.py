# main.py
from fastapi import FastAPI, Request, status, UploadFile, File, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from marshmallow import ValidationError as MarshmallowValidationError
import os
from routers import checkins, prescriptions, reports, hospitals, insurances
from db.database import init_db, SessionLocal
from db.models import CheckIn, Prescription, Report, OverallReport
from sqlalchemy import desc
from utils.transcribe import transcribe_audio
from utils.summarize import summarize_checkin_text
from utils.ocr_summary import process_prescription, process_lab_report
from utils.overall_report import process_overall_report

app = FastAPI(
    title="PraanLink API",
    description="Backend API for PraanLink - Your Proactive Health Companion",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
UPLOAD_DIR = "uploads/checkins/audio"
TRANSCRIPT_DIR = "uploads/checkins/transcripts"
PRESCRIPTION_DIR = "uploads/prescriptions"
LAB_REPORT_DIR = "uploads/lab_reports"
OVERALL_REPORT_DIR = "uploads/overall_reports"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
os.makedirs(PRESCRIPTION_DIR, exist_ok=True)
os.makedirs(LAB_REPORT_DIR, exist_ok=True)
os.makedirs(OVERALL_REPORT_DIR, exist_ok=True)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
@app.on_event("startup")
async def startup_event():
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

# Serve PDF files endpoint - must be before routers to avoid conflicts
@app.get("/uploads/{file_path:path}")
async def serve_upload_file(file_path: str):
    """
    Serve files from the uploads directory (PDFs, images, etc.)
    """
    import pathlib
    
    # Get the absolute path to the backend directory (where main.py is located)
    backend_dir = pathlib.Path(__file__).parent.resolve()
    uploads_dir = backend_dir / "uploads"
    
    # Construct the full file path
    full_path = uploads_dir / file_path
    
    # Security check: ensure the path is within the uploads directory
    try:
        resolved_path = full_path.resolve()
        resolved_base = uploads_dir.resolve()
        resolved_path.relative_to(resolved_base)
    except ValueError:
        print(f"Security check failed: {resolved_path} not relative to {resolved_base}")
        return JSONResponse(
            status_code=403,
            content={"error": "Access denied"}
        )
    
    # Check if file exists
    if not full_path.exists():
        print(f"File not found: {full_path}")
        print(f"Absolute path: {full_path.resolve()}")
        print(f"Backend dir: {backend_dir}")
        print(f"Uploads dir: {uploads_dir}")
        return JSONResponse(
            status_code=404,
            content={"error": "File not found", "path": str(full_path)}
        )
    
    if not full_path.is_file():
        print(f"Path is not a file: {full_path}")
        return JSONResponse(
            status_code=404,
            content={"error": "Path is not a file"}
        )
    
    # Determine media type based on file extension
    media_type = None
    if full_path.suffix == ".pdf":
        media_type = "application/pdf"
    elif full_path.suffix in [".jpg", ".jpeg"]:
        media_type = "image/jpeg"
    elif full_path.suffix == ".png":
        media_type = "image/png"
    
    print(f"Serving file: {full_path} with media type: {media_type}")
    return FileResponse(
        path=str(full_path),
        media_type=media_type,
        filename=full_path.name
    )


# Register routers
app.include_router(checkins.router)
app.include_router(prescriptions.router)
app.include_router(reports.router)
app.include_router(hospitals.router)
app.include_router(insurances.router)

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to PraanLink API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Upload check-in audio endpoint
@app.post("/upload-checkin")
async def upload_checkin(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a check-in audio recording.
    Transcribes the audio and generates health insights.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # Save the uploaded file
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Step 1: Transcribe with WhisperX (or your transcription service)
        print(f"Transcribing check-in audio: {file.filename}")
        transcript = transcribe_audio(file_path, output_dir=TRANSCRIPT_DIR)
        
        # Step 2: Analyze the check-in using AI
        print("Summarizing check-in transcript...")
        summary = summarize_checkin_text(transcript)
        print("this is the summary: ", summary)
        print("Check-in analysis completed")
        
        # Step 3: Save to database using the CheckIn model
        inner_summary = summary.get("summary", {}) if summary else {}
        print("\n"*3)
        print(inner_summary)

        checkin = CheckIn(
            audio_path=file_path,
            transcript=transcript,
            summary=inner_summary.get("summary", ""),
            mood=inner_summary.get("mood", ""),
            symptoms=inner_summary.get("symptoms", []),
            medications_taken=inner_summary.get("medications_taken", []),
            sleep_quality=inner_summary.get("sleep_quality", ""),
            energy_level=inner_summary.get("energy_level", ""),
            concerns=inner_summary.get("concerns", ""),
            ai_insights=inner_summary.get("ai_insights", []),
            overall_score=inner_summary.get("overall_score", "")
        )
        
        db.add(checkin)
        db.commit()
        db.refresh(checkin)
        
        return {
            "id": checkin.id,
            "message": "Check-in stored successfully",
            "transcript": transcript,
            "summary": summary
        }
    
    except Exception as e:
        print(f"Error processing check-in: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Processing failed",
                "message": str(e),
                "id": None
            }
        )


# Upload prescription endpoint
@app.post("/upload-prescription")
async def upload_prescription(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a prescription image.
    Performs OCR and extracts structured prescription data.
    """
    file_path = os.path.join(PRESCRIPTION_DIR, file.filename)
    
    try:
        # Save the uploaded file
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        print(f"Processing prescription: {file.filename}")
        
        # Process prescription (OCR + Agent)
        result = process_prescription(file_path)
        
        if result.get("status") == "failed":
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Processing failed",
                    "message": result.get("error", "Unknown error"),
                }
            )
        
        structured_data = result.get("structured_data", {})
        doctor_info = structured_data.get("doctor_info", {})
        patient_info = structured_data.get("patient_info", {})
        summary = structured_data.get("summary", {})
        
        # Save to database
        prescription = Prescription(
            file_path=file_path,
            ocr_text=result.get("ocr_text", ""),
            doctor_name=doctor_info.get("name"),
            doctor_qualification=doctor_info.get("qualification"),
            doctor_registration_number=doctor_info.get("registration_number"),
            hospital=doctor_info.get("hospital"),
            doctor_contact_info=doctor_info.get("contact_info"),
            prescription_date=doctor_info.get("date"),
            patient_name=patient_info.get("name"),
            patient_age=patient_info.get("age"),
            patient_gender=patient_info.get("gender"),
            medicines=structured_data.get("medicines", []),
            diagnosis=summary.get("diagnosis"),
            symptoms=summary.get("symptoms"),
            advice=summary.get("advice"),
            follow_up=summary.get("follow_up"),
            prescription_summary=structured_data.get("prescription_summary"),
            structured_data=structured_data
        )
        
        db.add(prescription)
        db.commit()
        db.refresh(prescription)
        
        return {
            "id": prescription.id,
            "message": "Prescription processed successfully",
            "data": structured_data
        }
    
    except Exception as e:
        print(f"Error processing prescription: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Processing failed",
                "message": str(e)
            }
        )


# Upload lab report endpoint (fixed)
@app.post("/upload-lab-report")
async def upload_lab_report(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = os.path.join(LAB_REPORT_DIR, file.filename)

    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        print(f"Processing lab report: {file.filename}")
        result = process_lab_report(file_path)

        if result.get("status") == "failed":
            return JSONResponse(
                status_code=500,
                content={"error": "Processing failed", "message": result.get("error", "Unknown error")},
            )

        print("results:", result)
        structured_data = result.get("structured_data", {})

        # 🔹 Fix: map values properly
        raw_lab_data = {
            "report_date": structured_data.get("report_date"),
            "report_time": structured_data.get("report_time"),
            "metrics": structured_data.get("metrics", [])
        }

        # optional AI extensions
        lab_analysis = result.get("lab_analysis", {})
        lab_risk_scores = result.get("lab_risk_scores", {})
        lab_summary = result.get("lab_summary", {})

        # Save to database
        lab_report = Report(
            file_path=file_path,
            ocr_text=result.get("ocr_text", ""),
            report_date=raw_lab_data.get("report_date"),
            report_time=raw_lab_data.get("report_time"),
            raw_lab_data=raw_lab_data,
            lab_analysis=lab_analysis,
            lab_risk_scores=lab_risk_scores,
            overall_health_risk_index=lab_risk_scores.get("overall_health_risk_index"),
            severity=lab_risk_scores.get("severity"),
            critical_flags=lab_risk_scores.get("critical_flags", []),
            lab_summary_overview=lab_summary.get("overview"),
            key_findings=lab_summary.get("key_findings", []),
            overall_risk=lab_summary.get("overall_risk"),
            tone=lab_summary.get("tone"),
            recommendations=lab_summary.get("recommendations", []),
            critical_alerts=lab_summary.get("critical_alerts", []),
            structured_data=structured_data
        )

        db.add(lab_report)
        db.commit()
        db.refresh(lab_report)

        return {
            "id": lab_report.id,
            "message": "Lab report processed successfully",
            "data": structured_data
        }

    except Exception as e:
        print(f"Error processing lab report: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Processing failed", "message": str(e)}
        )


# Upload insurance consultation audio endpoint
@app.post("/upload-insurance-consultation")
async def upload_insurance_consultation(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process an insurance consultation audio recording.
    """
    consultation_dir = "uploads/insurance/audio"
    consultation_transcript_dir = "uploads/insurance/transcripts"
    os.makedirs(consultation_dir, exist_ok=True)
    os.makedirs(consultation_transcript_dir, exist_ok=True)
    
    file_path = os.path.join(consultation_dir, file.filename)
    
    try:
        # Save the uploaded file
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Transcribe the consultation
        print(f"Transcribing insurance consultation: {file.filename}")
        transcript = transcribe_audio(file_path, output_dir=consultation_transcript_dir)
        
        return {
            "message": "Insurance consultation stored successfully",
            "file_path": file_path,
            "transcript": transcript
        }
    
    except Exception as e:
        print(f"Error processing insurance consultation: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Processing failed",
                "message": str(e)
            }
        )


# Generate overall report endpoint
@app.post("/generate-overall-report")
async def generate_overall_report(db: Session = Depends(get_db)):
    """
    Generate a comprehensive overall medical report by:
    1. Retrieving all check-ins, prescriptions, and lab reports
    2. Sending aggregated data to report_agent
    3. Generating PDF report
    4. Saving OverallReport to database
    """
    try:
        print("Starting overall report generation...")
        
        # Process overall report (retrieve data, call agent, generate PDF, save to DB)
        result = process_overall_report(db, output_dir=OVERALL_REPORT_DIR)
        
        if result.get("status") == "failed":
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Report generation failed",
                    "message": result.get("error", "Unknown error"),
                    "details": result.get("details", "")
                }
            )
        
        if result.get("status") == "no_json_found":
            return JSONResponse(
                status_code=500,
                content={
                    "error": "No structured data found in agent response",
                    "message": "The report agent did not return structured data in the expected format"
                }
            )
        
        return {
            "id": result.get("id"),
            "message": "Overall report generated successfully",
            "pdf_file_path": result.get("pdf_file_path"),
            "status": "success"
        }
    
    except Exception as e:
        print(f"Error generating overall report: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "error": "Report generation failed",
                "message": str(e)
            }
        )


# Get latest overall report endpoint
@app.get("/latest-overall-report")
async def get_latest_overall_report(db: Session = Depends(get_db)):
    """
    Get the most recently generated overall report
    """
    try:
        # Get the latest overall report ordered by timestamp
        latest_report = db.query(OverallReport)\
            .order_by(desc(OverallReport.timestamp))\
            .first()
        
        if not latest_report:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "No overall report found",
                    "message": "No overall reports have been generated yet"
                }
            )
        
        return {
            "id": latest_report.id,
            "timestamp": latest_report.timestamp.isoformat() if latest_report.timestamp else None,
            "pdf_file_path": latest_report.pdf_file_path,
            "overall_health_index": latest_report.overall_health_index,
            "overall_severity": latest_report.overall_severity,
            "risk_level": latest_report.risk_level
        }
    
    except Exception as e:
        print(f"Error fetching latest overall report: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to fetch latest report",
                "message": str(e)
            }
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not Found", "message": "The requested resource was not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": "An unexpected error occurred"}
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation Error", "message": "Invalid request data", "details": exc.errors()}
    )

@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"error": "Database Error", "message": "A database error occurred"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)