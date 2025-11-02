import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus.flowables import HRFlowable
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
from typing import Dict, Any, Optional

# Color scheme
PRIMARY_COLOR = "#1a4d7a"  # Dark blue
SECONDARY_COLOR = "#2e7db4"  # Medium blue
ACCENT_COLOR = "#d32f2f"  # Red for warnings
SUCCESS_COLOR = "#2e7d32"  # Green
INFO_COLOR = "#1976d2"  # Light blue
LIGHT_GRAY = "#f5f5f5"
MEDIUM_GRAY = "#e0e0e0"
DARK_GRAY = "#424242"


def get_status_color(status: str) -> str:
    """Map status to color"""
    if not status:
        return DARK_GRAY
    status_lower = str(status).lower()
    if 'normal' in status_lower or ('low' in status_lower and 'abnormal' not in status_lower):
        return SUCCESS_COLOR
    elif 'abnormal' in status_lower or 'high' in status_lower:
        return ACCENT_COLOR
    elif 'moderate' in status_lower:
        return "#f57c00"  # Orange
    else:
        return DARK_GRAY


def get_severity_color(severity: str) -> str:
    """Map severity level to color"""
    if not severity:
        return DARK_GRAY
    severity_lower = str(severity).lower()
    if 'low' in severity_lower:
        return SUCCESS_COLOR
    elif 'moderate' in severity_lower:
        return "#f57c00"  # Orange
    elif 'high' in severity_lower:
        return ACCENT_COLOR
    else:
        return DARK_GRAY


def generate_charts(clinical_trends: list, risk_data: Optional[Dict[str, Any]], output_dir: str = "charts") -> Dict[str, str]:
    """Generate multiple enhanced charts"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    chart_paths = {}
    
    # Chart 1: Enhanced Bar Chart for Clinical Trends
    if clinical_trends and len(clinical_trends) > 0:
        try:
            metrics = [str(trend.get('metric', 'N/A')) for trend in clinical_trends]
            values = []
            for trend in clinical_trends:
                val = trend.get('current_value')
                try:
                    values.append(float(val) if val is not None else 0.0)
                except (ValueError, TypeError):
                    values.append(0.0)
            
            status_colors = [get_status_color(trend.get('status', '')) for trend in clinical_trends]
            
            fig, ax = plt.subplots(figsize=(12, 7))
            bars = ax.bar(range(len(metrics)), values, color=status_colors, alpha=0.8, edgecolor='white', linewidth=1.5)
            
            # Add value labels
            for i, (bar, val) in enumerate(zip(bars, values)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            ax.set_xticks(range(len(metrics)))
            ax.set_xticklabels(metrics, rotation=45, ha='right', fontsize=9)
            ax.set_ylabel('Value', fontsize=11, fontweight='bold')
            ax.set_title('Clinical Trends - Current Values', fontsize=14, fontweight='bold', pad=20)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.set_facecolor('#fafafa')
            
            # Create legend for status colors
            normal_patch = mpatches.Patch(color=SUCCESS_COLOR, label='Normal')
            abnormal_patch = mpatches.Patch(color=ACCENT_COLOR, label='Abnormal')
            ax.legend(handles=[normal_patch, abnormal_patch], loc='upper right', framealpha=0.9)
            
            plt.tight_layout()
            chart_paths['clinical_trends'] = os.path.join(output_dir, "clinical_trends.png")
            plt.savefig(chart_paths['clinical_trends'], dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
        except Exception as e:
            print(f"Error generating clinical trends chart: {e}")
    
    # Chart 2: Risk Score Visualization
    if risk_data and risk_data.get('disease_risks'):
        try:
            disease_risks = risk_data['disease_risks']
            if isinstance(disease_risks, list) and len(disease_risks) > 0:
                diseases = [str(risk.get('disease', 'N/A')) for risk in disease_risks]
                risk_scores = []
                for risk in disease_risks:
                    score = risk.get('risk_score')
                    try:
                        risk_scores.append(float(score) if score is not None else 0.0)
                    except (ValueError, TypeError):
                        risk_scores.append(0.0)
                
                severity_colors = [get_severity_color(risk.get('severity_level', '')) for risk in disease_risks]
                
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.barh(diseases, risk_scores, color=severity_colors, alpha=0.8, edgecolor='white', linewidth=2)
                
                # Add value labels
                for i, (bar, score) in enumerate(zip(bars, risk_scores)):
                    width = bar.get_width()
                    ax.text(width + 1, bar.get_y() + bar.get_height()/2.,
                            f'{int(score)}', ha='left', va='center', fontsize=11, fontweight='bold')
                
                ax.set_xlabel('Risk Score', fontsize=12, fontweight='bold')
                ax.set_title('Disease Risk Assessment', fontsize=14, fontweight='bold', pad=20)
                ax.set_xlim(0, 100)
                ax.grid(axis='x', alpha=0.3, linestyle='--')
                ax.set_facecolor('#fafafa')
                
                plt.tight_layout()
                chart_paths['risk_scores'] = os.path.join(output_dir, "risk_scores.png")
                plt.savefig(chart_paths['risk_scores'], dpi=300, bbox_inches='tight', facecolor='white')
                plt.close()
        except Exception as e:
            print(f"Error generating risk scores chart: {e}")
    
    # Chart 3: Health Index Gauge (if health index exists)
    if risk_data and risk_data.get('overall_health_index') is not None:
        try:
            health_index = risk_data.get('overall_health_index')
            overall_severity = risk_data.get('overall_severity', 'Moderate')
            severity_color = get_severity_color(overall_severity)
            
            try:
                health_index = float(health_index)
            except (ValueError, TypeError):
                health_index = 50.0
            
            fig = plt.figure(figsize=(10, 7))
            ax = fig.add_subplot(111, projection='polar')
            
            # Create gauge background with color zones
            # High Risk zone: 0-40 (left side, red)
            theta_high = np.linspace(np.pi, np.pi * 0.6, 50)
            ax.fill_between(theta_high, 0.7, 1.0, color=ACCENT_COLOR, alpha=0.25, zorder=1)
            
            # Moderate zone: 40-70 (middle, orange)
            theta_mod = np.linspace(np.pi * 0.6, np.pi * 0.3, 50)
            ax.fill_between(theta_mod, 0.7, 1.0, color="#f57c00", alpha=0.25, zorder=1)
            
            # Low Risk zone: 70-100 (right side, green)
            theta_low = np.linspace(np.pi * 0.3, 0, 50)
            ax.fill_between(theta_low, 0.7, 1.0, color=SUCCESS_COLOR, alpha=0.25, zorder=1)
            
            # Outer ring
            theta_ring = np.linspace(np.pi, 0, 200)
            ax.plot(theta_ring, np.ones_like(theta_ring), 'k-', linewidth=2.5, zorder=2)
            ax.plot(theta_ring, np.ones_like(theta_ring) * 0.7, 'k-', linewidth=1.5, zorder=2)
            
            # Scale markers and labels
            scale_points = [0, 25, 50, 75, 100]
            scale_angles = [np.pi * (1 - p / 100) for p in scale_points]
            
            for angle, value in zip(scale_angles, scale_points):
                # Marker lines
                ax.plot([angle, angle], [0.95, 1.0], 'k-', linewidth=1.5, zorder=3)
                # Labels
                label_radius = 1.15
                ax.text(angle, label_radius, str(value), ha='center', va='center',
                       fontsize=10, fontweight='bold', zorder=4)
            
            # Add severity zone labels
            ax.text(np.pi * 0.85, 0.85, 'HIGH\nRISK', ha='center', va='center',
                   fontsize=9, fontweight='bold', color=ACCENT_COLOR, 
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor=ACCENT_COLOR, linewidth=1.5), zorder=5)
            ax.text(np.pi * 0.45, 0.85, 'MODERATE', ha='center', va='center',
                   fontsize=9, fontweight='bold', color="#f57c00",
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor="#f57c00", linewidth=1.5), zorder=5)
            ax.text(np.pi * 0.15, 0.85, 'LOW\nRISK', ha='center', va='center',
                   fontsize=9, fontweight='bold', color=SUCCESS_COLOR,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor=SUCCESS_COLOR, linewidth=1.5), zorder=5)
            
            # Add health index arrow
            index_angle = np.pi * (1 - health_index / 100)
            arrow_color = severity_color
            ax.arrow(index_angle, 0, 0, 0.75, head_width=0.12, head_length=0.08, 
                    fc=arrow_color, ec='black', linewidth=2.5, zorder=6)
            
            # Center text
            ax.set_ylim(0, 1.3)
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Main health index value
            ax.text(0, 0, f'{int(health_index)}', ha='center', va='center', 
                   fontsize=36, fontweight='bold', color=PRIMARY_COLOR, zorder=7)
            
            # Labels below the value
            ax.text(0, -0.25, 'Health Index', ha='center', va='center', 
                   fontsize=12, fontweight='bold', color=DARK_GRAY, zorder=7)
            ax.text(0, -0.4, f'Severity: {overall_severity}', ha='center', va='center',
                   fontsize=10, fontweight='bold', color=severity_color, zorder=7)
            
            # Add range indicator below gauge
            fig.text(0.5, 0.05, 'Scale: 0 (Critical) → 100 (Excellent)', 
                    ha='center', va='center', fontsize=9, style='italic', color=DARK_GRAY)
            
            ax.set_title('Overall Health Index Gauge', fontsize=14, fontweight='bold', pad=20)
            
            plt.tight_layout()
            chart_paths['health_index'] = os.path.join(output_dir, "health_index.png")
            plt.savefig(chart_paths['health_index'], dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
        except Exception as e:
            print(f"Error generating health index gauge: {e}")
    
    return chart_paths


def create_header_footer(canvas, doc):
    """Add header and footer to each page"""
    canvas.saveState()
    
    # Header
    canvas.setFont('Helvetica-Bold', 10)
    canvas.setFillColor(colors.HexColor(PRIMARY_COLOR))
    canvas.drawString(inch, A4[1] - 0.6*inch, "PraanLink Medical Report")
    
    # Header line
    canvas.setStrokeColor(colors.HexColor(PRIMARY_COLOR))
    canvas.setLineWidth(2)
    canvas.line(inch, A4[1] - 0.65*inch, A4[0] - inch, A4[1] - 0.65*inch)
    
    # Footer
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(colors.HexColor(DARK_GRAY))
    footer_text = f"Page {doc.page} | Generated on {datetime.now().strftime('%d-%m-%Y %H:%M')}"
    canvas.drawCentredString(A4[0]/2, 0.5*inch, footer_text)
    
    # Footer line
    canvas.setStrokeColor(colors.HexColor(MEDIUM_GRAY))
    canvas.setLineWidth(1)
    canvas.line(inch, 0.6*inch, A4[0] - inch, 0.6*inch)
    
    canvas.restoreState()


def create_info_box(story, title: str, content: str, bg_color: str = LIGHT_GRAY):
    """Create a styled information box"""
    title_style = ParagraphStyle(
        'boxTitle',
        parent=getSampleStyleSheet()['Normal'],
        leftIndent=12,
        rightIndent=12,
        spaceAfter=2,
        backColor=bg_color,
        borderPadding=6,
        borderColor=colors.HexColor(MEDIUM_GRAY),
        borderWidth=1,
        fontSize=10,
        leading=12
    )
    box_style = ParagraphStyle(
        'box',
        parent=getSampleStyleSheet()['Normal'],
        leftIndent=12,
        rightIndent=12,
        spaceAfter=4,
        backColor=bg_color,
        borderPadding=6,
        borderColor=colors.HexColor(MEDIUM_GRAY),
        borderWidth=1,
        fontSize=10,
        leading=12
    )
    if title:
        story.append(Paragraph(f"<b>{title}</b>", title_style))
    story.append(Paragraph(content, box_style))


def generate_medical_report_pdf(json_data: Dict[str, Any], output_pdf: str, charts_dir: str = "charts"):
    """Generate enhanced medical report PDF from JSON data"""
    
    # Extract patient name more robustly
    patient_overview = json_data.get('final_report', {}).get('patient_overview', '')
    if ',' in patient_overview:
        patient_name = patient_overview.split(",")[0]
    else:
        # Try to extract name from timeline events
        events = json_data.get('timeline', {}).get('events', [])
        if events and isinstance(events, list) and len(events) > 0:
            first_event = events[0]
            if isinstance(first_event, dict):
                description = first_event.get('description', '')
                if 'Patient' in description:
                    try:
                        patient_name = description.split('Patient')[1].split(',')[0].strip()
                    except:
                        patient_name = "Unknown Patient"
                else:
                    patient_name = "Unknown Patient"
            else:
                patient_name = "Unknown Patient"
        else:
            patient_name = "Unknown Patient"
    
    report_date = datetime.now().strftime("%d-%m-%Y")
    report_time = datetime.now().strftime("%H:%M")
    
    # PDF Setup with custom margins
    doc = SimpleDocTemplate(
        output_pdf, 
        pagesize=A4,
        rightMargin=1*inch,
        leftMargin=1*inch,
        topMargin=1.2*inch,
        bottomMargin=1*inch
    )
    
    # Custom styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        leading=32,
        alignment=1,  # Center
        spaceAfter=30,
        textColor=colors.HexColor(PRIMARY_COLOR),
        fontName='Helvetica-Bold'
    )
    
    # Section heading style
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=18,
        leading=22,
        spaceBefore=4,
        spaceAfter=4,
        textColor=colors.HexColor(PRIMARY_COLOR),
        fontName='Helvetica-Bold',
        borderPadding=4,
        backColor=colors.HexColor(LIGHT_GRAY),
        borderColor=colors.HexColor(PRIMARY_COLOR),
        borderWidth=2
    )
    
    # Subsection style
    subsection_style = ParagraphStyle(
        'Subsection',
        parent=styles['Heading3'],
        fontSize=14,
        leading=18,
        spaceBefore=4,
        spaceAfter=3,
        textColor=colors.HexColor(SECONDARY_COLOR),
        fontName='Helvetica-Bold'
    )
    
    # Body text style
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8,
        textColor=colors.HexColor(DARK_GRAY)
    )
    
    story = []
    
    # Title Page
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("PraanLink", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Medical Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Patient Info Box
    info_table_data = [
        [Paragraph("<b>Patient Name:</b>", body_style), Paragraph(str(patient_name), body_style)],
        [Paragraph("<b>Report Date:</b>", body_style), Paragraph(f"{report_date} at {report_time}", body_style)],
        [Paragraph("<b>Report Type:</b>", body_style), Paragraph("Comprehensive Health Analysis", body_style)]
    ]
    
    info_table = Table(info_table_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(LIGHT_GRAY)),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(MEDIUM_GRAY)),
    ]))
    story.append(info_table)
    
    story.append(PageBreak())
    
    # Medical Timeline Section
    story.append(Paragraph("Medical Timeline", section_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor(PRIMARY_COLOR), spaceAfter=4))
    
    timeline_events = json_data.get('timeline', {}).get('events', [])
    if isinstance(timeline_events, list) and len(timeline_events) > 0:
        for idx, event in enumerate(timeline_events, 1):
            if not isinstance(event, dict):
                continue
            event_date = event.get('date', 'N/A')
            event_type = event.get('event_type', '').replace('_', ' ').title()
            description = event.get('description', '')
            
            # Event box
            event_box_style = ParagraphStyle(
                'EventBox',
                parent=body_style,
                leftIndent=15,
                rightIndent=15,
                spaceBefore=3,
                spaceAfter=3,
                backColor=colors.white if idx % 2 == 0 else colors.HexColor('#f9f9f9'),
                borderPadding=6,
                borderColor=colors.HexColor(SECONDARY_COLOR),
                borderWidth=1
            )
            
            story.append(Paragraph(
                f"<b><font color='{PRIMARY_COLOR}'>Event #{idx}</font></b> | "
                f"<b>Date:</b> {event_date} | <b>Type:</b> {event_type}",
                subsection_style
            ))
            story.append(Paragraph(str(description), event_box_style))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("No timeline events available.", body_style))
    
    story.append(PageBreak())
    
    # Clinical Trends Section
    story.append(Paragraph("Clinical Trends Analysis", section_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor(PRIMARY_COLOR), spaceAfter=4))
    
    clinical_trends = json_data.get('clinical_trends', {}).get('trends', [])
    
    if isinstance(clinical_trends, list) and len(clinical_trends) > 0:
        # Enhanced Clinical Trends Table
        table_data = [["Metric", "Previous", "Current", "Trend", "Status", "Comment"]]
        for trend in clinical_trends:
            if not isinstance(trend, dict):
                continue
            status = trend.get('status', 'N/A')
            status_color = get_status_color(status)
            
            metric = trend.get('metric', 'N/A')
            previous = str(trend.get('previous_value', '-')) if trend.get('previous_value') else "-"
            current = str(trend.get('current_value', 'N/A'))
            trend_val = trend.get('trend', 'N/A')
            if isinstance(trend_val, str):
                trend_val = trend_val.title()
            comment = trend.get('clinical_comment', '')
            if isinstance(comment, str) and len(comment) > 80:
                comment = comment[:80] + "..."
            
            table_data.append([
                Paragraph(str(metric), body_style),
                Paragraph(str(previous), body_style),
                Paragraph(f"<b>{str(current)}</b>", body_style),
                Paragraph(str(trend_val), body_style),
                Paragraph(f"<font color='{status_color}'><b>{str(status).upper()}</b></font>", body_style),
                Paragraph(str(comment), ParagraphStyle('Small', parent=body_style, fontSize=8))
            ])
        
        # Calculate column widths dynamically
        col_widths = [1.3*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.9*inch, 2.5*inch]
        t = Table(table_data, repeatRows=1, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(PRIMARY_COLOR)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(MEDIUM_GRAY)),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))
        
        # Clinical Trends Summary
        clinical_trends_section = json_data.get('clinical_trends', {})
        if clinical_trends_section and clinical_trends_section.get('overall_summary'):
            create_info_box(
                story,
                "Clinical Trends Summary",
                str(clinical_trends_section['overall_summary']),
                LIGHT_GRAY
            )
        
        story.append(Spacer(1, 6))
        
        # Clinical Trends Charts
        risk_data = json_data.get('risk_and_severity', {})
        chart_paths = generate_charts(clinical_trends, risk_data, output_dir=charts_dir)
        
        if 'clinical_trends' in chart_paths:
            story.append(Paragraph("Clinical Trends Visualization", subsection_style))
            if os.path.exists(chart_paths['clinical_trends']):
                story.append(Image(chart_paths['clinical_trends'], width=6*inch, height=3.5*inch))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("No clinical trends data available.", body_style))
    
    story.append(PageBreak())
    
    # Risk & Severity Section
    story.append(Paragraph("Risk & Severity Assessment", section_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor(ACCENT_COLOR), spaceAfter=4))
    
    risk_data = json_data.get('risk_and_severity', {})
    
    # Overall Health Metrics Box
    health_index = risk_data.get('overall_health_index', 'N/A')
    overall_severity = risk_data.get('overall_severity', 'N/A')
    severity_color = get_severity_color(overall_severity)
    
    metrics_data = [
        [
            Paragraph("<b>Overall Health Index</b>", body_style),
            Paragraph(f"<font size='16' color='{PRIMARY_COLOR}'><b>{health_index}</b></font>", body_style)
        ],
        [
            Paragraph("<b>Overall Severity Level</b>", body_style),
            Paragraph(f"<font size='14' color='{severity_color}'><b>{str(overall_severity).upper()}</b></font>", body_style)
        ]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
    metrics_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(LIGHT_GRAY)),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(MEDIUM_GRAY)),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 6))
    
    # Clinical Comment
    if risk_data.get('clinical_comment'):
        create_info_box(
            story,
            "Clinical Assessment",
            str(risk_data['clinical_comment']),
            '#fff3e0' if 'Moderate' in str(overall_severity) else LIGHT_GRAY
        )
        story.append(Spacer(1, 6))
    
    # Disease Risks Table
    disease_risks = risk_data.get('disease_risks', [])
    if disease_risks and isinstance(disease_risks, list) and len(disease_risks) > 0:
        story.append(Paragraph("Disease Risk Breakdown", subsection_style))
        
        risk_table_data = [["Disease", "Risk Score", "Severity Level"]]
        for risk in disease_risks:
            if not isinstance(risk, dict):
                continue
            disease = risk.get('disease', 'N/A')
            risk_score = risk.get('risk_score', 'N/A')
            severity = risk.get('severity_level', 'N/A')
            severity_color_cell = get_severity_color(severity)
            
            risk_table_data.append([
                Paragraph(str(disease), body_style),
                Paragraph(f"<b>{risk_score}</b>", body_style),
                Paragraph(f"<font color='{severity_color_cell}'><b>{severity}</b></font>", body_style)
            ])
        
        t2 = Table(risk_table_data, repeatRows=1, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(ACCENT_COLOR)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(MEDIUM_GRAY)),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t2)
        story.append(Spacer(1, 6))
        
        # Risk Score Chart
        chart_paths = generate_charts(clinical_trends, risk_data, output_dir=charts_dir)
        if 'risk_scores' in chart_paths:
            story.append(Paragraph("Risk Score Visualization", subsection_style))
            if os.path.exists(chart_paths['risk_scores']):
                story.append(Image(chart_paths['risk_scores'], width=5.5*inch, height=3.2*inch))
            story.append(Spacer(1, 4))
        
        # Health Index Gauge
        if 'health_index' in chart_paths:
            story.append(Paragraph("Overall Health Index", subsection_style))
            if os.path.exists(chart_paths['health_index']):
                story.append(Image(chart_paths['health_index'], width=4*inch, height=3*inch))
    
    story.append(PageBreak())
    
    # Possible Conditions Section
    story.append(Paragraph("Possible Conditions", section_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor(INFO_COLOR), spaceAfter=4))
    
    conditions = json_data.get('possible_conditions', {}).get('conditions', [])
    if isinstance(conditions, list) and len(conditions) > 0:
        for idx, condition in enumerate(conditions, 1):
            if not isinstance(condition, dict):
                continue
            condition_name = condition.get('condition', 'N/A')
            confidence = condition.get('confidence', 'N/A')
            recommended_action = condition.get('recommended_action', 'N/A')
            
            # Color code by confidence
            try:
                confidence_val = float(confidence) if confidence != 'N/A' else 0
            except (ValueError, TypeError):
                confidence_val = 0
            
            if confidence_val >= 85:
                confidence_color = ACCENT_COLOR
            elif confidence_val >= 70:
                confidence_color = "#f57c00"
            else:
                confidence_color = INFO_COLOR
            
            condition_box_style = ParagraphStyle(
                'ConditionBox',
                parent=body_style,
                leftIndent=10,
                rightIndent=10,
                spaceBefore=3,
                spaceAfter=3,
                backColor=colors.HexColor('#f5f5f5'),
                borderPadding=6,
                borderColor=colors.HexColor(confidence_color),
                borderWidth=2
            )
            
            story.append(Paragraph(
                f"<b><font color='{PRIMARY_COLOR}'>Condition #{idx}:</font></b> {condition_name} "
                f"<font color='{confidence_color}'>(Confidence: {confidence}%)</font>",
                subsection_style
            ))
            story.append(Paragraph(
                f"<b>Recommended Action:</b> {recommended_action}",
                condition_box_style
            ))
            story.append(Spacer(1, 4))
        
        # Summary comment
        possible_conditions_section = json_data.get('possible_conditions', {})
        if possible_conditions_section and possible_conditions_section.get('summary_comment'):
            story.append(Spacer(1, 4))
            create_info_box(
                story,
                "Conditions Summary",
                str(possible_conditions_section['summary_comment']),
                '#e3f2fd'
            )
    else:
        story.append(Paragraph("No conditions data available.", body_style))
    
    story.append(PageBreak())
    
    # Medication Overview Section
    story.append(Paragraph("Medication Overview", section_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor(SECONDARY_COLOR), spaceAfter=4))
    
    medication_data = json_data.get('medication_overview', {})
    
    # Current Medications
    current_meds = medication_data.get('current_medications', [])
    if current_meds and isinstance(current_meds, list) and len(current_meds) > 0:
        story.append(Paragraph("Current Medications", subsection_style))
        for med in current_meds:
            if not isinstance(med, dict):
                continue
            med_info = f"{med.get('name', 'N/A')} - {med.get('dosage', 'N/A')} ({med.get('frequency', 'N/A')})"
            if med.get('special_instructions'):
                med_info += f" | Instructions: {med.get('special_instructions')}"
            story.append(Paragraph(f"• {med_info}", body_style))
        story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("<b>Current Medications:</b> None", body_style))
        story.append(Spacer(1, 6))
    
    # Past Medications
    past_meds = medication_data.get('past_medications', [])
    if past_meds and isinstance(past_meds, list) and len(past_meds) > 0:
        story.append(Paragraph("Past Medications", subsection_style))
        med_table_data = [["Medication", "Dosage", "Frequency", "Period", "Instructions"]]
        for med in past_meds:
            if not isinstance(med, dict):
                continue
            period = f"{med.get('start_date', '')} to {med.get('end_date', '')}"
            med_table_data.append([
                med.get('name', 'N/A'),
                med.get('dosage', 'N/A'),
                med.get('frequency', 'N/A'),
                period,
                med.get('special_instructions', 'N/A')
            ])
        
        med_table = Table(med_table_data, repeatRows=1, colWidths=[1.5*inch, 1*inch, 1*inch, 1.5*inch, 1.5*inch])
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(SECONDARY_COLOR)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(MEDIUM_GRAY)),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(med_table)
    
    # Medication Summary
    if medication_data.get('medication_summary'):
        story.append(Spacer(1, 4))
        create_info_box(
            story,
            "Medication Summary",
            str(medication_data['medication_summary']),
            LIGHT_GRAY
        )
    
    story.append(PageBreak())
    
    # Final Report Summary
    story.append(Paragraph("Final Report Summary", section_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor(PRIMARY_COLOR), spaceAfter=4))
    
    final_report = json_data.get('final_report', {})
    
    # Patient Overview
    if final_report.get('patient_overview'):
        story.append(Paragraph("Patient Overview", subsection_style))
        create_info_box(
            story,
            "",
            str(final_report['patient_overview']),
            LIGHT_GRAY
        )
        story.append(Spacer(1, 4))
    
    # Risk Level
    risk_level = final_report.get('risk_level', 'N/A')
    risk_level_color = get_severity_color(risk_level)
    risk_box_data = [
        [Paragraph("<b>Overall Risk Level:</b>", body_style),
         Paragraph(f"<font size='16' color='{risk_level_color}'><b>{str(risk_level).upper()}</b></font>", body_style)]
    ]
    risk_box = Table(risk_box_data, colWidths=[3*inch, 3*inch])
    risk_box.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff3e0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(risk_level_color)),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(risk_box)
    story.append(Spacer(1, 6))
    
    # Next Steps
    next_steps = final_report.get('next_steps', [])
    if next_steps and isinstance(next_steps, list) and len(next_steps) > 0:
        story.append(Paragraph("Next Steps & Recommendations", subsection_style))
        steps_box_style = ParagraphStyle(
            'StepsBox',
            parent=body_style,
            leftIndent=20,
            spaceBefore=2,
            spaceAfter=2,
            bulletIndent=10
        )
        for step in next_steps:
            story.append(Paragraph(f"✓ {step}", steps_box_style))
    
    # Summary Comment
    if final_report.get('summary_comment'):
        story.append(Spacer(1, 6))
        create_info_box(
            story,
            "Detailed Clinical Summary",
            str(final_report['summary_comment']),
            '#f3e5f5'
        )
    
    # Build PDF with header/footer
    def on_first_page(canvas, doc):
        create_header_footer(canvas, doc)
    
    def on_later_pages(canvas, doc):
        create_header_footer(canvas, doc)
    
    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    
    print(f"✓ PDF report generated successfully: {output_pdf}")
    print(f"✓ Charts saved in: {charts_dir}/ directory")

