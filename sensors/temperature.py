"""
Temperature Sensor Data Processing

Handles LM35 temperature sensor data from Arduino.
Converts raw ADC values to Celsius.
"""

import logging
from collections import deque
from typing import Optional

from config import TEMPERATURE_OFFSET, TEMPERATURE_MULTIPLIER

logger = logging.getLogger(__name__)


class TemperatureProcessor:
    """Process temperature sensor data from LM35."""
    
    # LM35 characteristics
    # Output: 10mV per °C
    # At 0°C: 0V
    # At 50°C: 0.5V
    # At 100°C: 1.0V (if using full range, but typically 0-50°C is used)
    
    # For Arduino with 5V reference and 10-bit ADC:
    # 1023 ADC units = 5V
    # 0 ADC units = 0V
    # So approximately: ADC * (5.0 / 1023) * 100 = Temperature in Celsius
    
    def __init__(self, buffer_size: int = 100):
        self.buffer_size = buffer_size
        self.raw_values = deque(maxlen=buffer_size)
        self.temperature_history = deque(maxlen=10)
        
    def add_raw_value(self, raw_adc: int):
        """Add a raw ADC reading from LM35."""
        if not isinstance(raw_adc, int) or raw_adc < 0 or raw_adc > 1023:
            logger.warning(f"Invalid temperature ADC value: {raw_adc}")
            return
        
        self.raw_values.append(raw_adc)
    
    def convert_to_celsius(self, raw_adc: int) -> float:
        """Convert raw ADC value to Celsius."""
        # Formula: Temperature = (ADC * 5.0 / 1023) * 100
        # The 5.0 is the reference voltage, 1023 is max ADC value
        # The factor of 100 converts from volts to celsius (10mV per °C)
        temperature = (raw_adc / 1023.0) * 5.0 * 100
        
        # Apply calibration offset and multiplier
        temperature = temperature * TEMPERATURE_MULTIPLIER + TEMPERATURE_OFFSET
        
        return temperature
    
    def estimate_temperature(self) -> Optional[float]:
        """Estimate current temperature from buffered readings."""
        if len(self.raw_values) == 0:
            return None
        
        # Calculate average of raw values
        avg_raw = sum(self.raw_values) / len(self.raw_values)
        
        # Convert to Celsius
        temperature = self.convert_to_celsius(int(avg_raw))
        
        # Validate reasonable range (28°C to 42°C for human body)
        if 28 <= temperature <= 42:
            self.temperature_history.append(temperature)
            return round(temperature, 1)
        else:
            logger.warning(f"Out of range temperature: {temperature}°C")
            return None
    
    def get_average_temperature(self) -> Optional[float]:
        """Get average temperature from history."""
        if not self.temperature_history:
            return None
        avg = sum(self.temperature_history) / len(self.temperature_history)
        return round(avg, 1)
    
    def clear(self):
        """Clear all buffers."""
        self.raw_values.clear()
        self.temperature_history.clear()
    
    def get_statistics(self) -> dict:
        """Get temperature statistics."""
        if not self.temperature_history:
            return {
                "count": 0,
                "current": None,
                "average": None,
                "min": None,
                "max": None,
            }
        
        values = list(self.temperature_history)
        return {
            "count": len(values),
            "current": values[-1] if values else None,
            "average": round(sum(values) / len(values), 1),
            "min": round(min(values), 1),
            "max": round(max(values), 1),
        }
