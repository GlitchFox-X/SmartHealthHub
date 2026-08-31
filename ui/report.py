"""
Report Summary Screen

Shows complete health report and provides options to save PDF and send SMS.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_PRIMARY, COLOR_SUCCESS, BUTTON_HEIGHT


class ReportScreen(QWidget):
    """Display complete health report."""
    
    generate_pdf_clicked = pyqtSignal()
    send_sms_clicked = pyqtSignal()
    finish_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.patient_data = {}
        self.test_results = {}
        self.initUI()
    
    def initUI(self):
        """Initialize the UI."""
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Health Report Summary")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Scrollable report area
        scroll = QScrollArea()
        scroll.setStyleSheet("QScrollArea { border: 1px solid #ddd; }")
        scroll.setWidgetResizable(True)
        
        report_widget = QWidget()
        report_layout = QVBoxLayout()
        report_layout.setSpacing(10)
        
        # Patient info section
        patient_title = QLabel("Patient Information")
        patient_title.setFont(QFont("Arial", 12, QFont.Bold))
        report_layout.addWidget(patient_title)
        
        self.patient_display = QLabel()
        self.patient_display.setFont(QFont("Arial", 10))
        self.patient_display.setStyleSheet("color: #333333; margin-left: 10px;")
        report_layout.addWidget(self.patient_display)
        
        # Test results section
        results_title = QLabel("Test Results")
        results_title.setFont(QFont("Arial", 12, QFont.Bold))
        results_title.setStyleSheet("margin-top: 10px;")
        report_layout.addWidget(results_title)
        
        self.results_display = QLabel()
        self.results_display.setFont(QFont("Arial", 10))
        self.results_display.setStyleSheet("color: #333333; margin-left: 10px;")
        report_layout.addWidget(self.results_display)
        
        # ECG section (if performed)
        self.ecg_title = QLabel("ECG Analysis")
        self.ecg_title.setFont(QFont("Arial", 12, QFont.Bold))
        self.ecg_title.setStyleSheet("margin-top: 10px;")
        report_layout.addWidget(self.ecg_title)
        
        self.ecg_display = QLabel()
        self.ecg_display.setFont(QFont("Arial", 10))
        self.ecg_display.setStyleSheet("color: #333333; margin-left: 10px;")
        report_layout.addWidget(self.ecg_display)
        
        # Observations section
        obs_title = QLabel("Observations")
        obs_title.setFont(QFont("Arial", 12, QFont.Bold))
        obs_title.setStyleSheet("margin-top: 10px;")
        report_layout.addWidget(obs_title)
        
        self.observations_display = QLabel()
        self.observations_display.setFont(QFont("Arial", 10))
        self.observations_display.setStyleSheet("color: #333333; margin-left: 10px;")
        report_layout.addWidget(self.observations_display)
        
        report_layout.addStretch()
        report_widget.setLayout(report_layout)
        scroll.setWidget(report_widget)
        layout.addWidget(scroll)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # PDF Button
        pdf_btn = QPushButton("📄 Save as PDF")
        pdf_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #{COLOR_PRIMARY[0]:02x}{COLOR_PRIMARY[1]:02x}{COLOR_PRIMARY[2]:02x};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #005a9e;
            }}
        """)
        pdf_btn.setMinimumHeight(BUTTON_HEIGHT - 25)
        pdf_btn.clicked.connect(self.generate_pdf_clicked.emit)
        button_layout.addWidget(pdf_btn)
        
        # SMS Button
        sms_btn = QPushButton("📱 Send SMS")
        sms_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #{COLOR_SUCCESS[0]:02x}{COLOR_SUCCESS[1]:02x}{COLOR_SUCCESS[2]:02x};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #33aa33;
            }}
        """)
        sms_btn.setMinimumHeight(BUTTON_HEIGHT - 25)
        sms_btn.clicked.connect(self.send_sms_clicked.emit)
        button_layout.addWidget(sms_btn)
        
        # Finish Button
        finish_btn = QPushButton("✓ Finish")
        finish_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #999999;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #666666;
            }}
        """)
        finish_btn.setMinimumHeight(BUTTON_HEIGHT - 25)
        finish_btn.clicked.connect(self.finish_clicked.emit)
        button_layout.addWidget(finish_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def set_data(self, patient_data: dict, test_results: dict, ecg_results: dict = None):
        """Set and display report data."""
        self.patient_data = patient_data
        self.test_results = test_results
        
        # Format patient info
        patient_text = f"""
Name: {patient_data.get('name')}
Age: {patient_data.get('age')} years
Gender: {patient_data.get('gender')}
Mobile: {patient_data.get('mobile')}
Address: {patient_data.get('address')}
        """.strip()
        self.patient_display.setText(patient_text)
        
        # Format test results
        results_text = f"""
Pulse: {test_results.get('pulse', 'N/A')} BPM
Temperature: {test_results.get('temperature', 'N/A')}°C
Blood Pressure: {test_results.get('blood_pressure', 'Not Available')}
Timestamp: {test_results.get('timestamp', 'N/A')}
        """.strip()
        self.results_display.setText(results_text)
        
        # Format ECG results if available
        if ecg_results:
            ecg_text = f"""
Status: Performed
Samples: {ecg_results.get('total_samples', 0)}
Duration: {ecg_results.get('duration_seconds', 0):.1f} seconds
Lead-off: {'Yes' if ecg_results.get('lead_off_detected') else 'No'}
            """.strip()
        else:
            self.ecg_title.hide()
            self.ecg_display.hide()
            ecg_text = "Not performed"
        
        self.ecg_display.setText(ecg_text)
        
        # Format observations
        obs_list = []
        if test_results.get('pulse_status') == 'CRITICAL':
            obs_list.append("⚠️ Heart rate is outside normal range")
        if test_results.get('temperature_status') == 'CRITICAL':
            obs_list.append("⚠️ Body temperature is abnormal")
        if test_results.get('emergency'):
            obs_list.append("🚨 EMERGENCY CONDITION DETECTED")
        
        if not obs_list:
            obs_list.append("✓ All measurements appear normal")
        
        obs_text = "\n".join(obs_list)
        self.observations_display.setText(obs_text)
