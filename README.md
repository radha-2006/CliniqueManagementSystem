🏥 Clinic Queue & Token Management System
📌 Project Description

The Clinic Queue & Token Management System is a full-stack Python application designed to streamline patient management in clinics and hospitals. The system generates digital tokens for patients, manages live queues, and allows doctors to track and serve patients efficiently.

This project showcases strong skills in backend development, database integration, frontend design, and API-driven communication — all without AI/ML.

✨ Features
👨‍⚕️ Frontend (Patient & Doctor UI)

🎨 Built with Streamlit (simple, interactive web interface).

📝 Patients can register and generate tokens.

📊 Doctors can view live queue, patient history, and manage token calling.

🔔 Real-time queue updates and notifications.

⚙️ Backend (Core Logic & API)

🧮 Core Python functions to handle token generation, queue management, and status updates.

📡 FastAPI endpoints for:

Adding patients

Fetching live queue

Marking patients as served/skipped

Viewing daily statistics

🗄️ Database (Supabase/PostgreSQL)

👤 User authentication (patients & doctors).

🧾 Store patient details, tokens, and visit history.

📂 Maintain doctor schedules and availability.

📊 Track statistics like average waiting time, patients served, and skipped tokens.

📂 Project Structure
ClinicQueueSystem/
│── src/                 # Core application logic
│   ├── logic.py         # Business logic (queue mgmt, token ops)
│   ├── db.py            # Database operations (Supabase)
│
│── API/                 # Backend API
│   ├── main.py          # FastAPI endpoints
│
│── Frontend/            # Frontend application
│   ├── app.py           # Streamlit web interface
│
│── requirements.txt     # Python dependencies
│── README.md            # Project documentation
│── .env                 # Environment variables (Supabase creds)

🚀 Quick Start
✅ Prerequisites

Python 3.8+

A Supabase account

Git (for cloning)

1️⃣ Clone or Download the Project

Option 1: Clone with Git

git clone https://github.com/radha-2006/ClinicQueueSystem.git


Option 2: Download ZIP

Extract files into a project folder.

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Set Up Supabase Database
Create Tables

users – Store patient & doctor accounts

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    role VARCHAR(20) CHECK (role IN ('patient', 'doctor')) NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);


tokens – Store generated tokens & queue info

CREATE TABLE tokens (
    token_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    doctor_id INT REFERENCES users(user_id),
    status VARCHAR(20) CHECK (status IN ('waiting','serving','done','skipped')) DEFAULT 'waiting',
    issued_at TIMESTAMP DEFAULT NOW(),
    served_at TIMESTAMP
);


doctor_schedule – Store doctor timings

CREATE TABLE doctor_schedule (
    schedule_id SERIAL PRIMARY KEY,
    doctor_id INT REFERENCES users(user_id),
    available_from TIME NOT NULL,
    available_to TIME NOT NULL,
    day VARCHAR(20) NOT NULL
);


stats – Track performance and analytics

CREATE TABLE stats (
    stat_id SERIAL PRIMARY KEY,
    doctor_id INT REFERENCES users(user_id),
    date DATE DEFAULT CURRENT_DATE,
    patients_served INT DEFAULT 0,
    patients_skipped INT DEFAULT 0,
    avg_wait_time FLOAT
);

4️⃣ Configure Environment Variables

Create a .env file in the root:

SUPABASE_URL=https://vgnsuebcwhoaweabqxuk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZnbnN1ZWJjd2hvYXdlYWJxeHVrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg5NTAwMTgsImV4cCI6MjA3NDUyNjAxOH0.L8DwUhCdT-TLw5l3ZZ6CABvFylgPgoJGQ4fGuwfzcYk


5️⃣ Run the Application

Frontend (Streamlit)

streamlit run Frontend/app.py


Open 👉 http://localhost:3000

Backend (FastAPI)

cd API
python main.py


API 👉 http://localhost:8000

🔧 Technologies Used

Frontend: Streamlit

Backend: FastAPI

Database: Supabase (PostgreSQL)

Language: Python 3.8+

📊 Future Enhancements

📱 Mobile-friendly PWA interface

📈 Advanced analytics dashboard

📲 SMS/WhatsApp notifications for tokens

🖥️ Multi-clinic support

🩺 Integration with EMR (Electronic Medical Records)

🗣️ Voice announcement for token calling

🛠️ Troubleshooting

Issue: "Module not Found"
✔️ Solution: Run

pip install -r requirements.txt


✔️ Ensure you’re inside project directory

🤝 Support

📧 radhasivani06@gmail.com

📞 8309655338