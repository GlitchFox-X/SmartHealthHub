# Smart Health Hub - Quick Reference Guide

## Quick Start (Raspberry Pi)

### First Time Setup

```bash
# 1. Navigate to project directory
cd /home/pi/SmartHealthHub

# 2. Run setup script
bash setup.sh

# 3. Reboot (to apply serial port permissions)
sudo reboot

# 4. Upload Arduino code
#    - Connect Arduino Mega to computer
#    - Open Arduino IDE
#    - Open arduino/sketch.ino
#    - Upload to board

# 5. Connect Arduino and SIM800L to Raspberry Pi via USB

# 6. Run application
python3 main.py
```

## Configuration Quick Reference

### File: `config.py`

**Hardware Ports:**
```python
ARDUINO_PORT = "/dev/ttyUSB0"      # Change if different
SIM800L_PORT = "/dev/ttyUSB1"      # Change if different
```

**Sensor Calibration:**
```python
TEMPERATURE_OFFSET = 0             # Adjust for calibration
TEMPERATURE_MULTIPLIER = 1.0       # Adjust for calibration
```

**Feature Toggles:**
```python
OFFLINE_MODE = False               # True = no Arduino needed
ENABLE_ECG = True
ENABLE_SMS = True
ENABLE_PDF = True
```

## Testing & Debugging

### Check Serial Ports

```bash
ls /dev/ttyUSB*
```

Should show `/dev/ttyUSB0` and/or `/dev/ttyUSB1`

### Test Arduino Connection

```bash
# Install minicom if needed
sudo apt-get install minicom

# Connect to Arduino
minicom -b 9600 -o -D /dev/ttyUSB0

# Type: AT
# Should echo back: AT
# Then response: OK or nothing (if not ATmega)
```

### Test SIM800L Modem

```bash
minicom -b 9600 -o -D /dev/ttyUSB1

# Type: AT
# Should respond: OK

# Type: AT+CPIN?
# Should respond: +CPIN: READY (or SIM PIN required)

# Type: AT+CSQ
# Should respond: +CSQ: signal,0
```

### Run in Debug Mode

```python
# In config.py, change:
LOG_LEVEL = "DEBUG"

# Then run:
python3 main.py

# Check logs:
tail -f logs/app.log
```

### Offline Testing (No Hardware)

```python
# In config.py:
OFFLINE_MODE = True

# Run:
python3 main.py
# UI will work without Arduino/modem
```

## Database Access

### View Patient Records

```bash
sqlite3 data/app.db

# List all patients
SELECT id, name, age, mobile FROM patients;

# Show test history for patient 1
SELECT t.*, b.pulse, b.temperature
FROM tests t
LEFT JOIN basic_results b ON t.id = b.test_id
WHERE t.patient_id = 1
ORDER BY t.test_date DESC;

# Exit
.quit
```

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'PyQt5'"

**Solution:**
```bash
pip3 install PyQt5
```

### Issue: Serial Port Permission Denied

**Solution:**
```bash
sudo usermod -a -G dialout $USER
# Then reboot
```

### Issue: Arduino Not Responding

**Check:**
1. USB cable is connected
2. Arduino has power (LED lights up)
3. Correct port in config.py
4. Arduino IDE can upload to it

### Issue: SIM800L Not Responding

**Check:**
1. Module has power (red LED on)
2. SIM card is inserted
3. Antenna is connected
4. Correct port in config.py
5. Try with minicom to test AT commands

### Issue: Touchscreen Not Working

**Solution:**
```bash
# Calibrate touchscreen
sudo DISPLAY=:0 xinput_calibrator

# Or use GUI settings in Raspberry Pi OS
# Settings → Display → Touchscreen
```

### Issue: Application Crashes on Start

**Debug:**
```bash
# Run with Python traceback
python3 main.py 2>&1 | tee error.log

# Check log file
cat logs/app.log

# Verify Python installation
python3 -c "import PyQt5, serial, sqlite3, reportlab; print('OK')"
```

## Performance Tuning

### Reduce Memory Usage

```python
# In config.py, reduce buffer sizes:
ECG_BUFFER_SIZE = 3000  # instead of 6000
```

### Reduce CPU Usage

```python
# In ui/ecg_test.py, increase update interval:
self.update_timer = QTimer()
self.update_timer.timeout.connect(self.update_display)
# Change from 1000ms to 2000ms for slower updates
```

## File Locations

```
/home/pi/SmartHealthHub/
├── data/app.db              # Patient database
├── reports/                 # Generated PDF reports
├── logs/app.log             # Application log
└── config.py                # User configuration
```

## Useful Commands

```bash
# View live logs
tail -f /home/pi/SmartHealthHub/logs/app.log

# Check disk space
df -h

# Check memory usage
free -h

# Run with profiling (advanced)
python3 -m cProfile -s cumulative main.py

# Start in background
nohup python3 main.py > app.out 2>&1 &

# Kill application
pkill -f "python3 main.py"
```

## Hardware Connections Checklist

- [ ] Arduino Mega connected via USB
- [ ] Pulse sensor wired to A0
- [ ] LM35 temperature sensor wired to A1
- [ ] Touch sensor wired to A2
- [ ] ECG module wired to A3 (output), D10 (LO+), D11 (LO-)
- [ ] SIM800L connected via USB (if using SMS)
- [ ] All sensors powered (5V and GND)
- [ ] 7-inch touchscreen connected and calibrated

## Next Steps After Setup

1. **Calibrate Sensors**
   - Run test with known reference temperature
   - Adjust TEMPERATURE_OFFSET in config.py

2. **Create Test Patient**
   - Use app to enter sample patient data
   - Verify database stores correctly

3. **Perform Full Test**
   - Place hand on sensor pad
   - Verify pulse and temperature readings
   - If ECG enabled, test with electrodes

4. **Generate Reports**
   - Create test and generate PDF
   - Check reports/ directory for output

5. **Test SMS (if enabled)**
   - Generate report with SMS option
   - Verify message received

## Support Resources

- **Logs:** `logs/app.log` - detailed application events
- **Database:** `data/app.db` - all patient records
- **Documentation:** `README.md` - complete guide
- **Arduino Code:** `arduino/sketch.ino` - sensor firmware
- **Source Code:** `main.py` and `ui/`, `sensors/`, etc. - implementation

---

For more detailed information, see README.md
