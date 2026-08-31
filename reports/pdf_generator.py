"""
PDF Report Generation Module

Generates professional health reports as PDF files using ReportLab.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from config import (
    APP_NAME,
    APP_VERSION,
    PDF_TITLE,
    PDF_AUTHOR,
    REPORTS_DIR,
)

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generate professional health reports in PDF format."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or REPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Styles
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#0078D7'),
            spaceAfter=12,
            alignment=TA_CENTER,
        ))
        
        # Section style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0078D7'),
            spaceAfter=8,
            spaceBefore=8,
        ))
        
        # Normal text
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
        ))
    
    def generate_report(self, patient_data: Dict[str, Any], 
                       test_results: Dict[str, Any],
                       ecg_summary: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Generate a comprehensive health report PDF.
        
        Args:
            patient_data: Dictionary with patient information
            test_results: Dictionary with test results
            ecg_summary: Optional ECG analysis results
            
        Returns:
            Path to generated PDF file, or None if failed
        """
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            patient_name = patient_data.get('name', 'Unknown').replace(' ', '_')
            filename = f"report_{patient_name}_{timestamp}.pdf"
            filepath = self.output_dir / filename
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch,
                title=PDF_TITLE,
                author=PDF_AUTHOR,
            )
            
            # Build story (content)
            story = []
            
            # Header
            story.extend(self._build_header())
            story.append(Spacer(1, 0.3*inch))
            
            # Patient Information
            story.extend(self._build_patient_info(patient_data))
            story.append(Spacer(1, 0.2*inch))
            
            # Test Results
            story.extend(self._build_test_results(test_results))
            story.append(Spacer(1, 0.2*inch))
            
            # ECG Results (if available)
            if ecg_summary:
                story.extend(self._build_ecg_section(ecg_summary))
                story.append(Spacer(1, 0.2*inch))
            
            # Observations and Recommendations
            story.extend(self._build_observations(test_results))
            story.append(Spacer(1, 0.2*inch))
            
            # Footer
            story.extend(self._build_footer())
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"Report generated: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return None
    
    def _build_header(self):
        """Build report header."""
        elements = []
        
        title = Paragraph(APP_NAME, self.styles['CustomTitle'])
        elements.append(title)
        
        subtitle = Paragraph(
            f"Smart Health Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Normal']
        )
        elements.append(subtitle)
        
        return elements
    
    def _build_patient_info(self, patient_data: Dict[str, Any]):
        """Build patient information section."""
        elements = []
        
        elements.append(Paragraph("Patient Information", self.styles['SectionHeading']))
        
        data = [
            ["Name:", patient_data.get('name', 'N/A')],
            ["Age:", str(patient_data.get('age', 'N/A')) + " years"],
            ["Gender:", patient_data.get('gender', 'N/A')],
            ["Mobile:", patient_data.get('mobile', 'N/A')],
            ["Address:", patient_data.get('address', 'N/A')],
        ]
        
        if patient_data.get('doctor_name'):
            data.append(["Attending Doctor:", patient_data.get('doctor_name')])
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(table)
        return elements
    
    def _build_test_results(self, test_results: Dict[str, Any]):
        """Build test results section."""
        elements = []
        
        elements.append(Paragraph("Test Results", self.styles['SectionHeading']))
        
        data = [
            ["Measurement", "Value", "Status"],
        ]
        
        # Pulse
        pulse = test_results.get('pulse', 'N/A')
        pulse_status = self._get_status(test_results.get('pulse_status', 'Normal'))
        data.append([
            "Pulse (BPM)",
            str(pulse) if pulse != 'N/A' else pulse,
            pulse_status
        ])
        
        # Temperature
        temp = test_results.get('temperature', 'N/A')
        temp_status = self._get_status(test_results.get('temperature_status', 'Normal'))
        data.append([
            "Temperature (°C)",
            f"{temp:.1f}" if isinstance(temp, (int, float)) else temp,
            temp_status
        ])
        
        # Blood Pressure
        bp = test_results.get('blood_pressure', 'Not Available')
        data.append([
            "Blood Pressure",
            bp,
            "N/A"
        ])
        
        table = Table(data, colWidths=[2*inch, 2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0078D7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(table)
        return elements
    
    def _build_ecg_section(self, ecg_summary: Dict[str, Any]):
        """Build ECG results section."""
        elements = []
        
        elements.append(Paragraph("ECG Analysis", self.styles['SectionHeading']))
        
        data = [
            ["Parameter", "Value"],
            ["Total Samples", str(ecg_summary.get('total_samples', 0))],
            ["Duration", f"{ecg_summary.get('duration_seconds', 0):.1f} seconds"],
            ["Lead-off Detected", "Yes" if ecg_summary.get('lead_off_detected') else "No"],
        ]
        
        if ecg_summary.get('issues'):
            data.append(["Issues", ", ".join(ecg_summary.get('issues', []))])
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0078D7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(table)
        
        # Disclaimer
        disclaimer = Paragraph(
            "<b>Note:</b> This report is for informational purposes only. "
            "For professional medical interpretation, please consult a qualified healthcare provider.",
            self.styles['CustomNormal']
        )
        elements.append(Spacer(1, 0.1*inch))
        elements.append(disclaimer)
        
        return elements
    
    def _build_observations(self, test_results: Dict[str, Any]):
        """Build observations and recommendations section."""
        elements = []
        
        elements.append(Paragraph("Observations & Recommendations", self.styles['SectionHeading']))
        
        observations = []
        
        # Check for abnormalities
        if test_results.get('pulse_status') == 'CRITICAL':
            observations.append("⚠️ Heart rate is outside normal range. Seek medical attention if symptoms persist.")
        
        if test_results.get('temperature_status') == 'CRITICAL':
            observations.append("⚠️ Body temperature is elevated. Consult a healthcare provider if fever persists.")
        
        if test_results.get('emergency'):
            observations.append("🚨 EMERGENCY CONDITION DETECTED: Seek immediate medical attention or call emergency services.")
        
        if not observations:
            observations.append("All measurements appear within normal ranges. Continue regular health monitoring.")
        
        for obs in observations:
            para = Paragraph(obs, self.styles['CustomNormal'])
            elements.append(para)
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _build_footer(self):
        """Build report footer."""
        elements = []
        
        footer_text = (
            f"<b>{APP_NAME}</b> v{APP_VERSION}<br/>"
            "For medical emergencies, contact emergency services immediately.<br/>"
            f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        footer = Paragraph(footer_text, self.styles['Normal'])
        elements.append(footer)
        
        return elements
    
    def _get_status(self, status: str) -> str:
        """Convert status to display format with emoji indicators."""
        status_map = {
            'Normal': '✓ Normal',
            'Warning': '⚠️ Warning',
            'Critical': '🔴 Critical',
            'UNAVAILABLE': 'N/A',
        }
        return status_map.get(status, status)


def generate_health_report(patient_data: Dict[str, Any],
                          test_results: Dict[str, Any],
                          ecg_summary: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Convenience function to generate a health report PDF.
    
    Args:
        patient_data: Dictionary with patient information
        test_results: Dictionary with test results
        ecg_summary: Optional ECG analysis results
        
    Returns:
        Path to generated PDF file, or None if failed
    """
    generator = PDFReportGenerator()
    return generator.generate_report(patient_data, test_results, ecg_summary)
