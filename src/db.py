import os 
from passlib.context import CryptContext
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional, List

# Load environment variables for mock data initialization
load_dotenv()

# Password hashing configuration
# NOTE: CryptContext is kept for schema compatibility, but actual hashing is simplified
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# --- Mock Database Structures (In-Memory) ---
MOCK_DB = {
    "users": [],
    "tokens": [],
    "stats": []
}

# Counters for generating IDs
user_id_counter = 1
token_id_counter = 1
stats_id_counter = 1

# --- Stable Hashing/Verification Functions ---

def hash_password(password: str) -> str:
    """
    STABILIZED: Uses a reversible, simple hash for stability in mock env.
    This avoids environment instability issues with bcrypt/sha256_crypt setup.
    """
    safe_password = str(password)
    # The simple hash is "SIMPLE_HASH_" + reversed_password
    return "SIMPLE_HASH_" + safe_password[::-1] 

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    STABILIZED: Verifies password using the simple string reversal logic.
    """
    safe_password = str(plain_password)
    
    # Check for the simple fallback hash format
    if hashed_password.startswith("SIMPLE_HASH_"):
        # Revert the hash back to the original password for comparison
        expected_password = hashed_password.replace("SIMPLE_HASH_", "")[::-1]
        return safe_password == expected_password
    
    # If a hash format not recognized by our stable system is provided, verification fails.
    return False


class MockDB:
    """Simulates database operations."""

    def __init__(self):
        # Initialize with the mock doctor if not already present
        global user_id_counter
        mock_email = os.getenv("MOCK_DOCTOR_EMAIL")
        mock_password = os.getenv("MOCK_DOCTOR_PASSWORD")
        
        # We must use the stable hash format for the doctor during initialization
        MOCK_DOCTOR_HARDCODED_HASH = hash_password(mock_password)

        if mock_email and mock_password and not self.get_user_by_email(mock_email):
            
            hashed_pw = MOCK_DOCTOR_HARDCODED_HASH
            
            self.add_user(
                name="Dr. Gregory House",
                email=mock_email,
                password_hash=hashed_pw,
                role="doctor",
                predefined_id=user_id_counter,
                is_hash=True
            )
            user_id_counter += 1

    def add_user(self, name: str, email: str, password: str = None, password_hash: str = None, role: str = 'patient', predefined_id: int = None, is_hash: bool = False) -> dict:
        """Adds a new user (Patient or Doctor)."""
        if self.get_user_by_email(email):
            return None 

        global user_id_counter
        user_id = predefined_id if predefined_id else user_id_counter
        if predefined_id is None:
            user_id_counter += 1

        if not is_hash and password:
            final_hash = hash_password(password)
        elif is_hash and password_hash:
            final_hash = password_hash
        else:
            raise ValueError("Must provide either a plain password or a hash.")
            
        # Optional check (not strictly needed since hash_password is now stable)
        if final_hash.startswith("SIMPLE_HASH_") and not is_hash:
             print(f"INFO: User {email} added with stable fallback hash.")

        new_user = {
            "user_id": str(user_id), 
            "role": role,
            "name": name,
            "email": email,
            "password_hash": final_hash,
            "created_at": str(datetime.now())
        }
        MOCK_DB['users'].append(new_user)
        return new_user

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Fetches a user by email."""
        for user in MOCK_DB['users']:
            if user['email'] == email:
                return user
        return None

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Fetches a user by ID."""
        for user in MOCK_DB['users']:
            if user['user_id'] == user_id:
                return user
        return None

    # --- Token Operations (Unchanged) ---

    def add_token(self, patient_id: str, doctor_id: str, token_number: str) -> dict:
        """Adds a new token to the queue."""
        global token_id_counter
        new_token = {
            "token_id": token_id_counter,
            "user_id": patient_id,
            "doctor_id": doctor_id,
            "status": "waiting",
            "issued_at": str(datetime.now()),
            "served_at": None,
            "token_number": token_number
        }
        MOCK_DB['tokens'].append(new_token)
        token_id_counter += 1
        return new_token

    def get_live_queue(self, doctor_id: str) -> List[dict]:
        """Retrieves waiting and serving tokens, sorted by issue time."""
        queue = [
            t for t in MOCK_DB['tokens'] 
            if t['doctor_id'] == doctor_id and t['status'] in ('waiting', 'serving')
        ]
        queue.sort(key=lambda t: t['issued_at'])
        return queue

    def update_token_status(self, token_id: int, status: str) -> Optional[dict]:
        """Updates the status of a specific token."""
        for token in MOCK_DB['tokens']:
            if token['token_id'] == token_id:
                token['status'] = status
                if status in ('done', 'skipped'):
                    token['served_at'] = str(datetime.now())
                return token
        return None

    # --- Stats Operations (Unchanged) ---
    
    def record_served_patient(self, doctor_id: str, is_served: bool):
        """Mocks updating daily stats."""
        global stats_id_counter
        today = datetime.now().date()
        
        daily_stat = next((s for s in MOCK_DB['stats'] 
                           if s['doctor_id'] == doctor_id and s['date'] == str(today)), None)

        if not daily_stat:
            daily_stat = {
                "stat_id": stats_id_counter,
                "doctor_id": doctor_id,
                "date": str(today),
                "patients_served": 0,
                "patients_skipped": 0,
                "avg_wait_time": 0.0
            }
            MOCK_DB['stats'].append(daily_stat)
            stats_id_counter += 1

        if is_served:
            daily_stat['patients_served'] += 1
        else:
            daily_stat['patients_skipped'] += 1
            
        total_served = daily_stat['patients_served']
        total_skipped = daily_stat['patients_skipped']
        
        if total_served + total_skipped > 0:
            daily_stat['avg_wait_time'] = (total_served * 10 + total_skipped * 5) / (total_served + total_skipped)
        else:
            daily_stat['avg_wait_time'] = 0.0

    def get_daily_stats(self, doctor_id: str) -> List[dict]:
        """Fetches all recorded statistics for a doctor."""
        return [s for s in MOCK_DB['stats'] if s['doctor_id'] == doctor_id]

# Initialize the mock database instance
db = MockDB()
