"""
ECG Decision Screen

Asks user whether to perform ECG test.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_PRIMARY, BUTTON_HEIGHT


class ECGDecisionScreen(QWidget):
    """Ask user if they want to perform ECG test."""
    
    ecg_yes_clicked = pyqtSignal()
    ecg_no_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        """Initialize the UI."""
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 40, 20, 40)
        layout.setSpacing(30)
        layout.addStretch()
        
        # Title
        title = QLabel("ECG Test")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Question
        question = QLabel("Would you like to perform an ECG test?")
        q_font = QFont()
        q_font.setPointSize(16)
        question.setFont(q_font)
        question.setAlignment(Qt.AlignCenter)
        question.setStyleSheet("color: #333333; margin: 20px;")
        layout.addWidget(question)
        
        # Info
        info = QLabel(
            "ECG (Electrocardiogram) measures electrical activity of your heart.\n"
            "The test takes approximately 30-60 seconds.\n\n"
            "You will need to wear ECG electrodes on your chest."
        )
        info_font = QFont()
        info_font.setPointSize(11)
        info.setFont(info_font)
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #666666;")
        layout.addWidget(info)
        
        layout.addStretch()
        
        # Yes Button
        yes_btn = QPushButton("YES - Perform ECG")
        yes_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #{COLOR_PRIMARY[0]:02x}{COLOR_PRIMARY[1]:02x}{COLOR_PRIMARY[2]:02x};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #005a9e;
            }}
        """)
        yes_btn.setMinimumHeight(BUTTON_HEIGHT)
        yes_btn.clicked.connect(self.ecg_yes_clicked.emit)
        layout.addWidget(yes_btn)
        
        # No Button
        no_btn = QPushButton("NO - Skip ECG")
        no_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #999999;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #666666;
            }}
        """)
        no_btn.setMinimumHeight(BUTTON_HEIGHT)
        no_btn.clicked.connect(self.ecg_no_clicked.emit)
        layout.addWidget(no_btn)
        
        layout.addStretch()
        
        self.setLayout(layout)
