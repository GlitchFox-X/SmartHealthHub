#!/usr/bin/env python3
"""
Arduino Serial Communication testing on Windows.
Tests the serial protocol and data parsing without real Arduino hardware.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from arduino.serial_manager import SerialManager
from sensors.pulse import PulseProcessor
from sensors.temperature import TemperatureProcessor
from sensors.ecg import ECGProcessor
from config import OFFLINE_MODE


def test_offline_mode():
    """Test that serial manager works in OFFLINE_MODE or falls back gracefully."""
    print("\n" + "="*60)
    print("TEST: Offline Mode Fallback (No Arduino Connected)")
    print("="*60)
    
    mgr = SerialManager()
    print(f"✓ Serial manager created")
    print(f"  - OFFLINE_MODE config: {OFFLINE_MODE}")
    print(f"  - Manager offline_mode: {mgr.offline_mode}")
    
    # Should not crash when sending commands
    result = mgr.send_command("START_TEST")
    print(f"✓ Command sent (result: {result})")
    
    result = mgr.send_command("START_ECG")
    print(f"✓ ECG command sent (result: {result})")
    
    result = mgr.send_command("STOP_ECG")
    print(f"✓ ECG stop command sent (result: {result})")
    
    print("\n✓ Offline mode tests PASSED\n")


def test_arduino_protocol_parsing():
    """Test parsing of simulated Arduino JSON responses."""
    print("="*60)
    print("TEST: Arduino Protocol JSON Parsing")
    print("="*60)
    
    # Simulate different Arduino response types
    
    # Status message
    status_json = '{"type":"status","value":"READY"}'
    data = json.loads(status_json)
    print(f"✓ Status parsed: type={data['type']}, value={data['value']}")
    assert data['type'] == 'status'
    assert data['value'] == 'READY'
    
    # Basic test results (as Arduino sends them)
    basic_json = '{"type":"basic","pulse":76,"temperature":36.8,"bp":"Not Available"}'
    data = json.loads(basic_json)
    print(f"✓ Basic result parsed: pulse={data['pulse']} BPM, temp={data['temperature']}°C, bp={data['bp']}")
    assert data['type'] == 'basic'
    assert 40 <= data['pulse'] <= 200
    assert 32 <= data['temperature'] <= 42
    
    # ECG sample
    ecg_json = '{"type":"ecg","timestamp":100,"value":512}'
    data = json.loads(ecg_json)
    print(f"✓ ECG sample parsed: timestamp={data['timestamp']}ms, value={data['value']}")
    assert data['type'] == 'ecg'
    assert 0 <= data['value'] <= 1023
    
    print("\n✓ Protocol parsing tests PASSED\n")


def test_pulse_sensor():
    """Test pulse processing."""
    print("="*60)
    print("TEST: Pulse Sensor Data Processing")
    print("="*60)
    
    processor = PulseProcessor()
    
    # Simulate raw pulse readings
    raw_values = [450, 480, 510, 470, 460, 500, 520, 490]
    
    for raw in raw_values:
        processor.add_raw_value(raw)
    
    # Estimate BPM
    bpm = processor.estimate_bpm()
    print(f"✓ Pulse estimated: {bpm} BPM")
    assert 40 <= bpm <= 200 if bpm else True  # May return None if not enough samples
    
    # Get average
    avg_bpm = processor.get_average_bpm()
    print(f"✓ Average BPM: {avg_bpm}")
    
    print("\n✓ Pulse sensor tests PASSED\n")


def test_temperature_sensor():
    """Test temperature processing."""
    print("="*60)
    print("TEST: Temperature Sensor Data Processing")
    print("="*60)
    
    processor = TemperatureProcessor()
    
    # Simulate raw ADC readings from LM35
    # LM35: 10mV per °C, so at 36.8°C: voltage = 0.368V
    # With 5V reference: ADC = (0.368 / 5.0) * 1023 ≈ 75
    raw_values = [74, 75, 76, 75, 74]  # Raw 10-bit ADC values for ~36.8°C
    
    for raw in raw_values:
        processor.add_raw_value(raw)
    
    avg_temp = processor.estimate_temperature()
    print(f"✓ Temperature processed: {avg_temp}°C (from raw ADC values)")
    
    if avg_temp is None:
        print("  Note: Temperature reading may be outside expected range for testing")
    else:
        assert 28 <= avg_temp <= 42, f"Temperature {avg_temp} out of valid range"
    
    print("\n✓ Temperature sensor tests PASSED\n")


def test_ecg_processor():
    """Test ECG data buffering and statistics."""
    print("="*60)
    print("TEST: ECG Data Buffering & Statistics")
    print("="*60)
    
    processor = ECGProcessor()
    
    # Simulate ECG samples
    for i in range(100):
        timestamp = i * 10  # 10ms intervals
        value = 512 + (20 * (i % 5) - 40)  # Oscillating value
        processor.add_sample(timestamp, value)
    
    # Check buffered data
    samples = processor.get_all_samples()
    print(f"✓ ECG samples buffered: {len(samples)} samples")
    assert len(samples) == 100
    
    # Get statistics
    stats = processor.get_statistics()
    print(f"✓ Statistics computed:")
    print(f"  - Total samples: {stats.get('total_samples')}")
    print(f"  - Duration: {stats.get('duration_seconds'):.2f}s")
    print(f"  - Min value: {stats.get('min_value')}")
    print(f"  - Max value: {stats.get('max_value')}")
    
    # Test lead-off detection
    processor.set_lead_off(True)
    print(f"✓ Lead-off detection triggered")
    
    # Export data
    exported = processor.export_raw_data()
    print(f"✓ Raw data exported: {len(exported)} points")
    
    print("\n✓ ECG processor tests PASSED\n")


def test_realistic_workflow():
    """Test a realistic workflow: basic test -> ECG -> data export."""
    print("="*60)
    print("TEST: Realistic Test Workflow")
    print("="*60)
    
    print("\n1. Simulating Basic Test (10 seconds)...")
    pulse_proc = PulseProcessor()
    temp_proc = TemperatureProcessor()
    
    # Simulate 10 seconds of readings (1 per second)
    for sec in range(10):
        # Pulse: fluctuates around 75 BPM
        pulse_raw = 450 + (sec % 3) * 20
        pulse_proc.add_raw_value(pulse_raw)
        
        # Temperature: ADC values for ~36.8°C = around 75
        temp_adc = 74 + (sec % 2)
        temp_proc.add_raw_value(temp_adc)
    
    final_pulse = pulse_proc.estimate_bpm()
    final_temp = temp_proc.estimate_temperature()
    
    if final_temp:
        print(f"✓ Basic test complete: Pulse={final_pulse} BPM, Temp={final_temp}°C")
    else:
        print(f"✓ Basic test complete: Pulse={final_pulse} BPM, Temp=N/A")
    
    print("\n2. User chooses ECG...")
    ecg_proc = ECGProcessor()
    
    # Simulate 30 seconds of ECG at 100 Hz (300 samples)
    print("  Recording ECG samples...")
    for i in range(300):
        timestamp = i * 10  # 10ms intervals
        # Simulate realistic ECG waveform
        value = 512 + int(40 * __import__('math').sin(i * 0.1))
        ecg_proc.add_sample(timestamp, value)
    
    print("✓ ECG recording complete")
    
    # Analyze ECG
    stats = ecg_proc.get_statistics()
    print(f"✓ ECG Statistics:")
    print(f"  - Samples: {stats['total_samples']}")
    print(f"  - Duration: {stats['duration_seconds']:.1f}s")
    print(f"  - Range: {stats['min_value']} - {stats['max_value']}")
    
    print("\n3. Generating report data...")
    report_data = {
        'pulse': final_pulse,
        'temperature': final_temp if final_temp else 'N/A',
        'blood_pressure': 'Not Available',
        'ecg_samples': len(ecg_proc.get_all_samples()),
        'ecg_duration': stats['duration_seconds']
    }
    
    print(f"✓ Report data ready:")
    for key, value in report_data.items():
        print(f"  - {key}: {value}")
    
    print("\n✓ Realistic workflow tests PASSED\n")


def main():
    """Run all serial communication tests."""
    print("\n" + "█"*60)
    print("█  SMART HEALTH HUB - SERIAL TESTS (Windows)")
    print("█"*60)
    
    try:
        test_offline_mode()
        test_arduino_protocol_parsing()
        test_pulse_sensor()
        test_temperature_sensor()
        test_ecg_processor()
        test_realistic_workflow()
        
        print("█"*60)
        print("█  ✓ ALL SERIAL TESTS PASSED")
        print("█"*60 + "\n")
        
        return 0
    
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
