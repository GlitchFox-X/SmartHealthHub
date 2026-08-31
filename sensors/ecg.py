"""
ECG Sensor Data Processing

Handles AD8232 ECG sensor data from Arduino.
Collects raw ECG samples for display and analysis.
"""

import logging
from collections import deque
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ECGSample:
    """Represents a single ECG sample."""
    timestamp: int  # milliseconds since ECG start
    value: int      # Raw ADC value (0-1023)


class ECGProcessor:
    """Process ECG sensor data from AD8232."""
    
    # AD8232 specifications
    # Output range: 0-3.3V (or 0-5V depending on configuration)
    # This maps to 0-1023 on Arduino 10-bit ADC
    # Lead-off detection: LO+ and LO- pins
    
    def __init__(self, sample_rate_hz: int = 100):
        """
        Initialize ECG processor.
        
        Args:
            sample_rate_hz: Expected sample rate in Hz (default 100 Hz = 10ms intervals)
        """
        self.sample_rate_hz = sample_rate_hz
        self.sample_interval_ms = 1000 // sample_rate_hz
        
        self.samples = deque(maxlen=6000)  # 60 seconds at 100 Hz
        self.lead_off_detected = False
        self.recording_start_time = None
        
    def add_sample(self, timestamp_ms: int, raw_value: int):
        """
        Add a raw ECG sample.
        
        Args:
            timestamp_ms: Milliseconds since ECG recording started
            raw_value: Raw ADC value (0-1023)
        """
        if not isinstance(raw_value, int) or raw_value < 0 or raw_value > 1023:
            logger.warning(f"Invalid ECG value: {raw_value}")
            return
        
        sample = ECGSample(timestamp=timestamp_ms, value=raw_value)
        self.samples.append(sample)
    
    def set_lead_off(self, detected: bool):
        """Set lead-off detection status."""
        if detected and not self.lead_off_detected:
            logger.warning("ECG lead-off detected!")
        self.lead_off_detected = detected
    
    def is_lead_off(self) -> bool:
        """Check if electrode lead-off is detected."""
        return self.lead_off_detected
    
    def get_all_samples(self) -> List[ECGSample]:
        """Get all recorded samples."""
        return list(self.samples)
    
    def get_samples_as_list(self) -> List[tuple]:
        """Get samples as list of (timestamp, value) tuples."""
        return [(s.timestamp, s.value) for s in self.samples]
    
    def get_latest_samples(self, count: int = 100) -> List[ECGSample]:
        """Get the most recent N samples."""
        if count <= 0:
            return []
        return list(self.samples)[-count:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get ECG statistics."""
        if not self.samples:
            return {
                "total_samples": 0,
                "duration_seconds": 0,
                "min_value": None,
                "max_value": None,
                "average_value": None,
                "lead_off": self.lead_off_detected,
            }
        
        values = [s.value for s in self.samples]
        duration = self.samples[-1].timestamp / 1000.0 if self.samples else 0
        
        return {
            "total_samples": len(values),
            "duration_seconds": round(duration, 2),
            "min_value": min(values),
            "max_value": max(values),
            "average_value": int(sum(values) / len(values)),
            "lead_off": self.lead_off_detected,
        }
    
    def clear(self):
        """Clear all recorded samples."""
        self.samples.clear()
        self.lead_off_detected = False
        self.recording_start_time = None
    
    def detect_abnormalities(self) -> Dict[str, Any]:
        """
        Detect basic ECG abnormalities.
        Note: This is NOT a medical diagnosis tool.
        Real ECG analysis requires professional interpretation.
        
        Returns:
            Dictionary with detected conditions (for informational purposes only)
        """
        if not self.samples:
            return {"issues": []}
        
        issues = []
        
        # Check for lead-off
        if self.lead_off_detected:
            issues.append("Electrode lead-off detected")
        
        # Check for extremely low signal
        values = [s.value for s in self.samples]
        avg_value = sum(values) / len(values)
        
        if avg_value < 50:
            issues.append("Very weak ECG signal")
        
        # Check for saturation
        if any(v >= 1000 for v in values):
            issues.append("Signal saturation detected")
        
        return {
            "total_samples": len(values),
            "issues": issues,
            "requires_review": len(issues) > 0,
        }
    
    def export_raw_data(self) -> List[Dict[str, int]]:
        """Export raw ECG data as list of dictionaries."""
        return [
            {"timestamp_ms": s.timestamp, "value": s.value}
            for s in self.samples
        ]
