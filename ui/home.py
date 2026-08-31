"""
Home Screen

Initial screen displayed when application starts.
Contains app logo and "START HEALTH CHECK" button.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_PRIMARY, BUTTON_HEIGHT, BUTTON_MIN_WIDTH, APP_NAME


class HomeScreen(QWidget):
    """Home screen with START button."""
    
    start_clicked = pyqtSignal()
    
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
        title = QLabel(APP_NAME)
        title_font = QFont()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Smart Health Monitoring System")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666666;")
        layout.addWidget(subtitle)
        
        # Spacer
        layout.addStretch()
        
        # Start Button
        start_btn = QPushButton("START HEALTH CHECK")
        start_btn.setFont(QFont("Arial", 16, QFont.Bold))
        start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #{COLOR_PRIMARY[0]:02x}{COLOR_PRIMARY[1]:02x}{COLOR_PRIMARY[2]:02x};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #005a9e;
            }}
        """)
        start_btn.setMinimumHeight(BUTTON_HEIGHT)
        start_btn.setMinimumWidth(BUTTON_MIN_WIDTH)
        start_btn.clicked.connect(self.start_clicked.emit)
        layout.addWidget(start_btn, alignment=Qt.AlignCenter)
        
        layout.addStretch()
        
        self.setLayout(layout)
