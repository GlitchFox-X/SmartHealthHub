"""
Smart Health Hub - Main Application

PyQt5 application for Raspberry Pi OS with 7-inch touchscreen.
Manages patient health monitoring workflow.
"""

import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

# Import all screens
from ui.home import HomeScreen
from ui.patient import PatientDetailsScreen
from ui.basic_test import BasicTestScreen
from ui.results import ResultsScreen
from ui.ecg_decision import ECGDecisionScreen
from ui.ecg_instruction import ECGInstructionScreen
from ui.ecg_test import ECGTestScreen
from ui.report import ReportScreen

# Import backend modules
from arduino.serial_manager import get_serial_manager
from sensors.pulse import PulseProcessor
from sensors.temperature import TemperatureProcessor
from sensors.ecg import ECGProcessor
from database.database import get_database
from communication.sim800l import get_sms_manager
from reports.pdf_generator import generate_health_report

from config import (
    APP_NAME, APP_VERSION, SCREEN_WIDTH, SCREEN_HEIGHT,
    OFFLINE_MODE, ENABLE_ECG, ENABLE_SMS, ENABLE_PDF,
    LOG_FILE, LOG_LEVEL, LOGS_DIR
)


# Configure logging
LOGS_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataProcessorThread(QThread):
    """Background thread for processing sensor data."""
    
    status_updated = pyqtSignal(str)
    basic_result_received = pyqtSignal(dict)
    ecg_sample_received = pyqtSignal(int, int)  # timestamp, value
    
    def __init__(self):
        super().__init__()
        self.serial_mgr = get_serial_manager()
        self.pulse_proc = PulseProcessor()
        self.temp_proc = TemperatureProcessor()
        self.ecg_proc = ECGProcessor()
        
        # Connect serial manager callbacks
        self.serial_mgr.on_status = self._on_status
        self.serial_mgr.on_basic_result = self._on_basic_result
        self.serial_mgr.on_ecg_sample = self._on_ecg_sample
    
    def run(self):
        """Start background processing."""
        # This thread just processes callbacks from serial manager
        pass
    
    def _on_status(self, status: str):
        """Handle status update from Arduino."""
        logger.debug(f"Status: {status}")
        self.status_updated.emit(status)
    
    def _on_basic_result(self, data: dict):
        """Handle basic test results."""
        logger.info(f"Basic test results: {data}")
        self.basic_result_received.emit(data)
    
    def _on_ecg_sample(self, data: dict):
        """Handle ECG sample."""
        timestamp = data.get('timestamp', 0)
        value = data.get('value', 0)
        self.ecg_proc.add_sample(timestamp, value)
        self.ecg_sample_received.emit(timestamp, value)


class SmartHealthHubApp(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Remove window decorations for fullscreen
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Initialize backend
        self.serial_mgr = get_serial_manager()
        self.db = get_database()
        self.sms_mgr = get_sms_manager()
        
        # Initialize data processors
        self.processor_thread = DataProcessorThread()
        self.pulse_proc = self.processor_thread.pulse_proc
        self.temp_proc = self.processor_thread.temp_proc
        self.ecg_proc = self.processor_thread.ecg_proc
        
        # Current session data
        self.current_patient_id = None
        self.current_test_id = None
        self.patient_data = {}
        self.test_results = {}
        self.ecg_results = None
        
        # Initialize UI
        self.init_ui()
        
        # Start data processor thread
        self.processor_thread.start()
        
        # Connect serial manager
        if not OFFLINE_MODE:
            self.serial_mgr.connect()
        
        logger.info(f"Application started: {APP_NAME} v{APP_VERSION}")
    
    def init_ui(self):
        """Initialize UI screens."""
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create all screens
        self.home_screen = HomeScreen()
        self.patient_screen = PatientDetailsScreen()
        self.basic_test_screen = BasicTestScreen()
        self.results_screen = ResultsScreen()
        self.ecg_decision_screen = ECGDecisionScreen()
        self.ecg_instruction_screen = ECGInstructionScreen()
        self.ecg_test_screen = ECGTestScreen()
        self.report_screen = ReportScreen()
        
        # Add screens to stack
        self.stacked_widget.addWidget(self.home_screen)           # 0
        self.stacked_widget.addWidget(self.patient_screen)        # 1
        self.stacked_widget.addWidget(self.basic_test_screen)     # 2
        self.stacked_widget.addWidget(self.results_screen)        # 3
        self.stacked_widget.addWidget(self.ecg_decision_screen)   # 4
        self.stacked_widget.addWidget(self.ecg_instruction_screen)  # 5
        self.stacked_widget.addWidget(self.ecg_test_screen)       # 6
        self.stacked_widget.addWidget(self.report_screen)         # 7
        
        # Connect screen signals
        self.connect_signals()
        
        # Show home screen
        self.stacked_widget.setCurrentWidget(self.home_screen)
    
    def connect_signals(self):
        """Connect all screen signals."""
        # Home screen
        self.home_screen.start_clicked.connect(self.show_patient_screen)
        
        # Patient screen
        self.patient_screen.next_clicked.connect(self.on_patient_data_entered)
        self.patient_screen.back_clicked.connect(self.show_home_screen)
        
        # Basic test screen
        self.basic_test_screen.test_started.connect(self.on_test_started)
        self.basic_test_screen.test_cancelled.connect(self.show_home_screen)
        self.processor_thread.status_updated.connect(self._handle_status_message)
        self.processor_thread.basic_result_received.connect(self.on_basic_result_received)
        
        # Results screen
        self.results_screen.next_clicked.connect(self.show_ecg_decision_screen)
        self.results_screen.back_clicked.connect(self.show_basic_test_screen)
        
        # ECG Decision screen
        self.ecg_decision_screen.ecg_yes_clicked.connect(self.show_ecg_instruction_screen)
        self.ecg_decision_screen.ecg_no_clicked.connect(self.show_report_screen)
        
        # ECG Instruction screen
        self.ecg_instruction_screen.ready_clicked.connect(self.show_ecg_test_screen)
        self.ecg_instruction_screen.back_clicked.connect(self.show_ecg_decision_screen)
        
        # ECG Test screen
        self.ecg_test_screen.stop_clicked.connect(self.on_ecg_complete)
        self.processor_thread.ecg_sample_received.connect(
            lambda ts, val: self.ecg_test_screen.add_ecg_sample(ts, val)
        )
        
        # Report screen
        self.report_screen.generate_pdf_clicked.connect(self.on_generate_pdf)
        self.report_screen.send_sms_clicked.connect(self.on_send_sms)
        self.report_screen.finish_clicked.connect(self.on_finish)
    
    # Screen navigation methods
    def show_home_screen(self):
        self.stacked_widget.setCurrentWidget(self.home_screen)
    
    def show_patient_screen(self):
        self.patient_screen.clear_form()
        self.stacked_widget.setCurrentWidget(self.patient_screen)
    
    def show_basic_test_screen(self):
        self.stacked_widget.setCurrentWidget(self.basic_test_screen)
    
    def show_results_screen(self):
        self.stacked_widget.setCurrentWidget(self.results_screen)
    
    def show_ecg_decision_screen(self):
        self.stacked_widget.setCurrentWidget(self.ecg_decision_screen)
    
    def show_ecg_instruction_screen(self):
        self.stacked_widget.setCurrentWidget(self.ecg_instruction_screen)
    
    def show_ecg_test_screen(self):
        self.ecg_proc.clear()
        self.ecg_test_screen.start_recording()
        self.stacked_widget.setCurrentWidget(self.ecg_test_screen)
        
        # Start ECG on Arduino
        self.serial_mgr.start_ecg()
    
    def show_report_screen(self):
        self.stacked_widget.setCurrentWidget(self.report_screen)
    
    # Event handlers
    def _handle_status_message(self, status: str):
        """Handle status messages from Arduino.
        
        Routes status messages to appropriate UI screens and handlers.
        """
        logger.debug(f"Status message: {status}")
        
        # Route to basic test screen if we're in that screen
        if status in ["TOUCH_WAIT", "TOUCH_CONFIRMED", "TOUCH_LOST", 
                      "TEST_STARTING", "TEST_ONGOING", "TEST_COMPLETE"]:
            self.basic_test_screen.set_status(status)
        
        # Handle ECG lead-off detection
        elif status == "ECG_LEAD_OFF":
            logger.warning("ECG lead-off detected")
            self.ecg_test_screen.set_lead_off(True)
            # Show warning
            QMessageBox.warning(
                self, 
                "Lead-off Detected", 
                "Electrode connection lost.\n\nPlease check and reposition the electrodes."
            )
        
        # Handle ECG completion
        elif status == "ECG_COMPLETE":
            logger.info("ECG recording complete")
    
    def on_patient_data_entered(self, patient_data: dict):
        """Handle patient data entry."""
        self.patient_data = patient_data
        
        # Try to find existing patient by phone
        existing = self.db.get_patient_by_mobile(patient_data['mobile'])
        if existing:
            self.current_patient_id = existing['id']
            logger.info(f"Found existing patient: {existing['name']}")
        else:
            # Create new patient
            self.current_patient_id = self.db.add_patient(
                name=patient_data['name'],
                age=patient_data['age'],
                gender=patient_data['gender'],
                mobile=patient_data['mobile'],
                address=patient_data['address'],
                doctor_name=patient_data.get('doctor_name'),
                doctor_phone=patient_data.get('doctor_phone'),
            )
            logger.info(f"Created new patient: {patient_data['name']}")
        
        # Create test record
        self.current_test_id = self.db.add_test(self.current_patient_id, "BASIC_ECG")
        
        # Move to basic test screen
        self.show_basic_test_screen()
        self.processor_thread.status_updated.emit("TOUCH_WAIT")
    
    def on_test_started(self):
        """Handle test start."""
        self.serial_mgr.start_test()
    
    def on_basic_result_received(self, result_data: dict):
        """Handle basic test results from Arduino.
        
        Arduino sends already-processed values:
        - pulse: Already converted to BPM (40-200 range)
        - temperature: Already converted to Celsius
        - bp: Always "Not Available" (HX710B hardware to be integrated)
        
        Do NOT re-process these values - use directly from Arduino.
        """
        # Get values directly from Arduino (already processed)
        pulse = result_data.get('pulse', 0)
        temperature = result_data.get('temperature', 0.0)
        bp = result_data.get('bp', 'Not Available')
        
        # Ensure proper types
        pulse = int(pulse) if pulse else 0
        temperature = float(temperature) if temperature else 0.0
        
        # Store results with evaluation
        self.test_results = {
            'pulse': pulse,  # BPM, from Arduino
            'temperature': temperature,  # Celsius, from Arduino
            'blood_pressure': bp,  # Not Available until HX710B is integrated
            'timestamp': datetime.now().isoformat(),
            'pulse_status': self._evaluate_pulse(pulse),
            'temperature_status': self._evaluate_temperature(temperature),
        }
        
        # Save to database (store actual Arduino readings)
        if self.current_test_id:
            self.db.add_basic_result(
                self.current_test_id,
                pulse,
                temperature,
                bp
            )
        
        logger.info(f"Test results stored: Pulse={pulse} BPM, Temp={temperature}°C, BP={bp}")
        
        # Display results on screen
        self.results_screen.set_results(pulse, temperature, bp)
        self.show_results_screen()
    
    def on_ecg_complete(self):
        """Handle ECG completion."""
        # Stop recording
        self.ecg_test_screen.stop_recording()
        self.serial_mgr.stop_ecg()
        
        # Get statistics
        stats = self.ecg_proc.get_statistics()
        abnormalities = self.ecg_proc.detect_abnormalities()
        
        self.ecg_results = {
            **stats,
            **abnormalities,
        }
        
        # Save to database if we have a test
        if self.current_test_id:
            raw_data = str(self.ecg_proc.export_raw_data())
            self.db.add_ecg_data(
                self.current_test_id,
                stats.get('total_samples', 0),
                stats.get('duration_seconds', 0),
                stats.get('lead_off', False),
                raw_data
            )
        
        logger.info(f"ECG recording complete: {len(self.ecg_proc.get_all_samples())} samples")
        self.show_report_screen()
    
    def on_generate_pdf(self):
        """Generate PDF report."""
        if not ENABLE_PDF:
            QMessageBox.warning(self, "PDF", "PDF generation is disabled")
            return
        
        try:
            pdf_path = generate_health_report(
                self.patient_data,
                self.test_results,
                self.ecg_results
            )
            
            if pdf_path:
                # Save to database
                if self.current_test_id:
                    self.db.add_report(self.current_test_id, pdf_path)
                
                QMessageBox.information(self, "Success", f"Report saved:\n{pdf_path}")
                logger.info(f"PDF report generated: {pdf_path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to generate PDF")
        
        except Exception as e:
            logger.error(f"PDF generation error: {e}")
            QMessageBox.critical(self, "Error", f"PDF generation failed: {e}")
    
    def on_send_sms(self):
        """Send SMS report."""
        if not ENABLE_SMS:
            QMessageBox.warning(self, "SMS", "SMS is disabled")
            return
        
        try:
            phone = self.patient_data.get('mobile')
            
            # Prepare data
            data = {
                'name': self.patient_data.get('name'),
                'age': self.patient_data.get('age'),
                'gender': self.patient_data.get('gender'),
                'address': self.patient_data.get('address'),
                'mobile': phone,
                'doctor_name': self.patient_data.get('doctor_name', 'N/A'),
                'pulse': self.test_results.get('pulse', 'N/A'),
                'temperature': f"{self.test_results.get('temperature', 'N/A'):.1f}",
                'blood_pressure': self.test_results.get('blood_pressure', 'Not Available'),
                'ecg_status': 'Performed' if self.ecg_results else 'Not performed',
                'issues': ', '.join(self.ecg_results.get('issues', [])) if self.ecg_results else 'None',
                'emergency': 'Yes' if self.test_results.get('emergency') else 'No',
            }
            
            # Send SMS
            success = self.sms_mgr.send_health_report(phone, self.patient_data, data)
            
            if success:
                # Log to database
                if self.current_test_id:
                    self.db.log_sms(self.current_patient_id, self.current_test_id, phone, 'SENT')
                
                QMessageBox.information(self, "Success", f"SMS sent to {phone}")
                logger.info(f"SMS sent to {phone}")
            else:
                if self.current_test_id:
                    self.db.log_sms(self.current_patient_id, self.current_test_id, phone, 'FAILED')
                
                QMessageBox.warning(self, "Error", "Failed to send SMS")
        
        except Exception as e:
            logger.error(f"SMS sending error: {e}")
            QMessageBox.critical(self, "Error", f"SMS failed: {e}")
    
    def on_finish(self):
        """Finish and return to home."""
        self.show_home_screen()
    
    # Evaluation methods
    def _evaluate_pulse(self, pulse: int) -> str:
        """Evaluate pulse reading."""
        if 60 <= pulse <= 100:
            return "Normal"
        elif 40 <= pulse < 60 or 100 < pulse <= 120:
            return "Warning"
        else:
            return "Critical"
    
    def _evaluate_temperature(self, temp: float) -> str:
        """Evaluate temperature reading."""
        if 36.5 <= temp <= 37.5:
            return "Normal"
        elif 36 <= temp < 36.5 or 37.5 < temp <= 38.5:
            return "Warning"
        else:
            return "Critical"
    
    def closeEvent(self, event):
        """Handle application close."""
        logger.info("Application closing...")
        self.serial_mgr.disconnect()
        self.sms_mgr.disconnect()
        self.processor_thread.quit()
        self.processor_thread.wait()
        event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    
    window = SmartHealthHubApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
