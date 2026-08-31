"""
Basic Test / Sensor Pad Screen

Shows instructions and progress during the basic health test.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_PRIMARY, BUTTON_HEIGHT, BASIC_TEST_DURATION


class BasicTestScreen(QWidget):
    """Screen for basic health test on sensor pad."""
    
    test_started = pyqtSignal()
    test_cancelled = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.test_active = False
        self.elapsed_seconds = 0
        self.timer = None
        self.initUI()
    
    def initUI(self):
        """Initialize the UI."""
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 40, 20, 40)
        layout.setSpacing(20)
        layout.addStretch()
        
        # Title
        title = QLabel("Health Check Test")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Status Label
        self.status_label = QLabel("Please place your hand on the sensor pad")
        status_font = QFont()
        status_font.setPointSize(14)
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #0078D7; margin: 20px;")
        layout.addWidget(self.status_label)
        
        # Instructions
        self.instruction_label = QLabel(
            "Keep your hand steady on the sensor pad.\n"
            "The test will take 10 seconds."
        )
        inst_font = QFont()
        inst_font.setPointSize(12)
        self.instruction_label.setFont(inst_font)
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.instruction_label)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(BASIC_TEST_DURATION)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Timer Display
        self.timer_label = QLabel("0 / 10 seconds")
        timer_font = QFont()
        timer_font.setPointSize(16)
        timer_font.setBold(True)
        self.timer_label.setFont(timer_font)
        self.timer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.timer_label)
        
        layout.addStretch()
        
        # Cancel Button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #cc0000;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #990000;
            }}
        """)
        cancel_btn.setMinimumHeight(BUTTON_HEIGHT - 20)
        cancel_btn.clicked.connect(self.on_cancel)
        layout.addWidget(cancel_btn)
        
        self.setLayout(layout)
        
        # Timer for updating progress
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
    
    def start_test(self):
        """Start the test."""
        self.test_active = True
        self.elapsed_seconds = 0
        self.progress_bar.setValue(0)
        self.status_label.setText("✓ Hand detected - Test in progress")
        self.status_label.setStyleSheet("color: #00aa00; margin: 20px;")
        self.instruction_label.setText("Keep steady - Do not move your hand")
        self.progress_timer.start(1000)  # Update every second
        self.test_started.emit()
    
    def update_progress(self):
        """Update progress bar and timer."""
        self.elapsed_seconds += 1
        self.progress_bar.setValue(self.elapsed_seconds)
        self.timer_label.setText(f"{self.elapsed_seconds} / {BASIC_TEST_DURATION} seconds")
        
        if self.elapsed_seconds >= BASIC_TEST_DURATION:
            self.progress_timer.stop()
            self.test_active = False
    
    def set_status(self, status: str):
        """Update status message."""
        if status == "TOUCH_WAIT":
            self.status_label.setText("Place your hand on the sensor pad and keep it there")
            self.status_label.setStyleSheet("color: #0078D7; margin: 20px;")
        elif status == "TOUCH_CONFIRMED":
            self.start_test()
        elif status == "TOUCH_LOST":
            self.status_label.setText("Hand removed - Touch lost. Please reposition.")
            self.status_label.setStyleSheet("color: #ff6600; margin: 20px;")
    
    def on_cancel(self):
        """Cancel test."""
        self.progress_timer.stop()
        self.test_active = False
        self.test_cancelled.emit()
