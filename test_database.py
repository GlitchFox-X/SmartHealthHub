#!/usr/bin/env python3
"""
Database layer testing on Windows.
Tests without requiring Arduino or Raspberry Pi hardware.
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from database.database import Database
from datetime import datetime


def test_patient_operations():
    """Test patient CRUD operations."""
    print("\n" + "="*60)
    print("TEST: Patient Operations")
    print("="*60)
    
    # Use temp test database
    test_db = Path(__file__).parent / "data" / "test_patients.db"
    test_db.parent.mkdir(exist_ok=True)
    if test_db.exists():
        test_db.unlink()
    
    db = Database(test_db)
    
    # Create patient
    patient_id = db.add_patient(
        name="John Doe",
        age=35,
        gender="Male",
        mobile="9876543210",
        address="123 Main Street, Springfield"
    )
    print(f"✓ Patient created: ID={patient_id}, Name=John Doe")
    assert patient_id is not None
    
    # Retrieve patient
    patient = db.get_patient(patient_id)
    print(f"✓ Patient retrieved: {patient['name']}, Age={patient['age']}")
    assert patient['name'] == "John Doe"
    assert patient['age'] == 35
    
    # Retrieve by mobile
    patient_by_mobile = db.get_patient_by_mobile("9876543210")
    print(f"✓ Patient found by mobile: {patient_by_mobile['name']}")
    assert patient_by_mobile['id'] == patient_id
    
    # Duplicate mobile should fail
    dup_id = db.add_patient(
        name="Jane Doe",
        age=30,
        gender="Female",
        mobile="9876543210",
        address="Same address"
    )
    print(f"✓ Duplicate mobile rejected: ID={dup_id}")
    assert dup_id is None
    
    print("\n✓ All patient tests PASSED\n")
    return test_db, db, patient_id


def test_test_operations(test_db, db, patient_id):
    """Test health test record operations."""
    print("="*60)
    print("TEST: Health Test Record Operations")
    print("="*60)
    
    # Create test record
    test_id = db.add_test(patient_id, "BASIC_ECG")
    print(f"✓ Test record created: ID={test_id}, Type=BASIC_ECG")
    assert test_id is not None
    
    # Add basic results
    pulse = 78
    temperature = 36.8
    bp = "Not Available"
    
    success = db.add_basic_result(test_id, pulse, temperature, bp)
    print(f"✓ Basic results stored: Pulse={pulse} BPM, Temp={temperature}°C, BP={bp}")
    assert success is True
    
    # Retrieve patient history
    history = db.get_patient_history(patient_id)
    print(f"✓ Patient history retrieved: {len(history)} test(s)")
    assert len(history) > 0
    assert history[0]['pulse'] == pulse
    assert history[0]['temperature'] == temperature
    
    print("\n✓ All test record tests PASSED\n")
    return test_id


def test_ecg_operations(db, test_id):
    """Test ECG data storage."""
    print("="*60)
    print("TEST: ECG Data Storage")
    print("="*60)
    
    # Simulate ECG samples
    sample_count = 100
    duration = 10.0
    lead_off = False
    raw_data = "[[0,512],[10,514],[20,513],...,[990,511]]"  # Simplified
    
    success = db.add_ecg_data(test_id, sample_count, duration, lead_off, raw_data)
    print(f"✓ ECG data stored: Samples={sample_count}, Duration={duration}s, Lead-off={lead_off}")
    assert success is True
    
    print("\n✓ All ECG tests PASSED\n")


def test_report_operations(db, test_id):
    """Test report metadata storage."""
    print("="*60)
    print("TEST: Report Generation & Storage")
    print("="*60)
    
    pdf_path = "/data/reports/report_test_20260831_120000.pdf"
    
    success = db.add_report(test_id, pdf_path)
    print(f"✓ Report metadata stored: {pdf_path}")
    assert success is True
    
    print("\n✓ All report tests PASSED\n")


def test_sms_logging(db, patient_id, test_id):
    """Test SMS logging."""
    print("="*60)
    print("TEST: SMS Logging")
    print("="*60)
    
    phone = "9876543210"
    status = "SENT"
    
    db.log_sms(patient_id, test_id, phone, status)
    print(f"✓ SMS logged: Phone={phone}, Status={status}")
    
    print("\n✓ All SMS logging tests PASSED\n")


def main():
    """Run all database tests."""
    print("\n" + "█"*60)
    print("█  SMART HEALTH HUB - DATABASE TESTS (Windows)")
    print("█"*60)
    
    try:
        test_db, db, patient_id = test_patient_operations()
        test_id = test_test_operations(test_db, db, patient_id)
        test_ecg_operations(db, test_id)
        test_report_operations(db, test_id)
        test_sms_logging(db, patient_id, test_id)
        
        print("█"*60)
        print("█  ✓ ALL DATABASE TESTS PASSED")
        print("█"*60 + "\n")
        
        # Cleanup
        if test_db.exists():
            test_db.unlink()
            print(f"Cleaned up test database: {test_db}\n")
        
        return 0
    
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
