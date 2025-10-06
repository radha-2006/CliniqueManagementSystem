import os # FIX: Added missing import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.db import db # Import the mocked database interface

# Load environment variables for MOCK_DOCTOR_EMAIL
from dotenv import load_dotenv
load_dotenv()


class QueueLogic:
    """Encapsulates the core business logic for the queue and tokens."""

    def __init__(self):
        # We assume a single mock doctor for simplicity in this demo.
        mock_doctor_email = os.getenv("MOCK_DOCTOR_EMAIL")
        
        if not mock_doctor_email:
             raise EnvironmentError("MOCK_DOCTOR_EMAIL environment variable not found. Check your .env file.")

        doctor_user = db.get_user_by_email(mock_doctor_email)
        
        if not doctor_user:
             raise ValueError(f"Mock doctor user with email '{mock_doctor_email}' not found in mock DB. Ensure db.py initialized correctly.")

        self.mock_doctor_id = doctor_user['user_id']


    def get_available_doctor(self) -> Optional[str]:
        """
        Simulates finding an available doctor.
        For this mock, we return the single mock doctor ID.
        """
        return self.mock_doctor_id

    def generate_token(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Generates a new token for a patient.
        """
        doctor_id = self.get_available_doctor()
        if not doctor_id:
            return None # No doctor available

        # Simple token number generation: T-ID-HHMMSS (Token-DoctorID-Time)
        timestamp = datetime.now().strftime("%H%M%S")
        token_number = f"T-{doctor_id}-{timestamp}"

        token = db.add_token(patient_id, doctor_id, token_number)
        return token

    def get_queue_status(self) -> List[Dict[str, Any]]:
        """
        Fetches the current live queue (waiting and serving) for the mock doctor.
        """
        return db.get_live_queue(self.mock_doctor_id)

    def call_next_patient(self) -> Optional[Dict[str, Any]]:
        """
        Updates the status of the first 'waiting' token to 'serving'.
        """
        queue = self.get_queue_status()

        # 1. Check if a patient is currently being served
        currently_serving = next((t for t in queue if t['status'] == 'serving'), None)
        if currently_serving:
            # Cannot call next until current patient is marked done/skipped
            return {"error": "A patient is currently being served. Mark them as 'done' or 'skipped' first.", "token": currently_serving}

        # 2. Find the next waiting patient
        next_waiting = next((t for t in queue if t['status'] == 'waiting'), None)

        if not next_waiting:
            return None # Queue is empty

        # 3. Update status to 'serving'
        token_id = next_waiting['token_id']
        updated_token = db.update_token_status(token_id, 'serving')

        # Augment with patient details for the doctor UI
        patient = db.get_user_by_id(updated_token['user_id']) 
        if updated_token and patient:
             updated_token['patient_name'] = patient['name']
             updated_token['patient_email'] = patient['email']
        return updated_token

    def mark_token_status(self, token_id: int, status: str) -> Optional[Dict[str, Any]]:
        """
        Marks a token as 'done' (served) or 'skipped'.
        """
        if status not in ('done', 'skipped'):
            raise ValueError("Status must be 'done' or 'skipped'.")

        updated_token = db.update_token_status(token_id, status)

        if updated_token:
            # Update stats
            is_served = (status == 'done')
            db.record_served_patient(updated_token['doctor_id'], is_served)

        return updated_token

    def get_daily_statistics(self) -> List[Dict[str, Any]]:
        """
        Fetches daily stats for the mock doctor.
        """
        return db.get_daily_stats(self.mock_doctor_id)

queue_logic = QueueLogic()