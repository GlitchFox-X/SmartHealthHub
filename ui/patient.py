"""
Patient Details Screen

Collects required patient information before performing health check.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QComboBox, QPushButton, QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import re

from config import (SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_PRIMARY, BUTTON_HEIGHT,
                   PHONE_REGEX, REQUIRED_PATIENT_FIELDS)


class PatientDetailsScreen(QWidget):
    """Screen for collecting patient information."""
    
    next_clicked = pyqtSignal(dict)  # Emit patient data
    back_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.patient_data = {}
        self.initUI()
    
    def initUI(self):
        """Initialize the UI."""
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setStyleSheet("background-color: white;")
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Title
        title = QLabel("Patient Information")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Scrollable form area
        scroll = QScrollArea()
        scroll.setStyleSheet("QScrollArea { border: none; }")
        scroll.setWidgetResizable(True)
        
        form_widget = QWidget()
        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)
        
        # Name
        form_layout.addWidget(QLabel("Name *"))
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(40)
        self.name_input.setStyleSheet("padding: 8px; font-size: 12px;")
        form_layout.addWidget(self.name_input)
        
        # Age
        form_layout.addWidget(QLabel("Age (years) *"))
        self.age_input = QLineEdit()
        self.age_input.setMinimumHeight(40)
        self.age_input.setInputMethodHints(Qt.ImhDigitsOnly)
        self.age_input.setStyleSheet("padding: 8px; font-size: 12px;")
        form_layout.addWidget(self.age_input)
        
        # Gender
        form_layout.addWidget(QLabel("Gender *"))
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Select...", "Male", "Female", "Other"])
        self.gender_combo.setMinimumHeight(40)
        self.gender_combo.setStyleSheet("padding: 8px; font-size: 12px;")
        form_layout.addWidget(self.gender_combo)
        
        # Mobile Number
        form_layout.addWidget(QLabel("Mobile Number (10-15 digits) *"))
        self.mobile_input = QLineEdit()
        self.mobile_input.setMinimumHeight(40)
        self.mobile_input.setInputMethodHints(Qt.ImhDigitsOnly)
        self.mobile_input.setStyleSheet("padding: 8px; font-size: 12px;")
        form_layout.addWidget(self.mobile_input)
        
        # Address
        form_layout.addWidget(QLabel("Address *"))
        self.address_input = QLineEdit()
        self.address_input.setMinimumHeight(40)
        self.address_input.setStyleSheet("padding: 8px; font-size: 12px;")
        form_layout.addWidget(self.address_input)
        
        # Doctor Name (optional)
        form_layout.addWidget(QLabel("Doctor Name (optional)"))
        self.doctor_name_input = QLineEdit()
        self.doctor_name_input.setMinimumHeight(40)
        self.doctor_name_input.setStyleSheet("padding: 8px; font-size: 12px;")
        form_layout.addWidget(self.doctor_name_input)
        
        # Doctor Phone (optional)
        form_layout.addWidget(QLabel("Doctor Phone (optional)"))
        self.doctor_phone_input = QLineEdit()
        self.doctor_phone_input.setMinimumHeight(40)
        self.doctor_phone_input.setStyleSheet("padding: 8px; font-size: 12px;")
        form_layout.addWidget(self.doctor_phone_input)
        
        form_layout.addStretch()
        form_widget.setLayout(form_layout)
        scroll.setWidget(form_widget)
        main_layout.addWidget(scroll)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #cccccc;
                color: black;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #999999;
            }}
        """)
        back_btn.setMinimumHeight(BUTTON_HEIGHT - 20)
        back_btn.clicked.connect(self.back_clicked.emit)
        button_layout.addWidget(back_btn)
        
        next_btn = QPushButton("Next →")
        next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #{COLOR_PRIMARY[0]:02x}{COLOR_PRIMARY[1]:02x}{COLOR_PRIMARY[2]:02x};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #005a9e;
            }}
        """)
        next_btn.setMinimumHeight(BUTTON_HEIGHT - 20)
        next_btn.clicked.connect(self.validate_and_proceed)
        button_layout.addWidget(next_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def validate_and_proceed(self):
        """Validate patient data and emit signal."""
        # Validate required fields
        name = self.name_input.text().strip()
        age_str = self.age_input.text().strip()
        gender = self.gender_combo.currentText()
        mobile = self.mobile_input.text().strip()
        address = self.address_input.text().strip()
        doctor_name = self.doctor_name_input.text().strip()
        doctor_phone = self.doctor_phone_input.text().strip()
        
        # Check required fields
        if not name:
            QMessageBox.warning(self, "Validation", "Please enter patient name.")
            return
        
        if not age_str or not age_str.isdigit() or not (1 <= int(age_str) <= 150):
            QMessageBox.warning(self, "Validation", "Please enter a valid age (1-150).")
            return
        
        if gender == "Select...":
            QMessageBox.warning(self, "Validation", "Please select a gender.")
            return
        
        if not mobile or not re.match(PHONE_REGEX, mobile):
            QMessageBox.warning(self, "Validation", "Please enter a valid mobile number (10-15 digits).")
            return
        
        if not address:
            QMessageBox.warning(self, "Validation", "Please enter an address.")
            return
        
        # Build patient data dictionary
        self.patient_data = {
            "name": name,
            "age": int(age_str),
            "gender": gender,
            "mobile": mobile,
            "address": address,
            "doctor_name": doctor_name or None,
            "doctor_phone": doctor_phone or None,
        }
        
        self.next_clicked.emit(self.patient_data)
    
    def clear_form(self):
        """Clear all form fields."""
        self.name_input.clear()
        self.age_input.clear()
        self.gender_combo.setCurrentIndex(0)
        self.mobile_input.clear()
        self.address_input.clear()
        self.doctor_name_input.clear()
        self.doctor_phone_input.clear()
