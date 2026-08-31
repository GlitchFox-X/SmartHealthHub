"""
Pulse Sensor Data Processing

Handles pulse sensor data from Arduino.
Converts raw sensor readings to BPM (beats per minute).
"""

import logging
from collections import deque
from typing import Optional, List

logger = logging.getLogger(__name__)


class PulseProcessor:
    """Process pulse sensor data and estimate heart rate."""
    
    # Calibration constants (may need adjustment based on specific sensor)
    MIN_RAW_VALUE = 100
    MAX_RAW_VALUE = 600
    MIN_BPM = 40
    MAX_BPM = 200
    
    def __init__(self, buffer_size: int = 100):
        self.buffer_size = buffer_size
        self.raw_values = deque(maxlen=buffer_size)
        self.pulse_history = deque(maxlen=10)
        
    def add_raw_value(self, raw_value: int):
        """Add a raw pulse sensor reading."""
        if not isinstance(raw_value, int) or raw_value < 0 or raw_value > 1023:
            logger.warning(f"Invalid pulse value: {raw_value}")
            return
        
        self.raw_values.append(raw_value)
    
    def estimate_bpm(self) -> Optional[int]:
        """Estimate heart rate from buffered raw values."""
        if len(self.raw_values) == 0:
            return None
        
        # Calculate average
        avg_raw = sum(self.raw_values) / len(self.raw_values)
        
        # Map to BPM range
        bpm = self._map_raw_to_bpm(avg_raw)
        
        # Validate against reasonable ranges
        if self.MIN_BPM <= bpm <= self.MAX_BPM:
            self.pulse_history.append(bpm)
            return int(bpm)
        else:
            logger.warning(f"Out of range pulse: {bpm} BPM")
            return None
    
    def _map_raw_to_bpm(self, raw_value: float) -> int:
        """Map raw sensor value to estimated BPM."""
        # Linear mapping from raw to BPM
        if raw_value <= self.MIN_RAW_VALUE:
            return self.MIN_BPM
        elif raw_value >= self.MAX_RAW_VALUE:
            return self.MAX_BPM
        else:
            ratio = (raw_value - self.MIN_RAW_VALUE) / (self.MAX_RAW_VALUE - self.MIN_RAW_VALUE)
            return int(self.MIN_BPM + ratio * (self.MAX_BPM - self.MIN_BPM))
    
    def get_average_bpm(self) -> Optional[int]:
        """Get average BPM from history."""
        if not self.pulse_history:
            return None
        return int(sum(self.pulse_history) / len(self.pulse_history))
    
    def clear(self):
        """Clear all buffers."""
        self.raw_values.clear()
        self.pulse_history.clear()
    
    def get_statistics(self) -> dict:
        """Get pulse statistics."""
        if not self.pulse_history:
            return {
                "count": 0,
                "current": None,
                "average": None,
                "min": None,
                "max": None,
            }
        
        values = list(self.pulse_history)
        return {
            "count": len(values),
            "current": values[-1] if values else None,
            "average": int(sum(values) / len(values)),
            "min": min(values),
            "max": max(values),
        }
