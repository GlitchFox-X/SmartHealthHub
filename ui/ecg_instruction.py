"""
ECG Instruction Screen

Shows electrode placement diagram and instructions.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_PRIMARY, BUTTON_HEIGHT


class ECGInstructionScreen(QWidget):
    """Show ECG electrode placement instructions."""
    
    ready_clicked = pyqtSignal()
    back_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        """Initialize the UI."""
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("ECG Electrode Placement")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Diagram area
        diagram_label = QLabel()
        diagram_text = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        UPPER CHEST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    RA (Red)  ●  ● LA (Yellow)
    (Right)      (Left)
    
    
    ━━━━━━  RL (Green) ━━━━━━
    (Lower Right Leg)
    

PLACEMENT INSTRUCTIONS:
1. RA (Red): Right shoulder, below collarbone
2. LA (Yellow): Left shoulder, below collarbone  
3. RL (Green): Left lower chest, above ribs

IMPORTANT:
• Clean skin with alcohol swab before placing
• Ensure good contact with skin
• Avoid hairy areas if possible
• Keep electrodes away from jewelry
• Do NOT touch the metal parts of electrodes

Ready to proceed when all electrodes are placed.
        """
        diagram_label.setText(diagram_text)
        diagram_label.setFont(QFont("Courier", 9))
        diagram_label.setAlignment(Qt.AlignCenter)
        diagram_label.setStyleSheet("color: #333333; background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        layout.addWidget(diagram_label)
        
        layout.addStretch()
        
        # Buttons
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
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #999999;
            }}
        """)
        back_btn.setMinimumHeight(BUTTON_HEIGHT - 20)
        back_btn.clicked.connect(self.back_clicked.emit)
        button_layout.addWidget(back_btn)
        
        ready_btn = QPushButton("Ready - Start ECG →")
        ready_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #{COLOR_PRIMARY[0]:02x}{COLOR_PRIMARY[1]:02x}{COLOR_PRIMARY[2]:02x};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #005a9e;
            }}
        """)
        ready_btn.setMinimumHeight(BUTTON_HEIGHT - 20)
        ready_btn.clicked.connect(self.ready_clicked.emit)
        button_layout.addWidget(ready_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
