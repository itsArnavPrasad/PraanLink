# routers/reports.py
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Dict, Any
from db.database import get_db
from db.models import Report
from schemas import ReportSchema
from marshmallow import ValidationError
import json
import traceback

router = APIRouter(prefix="/api/reports", tags=["reports"])
schema = ReportSchema()
schemas = ReportSchema(many=True)


def safe_parse_json(data, default=None):
    """Safely parse JSON data"""
    if default is None:
        default = []
    
    if data is None:
        return default
    if isinstance(data, list):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except (json.JSONDecodeError, ValueError):
            return default
    if isinstance(data, dict):
        return data
    return default


# IMPORTANT: /summaries must be defined BEFORE /{report_id} to avoid route conflicts
@router.get("/summaries")
def get_report_summaries(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all lab report summaries, ordered by most recent first
    """
    try:
        print("Fetching lab reports from database...")
        reports = db.query(Report).order_by(desc(Report.timestamp)).limit(limit).all()
        print(f"Found {len(reports)} reports")
        
        summaries = []
        for i, report in enumerate(reports):
            try:
                print(f"\nProcessing report {i+1}/{len(reports)} (ID: {report.id})")
                
                # Safely parse JSON fields
                raw_lab_data = safe_parse_json(report.raw_lab_data, {})
                lab_analysis = safe_parse_json(report.lab_analysis, {})
                lab_risk_scores = safe_parse_json(report.lab_risk_scores, {})
                key_findings = safe_parse_json(report.key_findings, [])
                recommendations = safe_parse_json(report.recommendations, [])
                critical_alerts = safe_parse_json(report.critical_alerts, [])
                critical_flags = safe_parse_json(report.critical_flags, [])
                
                # Extract metrics from raw_lab_data if available
                metrics = []
                if isinstance(raw_lab_data, dict) and 'metrics' in raw_lab_data:
                    metrics = raw_lab_data.get('metrics', [])
                
                # Extract analyzed metrics from lab_analysis
                analyzed_metrics = []
                pattern_insights = []
                if isinstance(lab_analysis, dict):
                    analyzed_metrics = lab_analysis.get('analyzed_metrics', [])
                    pattern_insights = lab_analysis.get('pattern_insights', [])
                
                # Extract category scores from lab_risk_scores
                category_scores = []
                if isinstance(lab_risk_scores, dict):
                    category_scores = lab_risk_scores.get('category_scores', [])
                
                print(f"Report {report.id} - Date: {report.report_date}, Risk Index: {report.overall_health_risk_index}")
                
                summaries.append({
                    "id": report.id,
                    "timestamp": report.timestamp.isoformat() if report.timestamp else None,
                    "report_date": report.report_date or "",
                    "report_time": report.report_time or "",
                    "metrics": metrics,
                    "analyzed_metrics": analyzed_metrics,
                    "pattern_insights": pattern_insights,
                    "category_scores": category_scores,
                    "overall_health_risk_index": report.overall_health_risk_index or 0,
                    "severity": report.severity or "",
                    "critical_flags": critical_flags,
                    "lab_summary_overview": report.lab_summary_overview or "",
                    "key_findings": key_findings,
                    "overall_risk": report.overall_risk or "",
                    "tone": report.tone or "",
                    "recommendations": recommendations,
                    "critical_alerts": critical_alerts,
                    "file_path": report.file_path or ""
                })
                
            except Exception as e:
                print(f"Error processing report {report.id}: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                continue
        
        print(f"\nSuccessfully processed {len(summaries)} reports")
        
        return {
            "success": True,
            "count": len(summaries),
            "reports": summaries
        }
    
    except Exception as e:
        print(f"Error in get_report_summaries: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error fetching reports: {str(e)}")


@router.get("", response_model=dict)
def get_all_reports(db: Session = Depends(get_db)):
    """Get all reports"""
    reports = db.query(Report).all()
    return {"data": schemas.dump(reports)}


@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get lab report by ID with full details"""
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Safely parse JSON fields
        raw_lab_data = safe_parse_json(report.raw_lab_data, {})
        lab_analysis = safe_parse_json(report.lab_analysis, {})
        lab_risk_scores = safe_parse_json(report.lab_risk_scores, {})
        key_findings = safe_parse_json(report.key_findings, [])
        recommendations = safe_parse_json(report.recommendations, [])
        critical_alerts = safe_parse_json(report.critical_alerts, [])
        critical_flags = safe_parse_json(report.critical_flags, [])
        structured_data = safe_parse_json(report.structured_data, {})
        
        return {
            "id": report.id,
            "timestamp": report.timestamp.isoformat() if report.timestamp else None,
            "file_path": report.file_path or "",
            "ocr_text": report.ocr_text or "",
            "report_date": report.report_date or "",
            "report_time": report.report_time or "",
            "raw_lab_data": raw_lab_data,
            "lab_analysis": lab_analysis,
            "lab_risk_scores": lab_risk_scores,
            "overall_health_risk_index": report.overall_health_risk_index or 0,
            "severity": report.severity or "",
            "critical_flags": critical_flags,
            "lab_summary_overview": report.lab_summary_overview or "",
            "key_findings": key_findings,
            "overall_risk": report.overall_risk or "",
            "tone": report.tone or "",
            "recommendations": recommendations,
            "critical_alerts": critical_alerts,
            "structured_data": structured_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_report: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error fetching report: {str(e)}")


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_report(report_data: Dict[Any, Any] = Body(...), db: Session = Depends(get_db)):
    """Create a new report"""
    try:
        validated_data = schema.load(report_data)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=err.messages)
    
    report = Report(**validated_data)
    db.add(report)
    db.commit()
    db.refresh(report)
    return {"data": schema.dump(report), "message": "Report created successfully"}


@router.put("/{report_id}", response_model=dict)
def update_report(report_id: int, report_data: Dict[Any, Any] = Body(...), db: Session = Depends(get_db)):
    """Update a report"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    try:
        validated_data = schema.load(report_data, partial=True)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=err.messages)
    
    for key, value in validated_data.items():
        setattr(report, key, value)
    
    db.commit()
    db.refresh(report)
    return {"data": schema.dump(report), "message": "Report updated successfully"}


@router.delete("/{report_id}", response_model=dict)
def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a report"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(report)
    db.commit()
    return {"message": "Report deleted successfully"}