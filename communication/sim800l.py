"""
SIM800L SMS Communication Module

Handles SMS sending via SIM800L GSM modem.
Runs in a separate thread to keep GUI responsive.
"""

import logging
import threading
import time
from typing import Optional, Callable

import serial

from config import SIM800L_PORT, SIM800L_BAUD, SIM800L_TIMEOUT, SMS_ENABLED, SMS_TEMPLATE

logger = logging.getLogger(__name__)


class SIM800LManager:
    """Manages communication with SIM800L GSM modem for SMS."""
    
    def __init__(self, port: str = SIM800L_PORT, baud: int = SIM800L_BAUD):
        self.port = port
        self.baud = baud
        self.timeout = SIM800L_TIMEOUT
        self.serial_conn = None
        self.enabled = SMS_ENABLED
        
        # Callbacks
        self.on_sms_sent = None
        self.on_sms_failed = None
        
    def connect(self) -> bool:
        """Connect to SIM800L modem."""
        if not self.enabled:
            logger.info("SMS disabled in configuration")
            return True
        
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=self.timeout
            )
            time.sleep(1)
            
            # Initialize modem
            if not self._send_at_command("AT"):
                logger.error("No response from SIM800L")
                self.serial_conn.close()
                return False
            
            # Check SIM status
            if not self._send_at_command("AT+CPIN?"):
                logger.warning("Could not verify SIM status")
            
            logger.info(f"Connected to SIM800L on {self.port}")
            return True
        
        except serial.SerialException as e:
            logger.error(f"Failed to connect to SIM800L: {e}")
            self.enabled = False
            return False
    
    def disconnect(self):
        """Disconnect from SIM800L."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logger.info("Disconnected from SIM800L")
    
    def _send_at_command(self, command: str, wait_time: float = 1.0) -> bool:
        """Send AT command to SIM800L and wait for response."""
        if not self.serial_conn or not self.serial_conn.is_open:
            return False
        
        try:
            # Send command
            self.serial_conn.write((command + "\r\n").encode('utf-8'))
            self.serial_conn.flush()
            
            # Wait for response
            time.sleep(wait_time)
            
            # Read response
            response = ""
            while self.serial_conn.in_waiting > 0:
                response += self.serial_conn.read(1).decode('utf-8', errors='ignore')
            
            # Check for OK response
            return "OK" in response or "READY" in response
        
        except Exception as e:
            logger.error(f"AT command failed: {e}")
            return False
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        """
        Send SMS message.
        
        Args:
            phone_number: Recipient phone number
            message: SMS message text
            
        Returns:
            True if SMS appears to be sent, False otherwise
        """
        if not self.enabled or not self.serial_conn or not self.serial_conn.is_open:
            logger.warning("SMS not available")
            return False
        
        try:
            # Set text mode
            self._send_at_command("AT+CMGF=1")
            
            # Set recipient
            cmd = f'AT+CMGS="{phone_number}"'
            self.serial_conn.write((cmd + "\r").encode('utf-8'))
            self.serial_conn.flush()
            
            # Wait for prompt
            time.sleep(0.5)
            
            # Send message
            self.serial_conn.write(message.encode('utf-8'))
            self.serial_conn.write(b"\x1a")  # Ctrl+Z to send
            self.serial_conn.flush()
            
            # Wait for response
            time.sleep(2)
            
            response = ""
            while self.serial_conn.in_waiting > 0:
                response += self.serial_conn.read(1).decode('utf-8', errors='ignore')
            
            success = "+CMGS:" in response or "OK" in response
            
            if success:
                logger.info(f"SMS sent to {phone_number}")
                if self.on_sms_sent:
                    self.on_sms_sent(phone_number)
            else:
                logger.error(f"SMS send failed for {phone_number}")
                if self.on_sms_failed:
                    self.on_sms_failed(phone_number, "No confirmation from modem")
            
            return success
        
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            if self.on_sms_failed:
                self.on_sms_failed(phone_number, str(e))
            return False
    
    def send_sms_async(self, phone_number: str, message: str):
        """Send SMS in a background thread."""
        thread = threading.Thread(
            target=self.send_sms,
            args=(phone_number, message),
            daemon=True
        )
        thread.start()


class SMSManager:
    """High-level SMS management for health reports."""
    
    def __init__(self):
        self.sim800l = SIM800LManager()
        self.last_status = None
        
    def connect(self) -> bool:
        """Connect to SIM800L."""
        return self.sim800l.connect()
    
    def disconnect(self):
        """Disconnect from SIM800L."""
        self.sim800l.disconnect()
    
    def send_health_report(self, phone_number: str, patient_data: dict, 
                          test_results: dict) -> bool:
        """
        Send a formatted health report SMS.
        
        Args:
            phone_number: Patient's phone number
            patient_data: Dictionary with patient info (name, age, gender, etc.)
            test_results: Dictionary with test results (pulse, temperature, bp, ecg)
            
        Returns:
            True if SMS was sent successfully
        """
        try:
            # Format the SMS message
            message = SMS_TEMPLATE.format(
                name=patient_data.get('name', 'N/A'),
                age=patient_data.get('age', 'N/A'),
                gender=patient_data.get('gender', 'N/A'),
                address=patient_data.get('address', 'N/A'),
                mobile=patient_data.get('mobile', 'N/A'),
                doctor=patient_data.get('doctor_name', 'N/A'),
                pulse=test_results.get('pulse', 'N/A'),
                temperature=test_results.get('temperature', 'N/A'),
                bp=test_results.get('blood_pressure', 'Not Available'),
                ecg=test_results.get('ecg_status', 'Not performed'),
                issues=test_results.get('issues', 'None'),
                emergency=test_results.get('emergency', 'No'),
            )
            
            # Truncate message if too long (SMS limit is typically 160 chars, 
            # but we'll allow up to 300 for this report)
            if len(message) > 300:
                logger.warning(f"SMS message truncated from {len(message)} to 300 chars")
                message = message[:297] + "..."
            
            logger.info(f"Sending health report SMS to {phone_number}")
            success = self.sim800l.send_sms(phone_number, message)
            self.last_status = "SENT" if success else "FAILED"
            return success
        
        except Exception as e:
            logger.error(f"Error sending health report: {e}")
            self.last_status = "ERROR"
            return False
    
    def set_callbacks(self, on_sent: Callable = None, on_failed: Callable = None):
        """Set callbacks for SMS events."""
        if on_sent:
            self.sim800l.on_sms_sent = on_sent
        if on_failed:
            self.sim800l.on_sms_failed = on_failed
    
    def get_status(self) -> str:
        """Get last SMS status."""
        return self.last_status or "IDLE"


# Singleton instance
_sms_manager = None


def get_sms_manager() -> SMSManager:
    """Get or create SMS manager singleton."""
    global _sms_manager
    if _sms_manager is None:
        _sms_manager = SMSManager()
    return _sms_manager
