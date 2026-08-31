#!/usr/bin/env python3
"""
PDF Report Generation testing on Windows.
Tests PDF output without requiring Arduino or real sensor data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from reports.pdf_generator import generate_health_report


def test_basic_report():
    """Test basic PDF report generation."""
    print("\n" + "="*60)
    print("TEST: Basic Health Report PDF")
    print("="*60)
    
    patient_data = {
        "name": "John Smith",
        "age": 45,
        "gender": "Male",
        "mobile": "9876543210",
        "address": "123 Main Street, Springfield, IL 62701",
        "doctor_name": "Dr. Emily Johnson",
        "doctor_phone": "2175551234"
    }
    
    test_results = {
        "pulse": 72,
        "temperature": 36.8,
        "blood_pressure": "Not Available",
        "pulse_status": "Normal",
        "temperature_status": "Normal",
        "timestamp": "2026-08-31T14:30:00",
        "emergency": False
    }
    
    ecg_results = {
        "total_samples": 1000,
        "duration_seconds": 30.5,
        "lead_off_detected": False,
        "issues": []
    }
    
    pdf_path = generate_health_report(patient_data, test_results, ecg_results)
    
    if pdf_path and Path(pdf_path).exists():
        file_size = Path(pdf_path).stat().st_size
        print(f"✓ PDF generated successfully")
        print(f"  Path: {pdf_path}")
        print(f"  Size: {file_size} bytes")
        return True
    else:
        print(f"✗ PDF generation failed")
        return False


def test_report_without_ecg():
    """Test report generation without ECG data."""
    print("\n" + "="*60)
    print("TEST: Report Without ECG Data")
    print("="*60)
    
    patient_data = {
        "name": "Jane Doe",
        "age": 28,
        "gender": "Female",
        "mobile": "5551234567",
        "address": "456 Oak Avenue, Chicago, IL 60601"
    }
    
    test_results = {
        "pulse": 68,
        "temperature": 37.1,
        "blood_pressure": "Not Available",
        "pulse_status": "Normal",
        "temperature_status": "Normal",
        "timestamp": "2026-08-31T15:45:00",
        "emergency": False
    }
    
    # No ECG data this time
    pdf_path = generate_health_report(patient_data, test_results, None)
    
    if pdf_path and Path(pdf_path).exists():
        file_size = Path(pdf_path).stat().st_size
        print(f"✓ PDF generated without ECG")
        print(f"  Path: {pdf_path}")
        print(f"  Size: {file_size} bytes")
        return True
    else:
        print(f"✗ PDF generation failed")
        return False


def test_report_with_abnormalities():
    """Test report with warning/critical readings."""
    print("\n" + "="*60)
    print("TEST: Report With Abnormal Readings")
    print("="*60)
    
    patient_data = {
        "name": "Robert Johnson",
        "age": 62,
        "gender": "Male",
        "mobile": "3125551234",
        "address": "789 Maple Drive, Houston, TX 77001"
    }
    
    test_results = {
        "pulse": 125,  # Warning range
        "temperature": 38.9,  # Warning range
        "blood_pressure": "Not Available",
        "pulse_status": "Warning",
        "temperature_status": "Warning",
        "timestamp": "2026-08-31T16:00:00",
        "emergency": False
    }
    
    ecg_results = {
        "total_samples": 1200,
        "duration_seconds": 45.0,
        "lead_off_detected": False,
        "issues": ["Possible arrhythmia detected"]
    }
    
    pdf_path = generate_health_report(patient_data, test_results, ecg_results)
    
    if pdf_path and Path(pdf_path).exists():
        file_size = Path(pdf_path).stat().st_size
        print(f"✓ Report with warnings generated")
        print(f"  Path: {pdf_path}")
        print(f"  Size: {file_size} bytes")
        return True
    else:
        print(f"✗ PDF generation failed")
        return False


def main():
    """Run all PDF tests."""
    print("\n" + "█"*60)
    print("█  SMART HEALTH HUB - PDF GENERATION TESTS (Windows)")
    print("█"*60)
    
    results = []
    
    try:
        results.append(("Basic Report", test_basic_report()))
        results.append(("Report Without ECG", test_report_without_ecg()))
        results.append(("Report With Abnormalities", test_report_with_abnormalities()))
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {name}")
        
        print("="*60)
        print(f"\nResult: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n█"*60)
            print("█  ✓ ALL PDF TESTS PASSED")
            print("█"*60 + "\n")
            return 0
        else:
            print("\n█"*60)
            print("█  ✗ SOME TESTS FAILED")
            print("█"*60 + "\n")
            return 1
    
    except Exception as e:
        print(f"\n✗ TEST SUITE FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
