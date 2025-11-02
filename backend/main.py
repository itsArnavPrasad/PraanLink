# main.py
from fastapi import FastAPI, Request, status, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from marshmallow import ValidationError as MarshmallowValidationError
import os
from routers import checkins, prescriptions, reports, hospitals, insurances
from db.database import init_db, SessionLocal
from db.models import CheckIn
from utils.transcribe import transcribe_audio
from utils.summarize import summarize_checkin_text

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
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

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
        # summarize = "check"
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
        
        # You can add analysis here if needed
        # analysis = analyze_insurance_consultation(transcript)
        
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