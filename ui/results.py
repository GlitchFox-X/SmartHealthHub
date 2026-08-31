"""
Basic Test Results Screen

Displays pulse, temperature, and blood pressure readings.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, BUTTON_HEIGHT


class ResultsScreen(QWidget):
    """Display basic test results."""
    
    next_clicked = pyqtSignal()
    back_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        """Initialize the UI."""
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Test Results")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Results grid
        results_layout = QVBoxLayout()
        results_layout.setSpacing(20)
        
        # Pulse
        pulse_label = QLabel("Heart Rate (Pulse)")
        pulse_label.setFont(QFont("Arial", 14, QFont.Bold))
        results_layout.addWidget(pulse_label)
        
        self.pulse_value = QLabel("-- BPM")
        pulse_font = QFont("Arial", 28, QFont.Bold)
        self.pulse_value.setFont(pulse_font)
        self.pulse_value.setAlignment(Qt.AlignCenter)
        self.pulse_value.setStyleSheet(f"color: #{COLOR_PRIMARY[0]:02x}{COLOR_PRIMARY[1]:02x}{COLOR_PRIMARY[2]:02x}; padding: 10px;")
        results_layout.addWidget(self.pulse_value)
        
        # Temperature
        temp_label = QLabel("Body Temperature")
        temp_label.setFont(QFont("Arial", 14, QFont.Bold))
        results_layout.addWidget(temp_label)
        
        self.temp_value = QLabel("-- °C")
        temp_font = QFont("Arial", 28, QFont.Bold)
        self.temp_value.setFont(temp_font)
        self.temp_value.setAlignment(Qt.AlignCenter)
        self.temp_value.setStyleSheet(f"color: #{COLOR_PRIMARY[0]:02x}{COLOR_PRIMARY[1]:02x}{COLOR_PRIMARY[2]:02x}; padding: 10px;")
        results_layout.addWidget(self.temp_value)
        
        # Blood Pressure
        bp_label = QLabel("Blood Pressure")
        bp_label.setFont(QFont("Arial", 14, QFont.Bold))
        results_layout.addWidget(bp_label)
        
        self.bp_value = QLabel("Not Available")
        bp_font = QFont("Arial", 14)
        self.bp_value.setFont(bp_font)
        self.bp_value.setAlignment(Qt.AlignCenter)
        self.bp_value.setStyleSheet("color: #999999; padding: 10px;")
        results_layout.addWidget(self.bp_value)
        
        layout.addLayout(results_layout)
        layout.addStretch()
        
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
        
        next_btn = QPushButton("Continue →")
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
        next_btn.clicked.connect(self.next_clicked.emit)
        button_layout.addWidget(next_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def set_results(self, pulse: int, temperature: float, bp_status: str = "Not Available"):
        """Set and display test results."""
        self.pulse_value.setText(f"{pulse} BPM")
        self.temp_value.setText(f"{temperature:.1f} °C")
        self.bp_value.setText("Not Available")
        
        # Color code based on values
        if 60 <= pulse <= 100:
            self.pulse_value.setStyleSheet(f"color: #{COLOR_SUCCESS[0]:02x}{COLOR_SUCCESS[1]:02x}{COLOR_SUCCESS[2]:02x}; padding: 10px;")
        elif 40 <= pulse < 60 or 100 < pulse <= 120:
            self.pulse_value.setStyleSheet("color: #ff9900; padding: 10px;")
        else:
            self.pulse_value.setStyleSheet("color: #ff0000; padding: 10px;")
        
        if 36.5 <= temperature <= 37.5:
            self.temp_value.setStyleSheet(f"color: #{COLOR_SUCCESS[0]:02x}{COLOR_SUCCESS[1]:02x}{COLOR_SUCCESS[2]:02x}; padding: 10px;")
        elif 36 <= temperature < 36.5 or 37.5 < temperature <= 38.5:
            self.temp_value.setStyleSheet("color: #ff9900; padding: 10px;")
        else:
            self.temp_value.setStyleSheet("color: #ff0000; padding: 10px;")
