# Smart Health Hub

A native PyQt5 desktop application for Raspberry Pi OS that implements a complete health monitoring system with Arduino sensor integration.

**Version:** 1.0.0

## Features

✓ **Patient Management** - Collect and store patient information
✓ **Basic Health Test** - Measure pulse and temperature in real-time
✓ **ECG Monitoring** - Record and display live ECG waveforms  
✓ **PDF Reports** - Generate professional health reports
✓ **SMS Notifications** - Send health summaries via SMS (SIM800L modem)
✓ **SQLite Database** - Persistent local storage of patient records
✓ **Touchscreen UI** - Optimized for 800x480 display
✓ **No Browser** - Pure native PyQt5 application

## Requirements

### Hardware

- **Raspberry Pi** (3B+ or newer recommended)
- **7-inch touchscreen display** (800x480)
- **Arduino Mega 2560**
- **Sensors:**
  - Pulse sensor (analog, A0)
  - LM35 temperature sensor (analog, A1)
  - Capacitive touch sensor (digital, A2)
  - AD8232 ECG module (analog A3, lead-off D10, D11)
- **SIM800L GSM modem** (optional, for SMS)
- **USB cables** (Arduino to Raspberry Pi, SIM800L to Raspberry Pi)

### Software

- Raspberry Pi OS (Bookworm or later)
- Python 3.8+
- Dependencies: See `requirements.txt`

## Installation

### 1. Prepare Raspberry Pi

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip python3-dev
```

### 2. Clone/Download Project

```bash
cd /home/pi
git clone <repository-url> SmartHealthHub
cd SmartHealthHub
```

### 3. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Upload Arduino Code

1. Connect Arduino Mega 2560 to your computer with USB
2. Open Arduino IDE
3. Load the sketch from: `arduino/sketch.ino`
4. Install the required libraries:
   - No external libraries required (uses Arduino core functions)
5. Upload to Arduino Mega 2560

### 5. Configure Hardware Connections

Edit `config.py` to match your hardware setup:

```python
# USB Serial Ports
ARDUINO_PORT = "/dev/ttyUSB0"      # Arduino connection
SIM800L_PORT = "/dev/ttyUSB1"      # SIM800L modem connection

# Baud rates
ARDUINO_BAUD = 9600
SIM800L_BAUD = 9600

# Sensor calibration (adjust based on your sensors)
TEMPERATURE_OFFSET = 0
TEMPERATURE_MULTIPLIER = 1.0
```

### 6. Create Desktop Launcher (Raspberry Pi)

```bash
mkdir -p ~/.local/share/applications
cp SmartHealthHub.desktop ~/.local/share/applications/
sed -i 's|/home/pi/SmartHealthHub|'$(pwd)'|g' ~/.local/share/applications/SmartHealthHub.desktop
```

Or run from terminal:
```bash
python3 main.py
```

## Project Structure

```
SmartHealthHub/
├── main.py                          # Main application
├── config.py                        # Configuration constants
├── requirements.txt                 # Python dependencies
├── SmartHealthHub.desktop          # Linux launcher
│
├── arduino/
│   ├── sketch.ino                  # Arduino Mega code
│   └── serial_manager.py           # Serial communication
│
├── sensors/
│   ├── pulse.py                    # Pulse data processing
│   ├── temperature.py              # Temperature data processing
│   └── ecg.py                      # ECG data processing
│
├── database/
│   └── database.py                 # SQLite operations
│
├── communication/
│   └── sim800l.py                  # SMS via SIM800L
│
├── reports/
│   └── pdf_generator.py            # PDF report generation
│
├── ui/
│   ├── home.py                     # Home screen
│   ├── patient.py                  # Patient details form
│   ├── basic_test.py               # Basic test screen
│   ├── results.py                  # Test results display
│   ├── ecg_decision.py             # ECG yes/no decision
│   ├── ecg_instruction.py          # Electrode placement guide
│   ├── ecg_test.py                 # Live ECG recording
│   └── report.py                   # Final report summary
│
├── data/
│   └── app.db                      # SQLite database (auto-created)
├── reports/                        # Generated PDF reports
├── logs/                           # Application logs
└── assets/                         # Application assets
```

## Hardware Setup

### Arduino Wiring

```
SENSORS TO ARDUINO MEGA 2560:
- Pulse Sensor Signal    → A0
- LM35 Output            → A1
- Touch Sensor Signal    → A2
- AD8232 ECG Output      → A3
- AD8232 LO+ (ref)       → D10
- AD8232 LO- (ref)       → D11
- GND                    → GND
- 5V                     → 5V

ARDUINO TO RASPBERRY PI:
- USB Data (micro-USB)   → USB port on Pi
```

### AD8232 ECG Electrode Placement

```
       RA (Red)     LA (Yellow)
       Right        Left
       Shoulder     Shoulder
         ●           ●
        
        
    RL (Green)
    Left Lower Chest
       ●
```

**Placement Guide:**
- **RA (Red):** Right shoulder, just below right collarbone
- **LA (Yellow):** Left shoulder, just below left collarbone
- **RL (Green):** Left side, below lower rib on left chest

### SIM800L Configuration (Optional)

For SMS functionality:

1. Connect SIM800L module to Raspberry Pi via USB adapter
2. Insert active SIM card into SIM800L
3. Configure in `config.py`:

```python
SMS_ENABLED = True
SIM800L_PORT = "/dev/ttyUSB1"
SIM800L_BAUD = 9600
```

## Usage

### Starting the Application

From Raspberry Pi desktop:
- Double-click "Smart Health Hub" launcher

From terminal:
```bash
cd /home/pi/SmartHealthHub
python3 main.py
```

### Workflow

1. **Home Screen** → Press "START HEALTH CHECK"
2. **Patient Details** → Enter patient information
3. **Sensor Pad Test** → Place hand on sensor pad for 3-second confirmation, then 10-second test
4. **Results** → View pulse and temperature readings
5. **ECG Decision** → Choose to perform ECG or skip
6. **ECG Test** (if selected) → Place electrodes and record 30-60 second ECG
7. **Report** → View summary with options to:
   - Save as PDF
   - Send SMS to patient
   - Finish and return to home

## Configuration

### Key Settings in `config.py`

```python
# Display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

# Sensor thresholds
EMERGENCY_PULSE_MIN = 40
EMERGENCY_PULSE_MAX = 150
EMERGENCY_TEMPERATURE_MAX = 40

# Test timing
BASIC_TEST_DURATION = 10        # seconds
TOUCH_CONFIRMATION_DURATION = 3 # seconds

# Features
ENABLE_ECG = True
ENABLE_SMS = True
ENABLE_PDF = True
OFFLINE_MODE = False            # Test without hardware
```

### Calibration

1. **Temperature Sensor:**
   - Adjust `TEMPERATURE_OFFSET` and `TEMPERATURE_MULTIPLIER` in `config.py`
   - Test with known temperature reference
   
2. **Pulse Sensor:**
   - Pulse estimation uses signal mapping in `sensors/pulse.py`
   - Adjust `MIN_RAW_VALUE`, `MAX_RAW_VALUE` if needed

## Serial Protocol

### Arduino ↔ Raspberry Pi Communication

All communication uses **line-delimited JSON** at 9600 baud:

**Commands sent to Arduino:**
```
START_TEST
START_ECG
STOP_ECG
RESET
```

**Responses from Arduino:**
```json
{"type":"status","value":"TOUCH_WAIT"}
{"type":"status","value":"TOUCH_CONFIRMED"}
{"type":"status","value":"TEST_ONGOING"}
{"type":"basic","pulse":72,"temperature":36.7,"bp":"UNAVAILABLE"}
{"type":"status","value":"TEST_COMPLETE"}
{"type":"status","value":"ECG_STARTING"}
{"type":"ecg","timestamp":1000,"value":512}
{"type":"status","value":"ECG_LEAD_OFF"}
{"type":"status","value":"ECG_COMPLETE"}
```

## Important Notes

### Blood Pressure

⚠️ **Currently Unavailable** - The HX710B load cell amplifier hardware is faulty. BP field is reserved in the architecture but marked as simulated/unavailable. To enable:

1. Replace HX710B module with working unit
2. Implement weight-to-pressure calibration in `sensors/` 
3. Update Arduino code to read from HX710B pins

### ECG Data

- Raw ECG samples are collected at ~100 Hz (10ms intervals)
- No smoothing or filtering is applied (raw acquisition preserved)
- Lead-off detection uses AD8232 LO+/LO- pins
- For medical diagnosis, require professional ECG interpretation

### No Fake Data

- All displayed readings come from actual sensors
- No synthetic data generation
- Application handles sensor unavailability gracefully
- Test mode (`OFFLINE_MODE=True`) simulates for development only

## Troubleshooting

### Arduino Not Detected

```bash
# Check USB connection
ls /dev/ttyUSB*

# Check permissions
sudo usermod -a -G dialout $USER
# Then reboot
```

### Serial Port Access Error

```bash
sudo chmod 666 /dev/ttyUSB0
sudo chmod 666 /dev/ttyUSB1
```

### SIM800L Not Responding

```bash
# Test AT commands
minicom -b 9600 -o -D /dev/ttyUSB1

# Send: AT
# Should receive: OK
```

### GUI Display Issues

- Ensure HDMI is connected before power-on
- Check touchscreen calibration
- In Raspberry Pi settings, set rotation to 0°

### Application Crashes

Check log file:
```bash
tail -f logs/app.log
```

## Development & Testing

### Run in Offline Mode

```python
# In config.py
OFFLINE_MODE = True
```

This allows testing UI without Arduino/SIM800L.

### Enable Debug Logging

```python
# In config.py
LOG_LEVEL = "DEBUG"
```

### Run Tests

```bash
# Check syntax
python3 -m py_compile main.py ui/*.py sensors/*.py database/*.py

# Check imports
python3 -c "import main; print('OK')"
```

## Database

SQLite database created at: `data/app.db`

**Tables:**
- `patients` - Patient information
- `tests` - Health test records
- `basic_results` - Basic test measurements
- `ecg_data` - ECG recordings
- `reports` - PDF report paths
- `sms_logs` - SMS delivery status

View database:
```bash
sqlite3 data/app.db
sqlite> .tables
sqlite> SELECT * FROM patients;
```

## PDF Reports

Generated reports saved to: `reports/report_*.pdf`

**Contents:**
- Patient information
- Test timestamp
- Vital measurements
- ECG summary (if performed)
- Observations
- Disclaimer for professional evaluation

## SMS Reports

Format example:
```
Smart Health Hub Report

Name: John Smith
Age: 45
Gender: Male
Address: 123 Main St
Mobile: +1234567890

Pulse: 72 bpm
Temperature: 36.7 C
Blood Pressure: UNAVAILABLE - Hardware faulty
ECG: Performed
Issues: None
Emergency: No
```

## Known Limitations

1. **Blood Pressure:** Hardware (HX710B) is faulty - field reserved for future use
2. **ECG Analysis:** Not for medical diagnosis - requires professional interpretation
3. **SMS:** Depends on active SIM card and network coverage
4. **Display:** Optimized for 800x480 - may not work well on other resolutions
5. **Offline Mode:** Uses simulated sensor data for development/testing only

## Future Enhancements

- [ ] Multi-language support
- [ ] Patient history visualization
- [ ] Bluetooth sensor support
- [ ] Cloud backup integration
- [ ] Medical provider portal
- [ ] Advanced ECG analysis algorithms
- [ ] Battery status monitoring
- [ ] Wireless charging dock integration

## License

Copyright © 2026 Healthcare Solutions

## Support

For issues, questions, or contributions:
- Check logs in `logs/app.log`
- Review troubleshooting section
- Inspect serial protocol for debugging
- Run offline tests

## Author

Smart Health Hub Development Team

---

**Last Updated:** 2026-08-31
**Application Version:** 1.0.0
