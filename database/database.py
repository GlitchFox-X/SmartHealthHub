"""
SQLite Database Module

Stores patient information, test results, and report metadata.
"""

import logging
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from config import DATABASE_PATH

logger = logging.getLogger(__name__)


class Database:
    """SQLite database for Smart Health Hub."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DATABASE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Patients table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        age INTEGER,
                        gender TEXT,
                        mobile TEXT UNIQUE NOT NULL,
                        address TEXT,
                        doctor_name TEXT,
                        doctor_phone TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tests table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_id INTEGER NOT NULL,
                        test_type TEXT NOT NULL,
                        test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'COMPLETED',
                        FOREIGN KEY (patient_id) REFERENCES patients(id)
                    )
                """)
                
                # Basic test results
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS basic_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        test_id INTEGER NOT NULL,
                        pulse INTEGER,
                        temperature REAL,
                        blood_pressure TEXT,
                        FOREIGN KEY (test_id) REFERENCES tests(id)
                    )
                """)
                
                # ECG data
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ecg_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        test_id INTEGER NOT NULL,
                        sample_count INTEGER,
                        duration_seconds REAL,
                        lead_off_detected INTEGER,
                        raw_data TEXT,
                        FOREIGN KEY (test_id) REFERENCES tests(id)
                    )
                """)
                
                # Reports
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        test_id INTEGER NOT NULL,
                        pdf_path TEXT,
                        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (test_id) REFERENCES tests(id)
                    )
                """)
                
                # SMS status
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sms_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_id INTEGER NOT NULL,
                        test_id INTEGER NOT NULL,
                        phone_number TEXT,
                        status TEXT,
                        sent_at TIMESTAMP,
                        FOREIGN KEY (patient_id) REFERENCES patients(id),
                        FOREIGN KEY (test_id) REFERENCES tests(id)
                    )
                """)
                
                conn.commit()
                logger.info(f"Database initialized at {self.db_path}")
        
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def add_patient(self, name: str, age: int, gender: str, mobile: str,
                   address: str, doctor_name: str = None, doctor_phone: str = None) -> Optional[int]:
        """Add a new patient. Returns patient ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO patients 
                    (name, age, gender, mobile, address, doctor_name, doctor_phone)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, age, gender, mobile, address, doctor_name, doctor_phone))
                conn.commit()
                
                patient_id = cursor.lastrowid
                logger.info(f"Patient added: {name} (ID: {patient_id})")
                return patient_id
        
        except sqlite3.IntegrityError as e:
            logger.error(f"Patient with mobile {mobile} already exists")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding patient: {e}")
            return None
    
    def get_patient(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve patient information."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error retrieving patient: {e}")
            return None
    
    def get_patient_by_mobile(self, mobile: str) -> Optional[Dict[str, Any]]:
        """Retrieve patient by mobile number."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients WHERE mobile = ?", (mobile,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error retrieving patient: {e}")
            return None
    
    def add_test(self, patient_id: int, test_type: str) -> Optional[int]:
        """Add a new test record. Returns test ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tests (patient_id, test_type)
                    VALUES (?, ?)
                """, (patient_id, test_type))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding test: {e}")
            return None
    
    def add_basic_result(self, test_id: int, pulse: int, temperature: float, 
                        blood_pressure: str) -> bool:
        """Store basic test results."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO basic_results (test_id, pulse, temperature, blood_pressure)
                    VALUES (?, ?, ?, ?)
                """, (test_id, pulse, temperature, blood_pressure))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error storing basic results: {e}")
            return False
    
    def add_ecg_data(self, test_id: int, sample_count: int, duration_seconds: float,
                    lead_off_detected: bool, raw_data: str) -> bool:
        """Store ECG data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ecg_data 
                    (test_id, sample_count, duration_seconds, lead_off_detected, raw_data)
                    VALUES (?, ?, ?, ?, ?)
                """, (test_id, sample_count, duration_seconds, int(lead_off_detected), raw_data))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error storing ECG data: {e}")
            return False
    
    def add_report(self, test_id: int, pdf_path: str) -> bool:
        """Store report metadata."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO reports (test_id, pdf_path)
                    VALUES (?, ?)
                """, (test_id, pdf_path))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error storing report: {e}")
            return False
    
    def log_sms(self, patient_id: int, test_id: int, phone_number: str, status: str):
        """Log SMS sending attempt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sms_logs (patient_id, test_id, phone_number, status, sent_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (patient_id, test_id, phone_number, status))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error logging SMS: {e}")
    
    def get_patient_history(self, patient_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get patient's test history."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT t.*, b.pulse, b.temperature, b.blood_pressure
                    FROM tests t
                    LEFT JOIN basic_results b ON t.id = b.test_id
                    WHERE t.patient_id = ?
                    ORDER BY t.test_date DESC
                    LIMIT ?
                """, (patient_id, limit))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving patient history: {e}")
            return []
    
    def close(self):
        """Close database connection."""
        pass  # SQLite connections are closed automatically


# Singleton instance
_db_instance = None


def get_database() -> Database:
    """Get or create the database singleton."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
