"""
Arduino Serial Communication Manager

Handles all serial communication with Arduino Mega 2560.
Provides a clean interface for sending commands and receiving sensor data.
Runs in a separate thread to prevent GUI freezing.
"""

import json
import logging
import threading
import time
from collections import deque
from pathlib import Path
from typing import Optional, Callable, Dict, Any

import serial
from serial.tools import list_ports

from config import (
    ARDUINO_PORT,
    ARDUINO_BAUD,
    ARDUINO_TIMEOUT,
    OFFLINE_MODE,
)

logger = logging.getLogger(__name__)


class SerialManager:
    """Manages communication with Arduino via USB serial port."""
    
    def __init__(self, port: Optional[str] = None, baud: int = ARDUINO_BAUD):
        self.port = port or ARDUINO_PORT
        self.baud = baud
        self.serial_conn = None
        self.running = False
        self.reader_thread = None
        self.offline_mode = OFFLINE_MODE
        
        # Callbacks for received data
        self.on_status = None
        self.on_basic_result = None
        self.on_ecg_sample = None
        self.on_error = None
        
        # Data buffers
        self.status_queue = deque(maxlen=10)
        self.ecg_buffer = deque(maxlen=1000)
        
    def connect(self) -> bool:
        """Connect to Arduino over USB serial."""
        if self.offline_mode:
            logger.warning("Running in OFFLINE MODE - no Arduino connection")
            return True
            
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=ARDUINO_TIMEOUT
            )
            time.sleep(2)  # Wait for Arduino to initialize
            logger.info(f"Connected to Arduino on {self.port} at {self.baud} baud")
            
            # Start reader thread
            self.running = True
            self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.reader_thread.start()
            
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            self.offline_mode = True
            return False
    
    def disconnect(self):
        """Disconnect from Arduino."""
        self.running = False
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join(timeout=2)
        
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logger.info("Disconnected from Arduino")
    
    def send_command(self, command: str) -> bool:
        """Send a command to Arduino."""
        if self.offline_mode:
            logger.debug(f"OFFLINE: Would send command: {command}")
            return True
        
        if not self.serial_conn or not self.serial_conn.is_open:
            logger.error("Serial connection not open")
            return False
        
        try:
            self.serial_conn.write((command + "\n").encode('utf-8'))
            logger.debug(f"Sent command: {command}")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to send command: {e}")
            self.offline_mode = True
            return False
    
    def start_test(self) -> bool:
        """Start basic health test."""
        return self.send_command("START_TEST")
    
    def start_ecg(self) -> bool:
        """Start ECG recording."""
        return self.send_command("START_ECG")
    
    def stop_ecg(self) -> bool:
        """Stop ECG recording."""
        return self.send_command("STOP_ECG")
    
    def reset(self) -> bool:
        """Reset Arduino."""
        return self.send_command("RESET")
    
    def _read_loop(self):
        """Background thread that reads serial data from Arduino."""
        buffer = ""
        
        while self.running:
            try:
                if not self.serial_conn or not self.serial_conn.is_open:
                    break
                
                if self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.read(self.serial_conn.in_waiting).decode('utf-8')
                    buffer += data
                    
                    # Process complete lines
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        
                        if line:
                            self._process_line(line)
                else:
                    time.sleep(0.01)  # Small sleep to prevent CPU spinning
            
            except serial.SerialException as e:
                logger.error(f"Serial read error: {e}")
                self.offline_mode = True
                break
            except Exception as e:
                logger.error(f"Unexpected error in read loop: {e}")
                if self.on_error:
                    self.on_error(str(e))
    
    def _process_line(self, line: str):
        """Process a single line of data from Arduino."""
        try:
            # Parse JSON
            data = json.loads(line)
            msg_type = data.get("type")
            
            if msg_type == "status":
                self._handle_status(data)
            elif msg_type == "basic":
                self._handle_basic_result(data)
            elif msg_type == "ecg":
                self._handle_ecg_sample(data)
            else:
                logger.warning(f"Unknown message type: {msg_type}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {line} - Error: {e}")
            if self.on_error:
                self.on_error(f"Invalid serial data: {line}")
        except Exception as e:
            logger.error(f"Error processing line: {e}")
            if self.on_error:
                self.on_error(str(e))
    
    def _handle_status(self, data: Dict[str, Any]):
        """Handle status message from Arduino."""
        status = data.get("value")
        logger.debug(f"Arduino status: {status}")
        self.status_queue.append(status)
        
        if self.on_status:
            self.on_status(status)
    
    def _handle_basic_result(self, data: Dict[str, Any]):
        """Handle basic test results from Arduino."""
        logger.info(f"Received basic test results: {data}")
        
        if self.on_basic_result:
            self.on_basic_result(data)
    
    def _handle_ecg_sample(self, data: Dict[str, Any]):
        """Handle ECG sample from Arduino."""
        self.ecg_buffer.append(data)
        
        if self.on_ecg_sample:
            self.on_ecg_sample(data)
    
    def get_last_status(self) -> Optional[str]:
        """Get the most recent status message."""
        if self.status_queue:
            return self.status_queue[-1]
        return None
    
    def clear_ecg_buffer(self):
        """Clear ECG data buffer."""
        self.ecg_buffer.clear()
    
    def get_ecg_samples(self) -> list:
        """Get all buffered ECG samples."""
        return list(self.ecg_buffer)
    
    @staticmethod
    def list_available_ports() -> list:
        """List all available serial ports."""
        ports = []
        for port_info in list_ports.comports():
            ports.append({
                'port': port_info.device,
                'description': port_info.description,
            })
        return ports


# Singleton instance
_manager_instance = None


def get_serial_manager() -> SerialManager:
    """Get or create the serial manager singleton."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = SerialManager()
    return _manager_instance
