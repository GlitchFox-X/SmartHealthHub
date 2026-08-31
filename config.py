"""
Smart Health Hub Configuration

Central location for all application constants and settings.
"""

import os
from pathlib import Path

# Application Info
APP_NAME = "Smart Health Hub"
APP_VERSION = "1.0.0"
ORGANIZATION = "Healthcare Solutions"

# Display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
DISPLAY_DPI = 96

# Paths
BASE_DIR = Path(__file__).parent.absolute()
REPORTS_DIR = BASE_DIR / "reports"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure directories exist
for directory in [REPORTS_DIR, DATA_DIR, LOGS_DIR, ASSETS_DIR]:
    directory.mkdir(exist_ok=True)

# Database
DATABASE_PATH = DATA_DIR / "app.db"

# Arduino Serial Connection
ARDUINO_PORT = "/dev/ttyUSB0"  # Raspberry Pi, change to COM3 or similar on Windows
ARDUINO_BAUD = 9600
ARDUINO_TIMEOUT = 2

# Sensor Pins (Arduino)
PULSE_SENSOR_PIN = "A0"
TEMPERATURE_SENSOR_PIN = "A1"
TOUCH_SENSOR_PIN = "A2"
ECG_SENSOR_PIN = "A3"
ECG_LO_PLUS_PIN = 10
ECG_LO_MINUS_PIN = 11

# Test Durations
BASIC_TEST_DURATION = 10  # seconds
TOUCH_CONFIRMATION_DURATION = 3  # seconds
ECG_LEAD_OFF_THRESHOLD = 2  # seconds without data

# Sensor Calibration & Thresholds
TEMPERATURE_OFFSET = 0  # Adjust based on calibration
TEMPERATURE_MULTIPLIER = 1.0
PULSE_MIN = 40
PULSE_MAX = 200
TEMPERATURE_MIN = 32  # Celsius
TEMPERATURE_MAX = 42

# Blood Pressure Module
# HX710B hardware will be integrated separately.
# Currently placeholder until hardware is available.
BP_STATUS = "Not Available"

# Emergency Thresholds
EMERGENCY_PULSE_MIN = 40
EMERGENCY_PULSE_MAX = 150
EMERGENCY_TEMPERATURE_MAX = 40

# SIM800L Configuration
SIM800L_PORT = "/dev/ttyUSB1"  # Or COM4, etc.
SIM800L_BAUD = 9600
SIM800L_TIMEOUT = 5
SMS_ENABLED = True

# SMS Content Template
SMS_TEMPLATE = """Smart Health Hub Report

Name: {name}
Age: {age}
Gender: {gender}
Address: {address}
Mobile: {mobile}
Doctor: {doctor}

Pulse: {pulse} bpm
Temperature: {temperature} C
Blood Pressure: {bp}
ECG: {ecg}
Issues: {issues}
Emergency: {emergency}
"""

# PDF Report Configuration
PDF_TITLE = "Smart Health Hub Report"
PDF_AUTHOR = "Healthcare Solutions"
PDF_PAGE_WIDTH = 8.5  # inches (letter)
PDF_PAGE_HEIGHT = 11

# Logging
LOG_FILE = LOGS_DIR / "app.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# UI Styling
BUTTON_FONT_SIZE = 14
TITLE_FONT_SIZE = 18
LABEL_FONT_SIZE = 12
BUTTON_HEIGHT = 60
BUTTON_MIN_WIDTH = 200

# Touchscreen specific
TOUCH_SENSITIVITY = 100  # milliseconds before considering a touch
LONG_PRESS_DURATION = 1000  # milliseconds

# Serial Protocol Commands
SERIAL_COMMANDS = {
    "START_TEST": "START_TEST\n",
    "START_ECG": "START_ECG\n",
    "STOP_ECG": "STOP_ECG\n",
    "RESET": "RESET\n",
}

# Feature Flags
ENABLE_ECG = True
ENABLE_SMS = True
ENABLE_PDF = True
OFFLINE_MODE = False  # If True, app runs without Arduino/SIM800L

# Validation Rules
REQUIRED_PATIENT_FIELDS = ["name", "age", "gender", "mobile", "address"]
PHONE_REGEX = r"^\d{10,15}$"  # Basic international phone validation

# Theme Colors (RGB tuples)
COLOR_PRIMARY = (0, 120, 215)
COLOR_SUCCESS = (50, 200, 50)
COLOR_WARNING = (255, 180, 0)
COLOR_DANGER = (220, 50, 50)
COLOR_BACKGROUND = (240, 240, 240)
COLOR_TEXT = (0, 0, 0)
