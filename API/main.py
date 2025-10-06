import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, RootModel 
from dotenv import load_dotenv

# Internal Imports
from src.db import db, verify_password # FIX: Imported verify_password explicitly
from src.logic import QueueLogic 

# Load environment variables (needed to initialize QueueLogic)
load_dotenv()

# --- Pydantic Schemas ---

class UserRegistration(BaseModel):
    name: str
    email: str
    password: str

class TokenResponse(BaseModel):
    token_id: int
    user_id: str
    doctor_id: str
    status: str
    issued_at: str
    token_number: str
    patient_name: Optional[str] = None
    patient_email: Optional[str] = None

class QueueStatus(RootModel[List[TokenResponse]]):
    """Defines the response model for a list of tokens."""
    pass

class StatsResponse(BaseModel):
    stat_id: int
    doctor_id: str
    date: str
    patients_served: int
    patients_skipped: int
    avg_wait_time: float


# --- Application Setup ---

app = FastAPI(title="Clinic Queue API", version="1.0.0")

# Instantiate the queue logic (Requires environment variables to be loaded)
try:
    queue_logic = QueueLogic()
except (EnvironmentError, ValueError) as e:
    print(f"FATAL ERROR during QueueLogic initialization: {e}")
    # Stop the server if the mock doctor setup fails
    raise SystemExit(f"Queue Logic Setup Failed: {e}") from e

# --- Auth Dependency (Mocked) ---

def get_current_user_mock(email: str = Depends(lambda email: email)) -> Dict[str, Any]:
    """Mock dependency to simulate user authentication (Doctor/Patient)."""
    user = db.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or authentication failed.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# --- ENDPOINTS ---

@app.get("/", tags=["Health"])
def read_root():
    """Simple health check."""
    return {"status": "ok", "message": "Clinic Queue API is running."}

# --- User Management ---

@app.post("/users/register", tags=["Users"], response_model=Dict[str, Any])
def register_user(user: UserRegistration, role: str = "patient"):
    """Register a new user (Patient or Doctor)."""
    if role not in ["patient", "doctor"]:
         raise HTTPException(status_code=400, detail="Invalid role specified.")

    new_user = db.add_user(user.name, user.email, user.password, role)

    if not new_user:
        raise HTTPException(status_code=400, detail="User already exists.")

    return {"message": f"{role.capitalize()} registered successfully.", "user_id": new_user['user_id']}

@app.post("/users/login", tags=["Users"], response_model=Dict[str, Any])
def login_user(user: UserRegistration):
    """Mock login endpoint for validation."""
    db_user = db.get_user_by_email(user.email)
    
    # FIX: Correctly call the global verify_password function imported from src.db
    if not db_user or not verify_password(user.password, db_user['password_hash']):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
        
    return {"message": "Login successful (Mock Auth)", "user": db_user}

# --- Token Management ---

@app.post("/tokens/generate/{email}", tags=["Tokens"], response_model=TokenResponse)
def generate_patient_token(email: str):
    """Patient generates a new token for themselves."""
    patient = db.get_user_by_email(email)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not registered.")

    token = queue_logic.generate_token(patient['user_id'])
    if not token:
        raise HTTPException(status_code=503, detail="No doctor available to issue a token.")

    # Augment response with basic patient info
    token['patient_name'] = patient['name']
    token['patient_email'] = patient['email']
    return token

@app.get("/queue/status", tags=["Queue"], response_model=List[TokenResponse])
def get_live_queue():
    """Fetches the current waiting and serving queue for the mock doctor."""
    return queue_logic.get_queue_status()

@app.post("/queue/call-next", tags=["Queue - Doctor Action"], response_model=Optional[TokenResponse])
def doctor_call_next():
    """Doctor calls the next patient in the queue."""
    result = queue_logic.call_next_patient()
    
    if result and 'error' in result:
        raise HTTPException(status_code=409, detail=result['error'])

    return result

@app.post("/queue/mark-status/{token_id}", tags=["Queue - Doctor Action"], response_model=TokenResponse)
def doctor_mark_status(token_id: int, status: str):
    """Doctor marks a patient token as 'done' or 'skipped'."""
    if status not in ['done', 'skipped']:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'done' or 'skipped'.")

    updated_token = queue_logic.mark_token_status(token_id, status)

    if not updated_token:
        raise HTTPException(status_code=404, detail=f"Token ID {token_id} not found.")

    return updated_token

# --- Statistics ---

@app.get("/stats/daily", tags=["Statistics"], response_model=List[StatsResponse])
def get_stats():
    """Fetches daily operational statistics for the mock doctor."""
    return queue_logic.get_daily_statistics()
