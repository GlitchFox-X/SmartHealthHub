"""
ECG Test Screen with Live Waveform Display

Displays real-time ECG waveform from AD8232 sensor.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

try:
    import pyqtgraph as pg
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_PRIMARY, BUTTON_HEIGHT


class ECGTestScreen(QWidget):
    """ECG test screen with live waveform display."""
    
    stop_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.ecg_data = []
        self.max_points = 1000
        self.lead_off = False
        self.initUI()
    
    def initUI(self):
        """Initialize the UI."""
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title bar
        title_layout = QHBoxLayout()
        
        title = QLabel("ECG Test - Live Recording")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title_layout.addWidget(title)
        
        self.time_label = QLabel("00:00")
        time_font = QFont()
        time_font.setPointSize(12)
        time_font.setBold(True)
        self.time_label.setFont(time_font)
        self.time_label.setAlignment(Qt.AlignRight)
        title_layout.addWidget(self.time_label)
        
        layout.addLayout(title_layout)
        
        # Status line
        self.status_label = QLabel("Acquiring ECG data...")
        self.status_label.setStyleSheet("color: #0078D7; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Waveform plot area
        if PYQTGRAPH_AVAILABLE:
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setLabel('left', 'ECG Voltage', units='mV')
            self.plot_widget.setLabel('bottom', 'Time', units='ms')
            self.plot_widget.setTitle('Electrocardiogram')
            self.plot_widget.setStyleSheet("border: 1px solid #cccccc;")
            
            # Configure plot
            self.plot_widget.getPlotItem().getAxis('left').setPen(pg.mkPen('#333333'))
            self.plot_widget.getPlotItem().getAxis('bottom').setPen(pg.mkPen('#333333'))
            self.plot_widget.getPlotItem().getAxis('left').setTextPen(pg.mkPen('#000000'))
            self.plot_widget.getPlotItem().getAxis('bottom').setTextPen(pg.mkPen('#000000'))
            
            self.curve = self.plot_widget.plot(pen=pg.mkPen('#0078D7', width=2))
            layout.addWidget(self.plot_widget)
        else:
            # Fallback: simple text display
            self.waveform_text = QLabel(
                "Waveform display requires PyQtGraph.\n"
                "Install: pip install pyqtgraph\n\n"
                "Recording ECG data..."
            )
            self.waveform_text.setAlignment(Qt.AlignCenter)
            self.waveform_text.setStyleSheet(
                "border: 1px solid #cccccc; padding: 20px; "
                "background-color: #f0f0f0; font-size: 12px;"
            )
            layout.addWidget(self.waveform_text)
        
        # Info bar
        self.info_label = QLabel("Samples: 0 | Lead-off: No")
        self.info_label.setStyleSheet("color: #666666; font-size: 11px;")
        layout.addWidget(self.info_label)
        
        # Stop button
        stop_btn = QPushButton("Stop ECG")
        stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #cc0000;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #990000;
            }}
        """)
        stop_btn.setMinimumHeight(BUTTON_HEIGHT - 20)
        stop_btn.clicked.connect(self.on_stop)
        layout.addWidget(stop_btn)
        
        self.setLayout(layout)
        
        # Timer for updating display
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.elapsed_seconds = 0
    
    def add_ecg_sample(self, timestamp_ms: int, value: int):
        """Add a new ECG sample."""
        self.ecg_data.append((timestamp_ms, value))
        
        # Keep only recent data
        if len(self.ecg_data) > self.max_points:
            self.ecg_data.pop(0)
    
    def set_lead_off(self, detected: bool):
        """Set lead-off detection status."""
        self.lead_off = detected
        if detected:
            self.status_label.setText("⚠️ LEAD-OFF DETECTED - Check electrode connections")
            self.status_label.setStyleSheet("color: #ff6600; font-weight: bold;")
        else:
            self.status_label.setText("✓ ECG recording - Electrodes connected")
            self.status_label.setStyleSheet("color: #00aa00; font-weight: bold;")
    
    def start_recording(self):
        """Start ECG recording."""
        self.ecg_data.clear()
        self.elapsed_seconds = 0
        self.update_timer.start(1000)  # Update every second
        self.status_label.setText("✓ ECG recording - Electrodes connected")
        self.status_label.setStyleSheet("color: #00aa00; font-weight: bold;")
    
    def stop_recording(self):
        """Stop ECG recording."""
        self.update_timer.stop()
    
    def update_display(self):
        """Update the waveform display."""
        self.elapsed_seconds += 1
        minutes = self.elapsed_seconds // 60
        seconds = self.elapsed_seconds % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        
        # Update waveform plot
        if PYQTGRAPH_AVAILABLE and self.ecg_data:
            timestamps = [x[0] for x in self.ecg_data]
            values = [x[1] for x in self.ecg_data]
            self.curve.setData(timestamps, values)
        
        # Update info
        lead_off_text = "Yes ⚠️" if self.lead_off else "No ✓"
        self.info_label.setText(
            f"Samples: {len(self.ecg_data)} | Lead-off: {lead_off_text} | "
            f"Duration: {self.elapsed_seconds}s"
        )
    
    def on_stop(self):
        """Handle stop button."""
        self.stop_recording()
        self.stop_clicked.emit()
    
    def get_ecg_data(self):
        """Get all recorded ECG data."""
        return self.ecg_data
