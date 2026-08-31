# Smart Health Hub - Windows Testing Guide

## Quick Start

### Run All Tests
```powershell
cd c:\Users\Root_PC\Downloads\SHHAK
python run_tests.py
```

### Run Individual Tests

**Database Tests** (Patient data, test records, ECG storage)
```powershell
python test_database.py
```

**PDF Generation Tests** (Report creation with various scenarios)
```powershell
python test_pdf.py
```

**Serial Communication Tests** (Arduino protocol, sensor processing)
```powershell
python test_serial.py
```

---

## What Each Test Suite Covers

### test_database.py
- ✓ Patient creation and retrieval
- ✓ Duplicate mobile detection (prevents duplicates)
- ✓ Test record creation
- ✓ Basic result storage
- ✓ Patient history retrieval
- ✓ ECG data storage
- ✓ Report metadata tracking
- ✓ SMS logging

**Expected Output:** ~10 test checks, creates/deletes temporary test database

### test_pdf.py
- ✓ Basic health report generation
- ✓ Report without ECG data
- ✓ Report with warning/critical readings
- ✓ PDF file validation (file size > 0)
- ✓ All required fields present

**Expected Output:** 3 PDF files created in `reports/` directory (you can open and inspect them)

### test_serial.py
- ✓ Offline mode operation (no Arduino required)
- ✓ Arduino JSON protocol parsing (status, basic results, ECG samples)
- ✓ Pulse sensor data processing
- ✓ Temperature sensor data processing
- ✓ ECG buffering and statistics
- ✓ Lead-off detection
- ✓ Realistic 10-second basic test simulation
- ✓ Realistic 30-second ECG simulation

**Expected Output:** Protocol validation, sensor calculations

---

## Test Results Interpretation

### ✓ PASS
- All tests passed
- Code is syntactically correct
- Logic flow works as expected
- Safe to proceed with hardware testing

### ✗ FAIL
- Indicates a bug in the code
- Review the error message
- Check traceback for line number
- Fix the issue and re-run

---

## Generated Files During Testing

These files are created during tests and can be inspected:

- `data/test_patients.db` → Created and deleted automatically
- `reports/report_*.pdf` → Generated PDF files (inspect these in Adobe Reader)
- `logs/app.log` → Application log file

---

## Next Steps

1. **Run the full test suite:**
   ```powershell
   python run_tests.py
   ```

2. **If all tests pass:** Application is ready for hardware deployment

3. **If any test fails:** 
   - Read the error message carefully
   - Check the line number in the traceback
   - Fix the issue
   - Re-run tests

4. **Hardware Testing (when ready):**
   - Deploy to Raspberry Pi
   - Connect Arduino Mega 2560
   - Run the application with real sensors
   - Verify all readings are real (not simulated)

---

## Important Notes

- These tests run WITHOUT Arduino hardware
- They use OFFLINE_MODE (simulated Arduino responses)
- The tests do NOT generate fake sensor data
- PDF files can be opened with any PDF reader to verify content
- Database tests create temporary files that are cleaned up automatically

---

## Windows-Specific Issues

If you encounter these errors, try these solutions:

**"ModuleNotFoundError: No module named..."**
```powershell
python -m pip install -r requirements.txt
```

**"Cannot create Qt application" (GUI error)**
```powershell
# Use offscreen mode
$env:QT_QPA_PLATFORM='offscreen'
python test_serial.py
```

**"Permission denied" on database**
- Close any database viewers
- The test database is temporary and auto-deleted

---

## Test Coverage

| Component | Test File | Status |
|-----------|-----------|--------|
| Database Schema | test_database.py | ✓ Covered |
| Patient CRUD | test_database.py | ✓ Covered |
| PDF Generation | test_pdf.py | ✓ Covered |
| Arduino Protocol | test_serial.py | ✓ Covered |
| Pulse Processing | test_serial.py | ✓ Covered |
| Temperature Processing | test_serial.py | ✓ Covered |
| ECG Buffering | test_serial.py | ✓ Covered |
| GUI Startup | (Import test) | ✓ Passed |
| Real Hardware | (Requires Raspberry Pi + Arduino) | ⏳ Pending |

---

## Questions?

Check the following files for more details:
- `README.md` - Project overview
- `DEPLOYMENT.md` - Deployment instructions
- `config.py` - Configuration settings
- `main.py` - Application entry point
