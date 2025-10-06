🏥 CliniqueManagementSystem
The CliniqueManagementSystem is a full-stack Python application designed to streamline patient flow in clinics and hospitals. It manages digital token generation, displays live queue status, and allows doctors to track and serve patients efficiently.

This project showcases strong skills in backend development, database integration, frontend design, and API-driven communication.

✨ Features Overview
👨‍⚕️ Frontend (Patient & Doctor UI - Streamlit)
Registration & Login: Secure access for both patients and doctors.

Token Generation: Patients can quickly register and receive a unique token for the current queue.

Live Queue: Real-time visualization of the patient queue, including who is currently being served and the list of waiting patients.

Doctor Dashboard: Tools for doctors to manually call the next patient, mark tokens as 'served' or 'skipped', and view today's statistics.

⚙️ Backend (Core Logic & API - FastAPI)
The API manages all application state and business logic.

User Management: Endpoints for patient/doctor registration and mock login validation.

Token Flow: Endpoints for generating tokens, fetching the live queue, and updating token status.

Doctor Scheduling (New): CRUD operations to define a doctor's weekly availability (available_from, available_to, day).

Patient History (New): Retrieval of a patient's complete token and visit history, regardless of status.

Statistics: Fetching daily performance metrics (patients served, wait times).

🗄️ Database Schema (PostgreSQL)
The system is architected to use PostgreSQL (Supabase) for persistent data storage.

-- users: Store patient & doctor accounts
CREATE TABLE users (
user_id SERIAL PRIMARY KEY,
role VARCHAR(20) CHECK (role IN ('patient', 'doctor')) NOT NULL,
name VARCHAR(100) NOT NULL,
email VARCHAR(100) UNIQUE NOT NULL,
password_hash TEXT NOT NULL,
created_at TIMESTAMP DEFAULT NOW()
);

-- tokens: Store generated tokens & queue info
CREATE TABLE tokens (
token_id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(user_id),
doctor_id INT REFERENCES users(user_id),
status VARCHAR(20) CHECK (status IN ('waiting','serving','done','skipped')) DEFAULT 'waiting',
issued_at TIMESTAMP DEFAULT NOW(),
served_at TIMESTAMP
);

-- doctor_schedule: Store doctor timings
CREATE TABLE doctor_schedule (
schedule_id SERIAL PRIMARY KEY,
doctor_id INT REFERENCES users(user_id),
available_from TIME NOT NULL,
available_to TIME NOT NULL,
day VARCHAR(20) NOT NULL
);

-- stats: Track performance and analytics
CREATE TABLE stats (
stat_id SERIAL PRIMARY KEY,
doctor_id INT REFERENCES users(user_id),
date DATE DEFAULT CURRENT_DATE,
patients_served INT DEFAULT 0,
patients_skipped INT DEFAULT 0,
avg_wait_time FLOAT
);

📂 Project Structure
CliniqueManagementSystem/
│── src/                 # Core application logic
│   ├── logic.py         # Business logic (queue mgmt, token ops)
│   └── db.py            # Database operations (Mocked or Supabase client)
│
│── API/                 # Backend API
│   └── main.py          # FastAPI endpoints
│
│── Frontend/            # Frontend application
│   └── app.py           # Streamlit web interface
│
│── requirements.txt     # Python dependencies
│── README.md            # Project documentation
│── .env                 # Environment variables (Credentials)

🚀 Quick Start (Local Setup)
✅ Prerequisites
Python 3.8+

Git

1️⃣ Clone the Project
git clone [https://github.com/radha-2006/CliniqueManagementSystem.git](https://github.com/radha-2006/CliniqueManagementSystem.git)
cd CliniqueManagementSystem

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Configure Environment Variables
Create a .env file in the root directory for local mock testing:

MOCK_DOCTOR_EMAIL="dr.house@clinic.com"
MOCK_DOCTOR_PASSWORD="password123"

SUPABASE_URL=... # Placeholder
SUPABASE_KEY=... # Placeholder

4️⃣ Run the Application
The system requires two separate terminals running simultaneously.

Component

Command (Run from Root Directory)

Access URL

Backend (FastAPI)

uvicorn API.main:app --reload

http://127.0.0.1:8000

Frontend (Streamlit)

streamlit run Frontend/app.py

http://localhost:8501

🧪 Testing Credentials (Local Mock)
Role

Email

Password

Doctor

dr.house@clinic.com

password123

Patient

Register a new user via the Streamlit interface.

🤝 Support
For any questions or support, please contact:

Email: radhasivani06@gmail.com

Phone: 8309655338
