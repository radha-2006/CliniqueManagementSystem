import streamlit as st
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# --- Configuration ---
# Point to the FastAPI backend
API_BASE_URL = "http://127.0.0.1:8000"
# Credentials for the mock doctor are loaded in backend, not needed here

# --- API Interaction Functions ---

@st.cache_data(show_spinner=False)
def get_live_queue_status() -> List[Dict[str, Any]]:
    """Fetches the current live queue."""
    try:
        response = httpx.get(f"{API_BASE_URL}/queue/status")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        try:
             # FIX: Added robust check for JSON content before parsing
             if e.response.content:
                 detail = e.response.json().get("detail", str(e))
             else:
                 detail = "Backend returned empty response. Check backend terminal for crash logs."

        except json.JSONDecodeError:
             detail = f"Backend returned invalid JSON. Content: {e.response.content[:50]}..."

        except Exception:
             detail = str(e)
             
        st.error(f"Failed to fetch queue status (HTTP Error). Detail: {detail}")
        return []
    except httpx.RequestError as e:
        st.error(f"Network or connection error: {e}. Ensure the FastAPI backend is running.")
        return []
    except json.JSONDecodeError:
        st.error("Failed to decode JSON response from API. Check API logs.")
        return []

def api_call(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None):
    """Generic API caller function with robust error handling."""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "POST":
            response = httpx.post(url, json=data, params=params)
        elif method == "GET":
            response = httpx.get(url, params=params)
        else:
            raise ValueError("Unsupported HTTP method")

        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        # Check if the response actually contains JSON content (e.g., if 404/400)
        if e.response.content:
             try:
                detail = e.response.json().get("detail", "No detail provided.")
             except json.JSONDecodeError:
                detail = f"API returned non-JSON error format. Status: {e.response.status_code}"
        else:
             # This handles the case where FastAPI crashes and returns an empty 500 response
             detail = "Backend returned empty response (Possible Internal Server Error/Crash)."
             
        st.error(f"Operation failed. Status: {e.response.status_code}. Detail: {detail}")
        return {"error": detail}

    except httpx.RequestError as e:
        st.error(f"Network or connection error: {e}")
        return {"error": "Network or connection error."}
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return {"error": "An unexpected error occurred."}

# --- State Management & UI Components ---

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'patient_email' not in st.session_state:
    st.session_state['patient_email'] = ""
if 'token_info' not in st.session_state:
    st.session_state['token_info'] = None


def render_queue_display(queue_data):
    """Displays the current queue status for both patient and doctor."""
    
    st.subheader("Live Queue Status")
    
    if not queue_data:
        st.info("The waiting queue is currently empty.")
        return

    # Find the current serving patient
    serving = next((t for t in queue_data if t['status'] == 'serving'), None)
    
    # Calculate the waiting list (everything that is not serving)
    waiting_list = [t for t in queue_data if t['status'] == 'waiting']
    
    # --- Currently Serving Card ---
    with st.container(border=True):
        st.markdown("**NOW SERVING**")
        if serving:
            st.metric(
                label=f"Token: {serving.get('token_number', 'N/A')}", 
                value=serving.get('patient_name', 'Patient N/A'),
                help=f"Patient email: {serving.get('patient_email')}"
            )
        else:
            st.info("No patient is currently being served.")

    # --- Waiting List ---
    st.subheader(f"Waiting List ({len(waiting_list)})")
    
    if waiting_list:
        cols = st.columns([1, 2, 2])
        cols[0].markdown("**Queue Position**")
        cols[1].markdown("**Token Number**")
        cols[2].markdown("**Patient Name**")
        
        for i, token in enumerate(waiting_list):
            cols = st.columns([1, 2, 2])
            cols[0].write(i + 1)
            cols[1].markdown(f"**{token['token_number']}**")
            cols[2].write(token.get('patient_name', 'N/A'))
    else:
        st.info("No patients are currently waiting.")

    # Show patient's current token position if logged in as patient
    if st.session_state.user_role == 'patient' and st.session_state.token_info:
        current_token_id = st.session_state.token_info['token_id']
        try:
            position = next((i + 1 for i, t in enumerate(waiting_list) if t['token_id'] == current_token_id), None)
            
            if serving and serving['token_id'] == current_token_id:
                 st.success("✅ Your token is currently being served!")
            elif position is not None:
                st.info(f"Your token **{st.session_state.token_info['token_number']}** is currently at position **#{position}** in the waiting queue.")
            else:
                 st.warning("Your token is either served, skipped, or not yet in the active queue.")
        except Exception:
             pass


def doctor_actions_dashboard(queue_data):
    """Doctor dashboard for managing the queue."""
    st.title("👨‍⚕️ Doctor Queue Management")
    st.markdown("---")
    
    # Force refresh button to clear cache and reload data
    st.button("🔄 Refresh Queue Status", on_click=st.cache_data.clear)
    
    # --- Main Actions ---
    
    currently_serving = next((t for t in queue_data if t['status'] == 'serving'), None)
    
    col_call, col_mark = st.columns([1, 1])

    with col_call:
        if currently_serving:
            st.warning(f"Patient {currently_serving.get('token_number')} is currently being served.")
            st.button("Call Next Patient", disabled=True, use_container_width=True)
        else:
            st.button("📞 Call Next Patient", on_click=handle_call_next, type="primary", use_container_width=True)

    with col_mark:
        st.subheader("Mark Current Token")
        if currently_serving:
            st.markdown(f"**Token:** `{currently_serving['token_number']}` | **Patient:** `{currently_serving.get('patient_name')}`")
            
            col_done, col_skip = st.columns(2)
            with col_done:
                st.button("✅ Mark as Served (Done)", on_click=handle_mark_status, args=(currently_serving['token_id'], 'done'), type="success", use_container_width=True)
            with col_skip:
                st.button("❌ Mark as Skipped", on_click=handle_mark_status, args=(currently_serving['token_id'], 'skipped'), type="warning", use_container_width=True)
        else:
            st.info("No patient is actively serving to mark status.")
    
    st.markdown("---")
    render_queue_display(queue_data)
    
    # --- Stats View ---
    st.subheader("📊 Daily Statistics")
    stats = api_call("GET", "/stats/daily")
    if stats and not stats.get('error'):
        # Filter for today's stats
        today = datetime.now().strftime("%Y-%m-%d")
        daily_stats = [s for s in stats if s['date'] == today]
        
        if daily_stats:
            st.dataframe(daily_stats, hide_index=True)
        else:
            st.info("No statistics recorded for today.")
            
    elif not stats:
        st.info("No statistics recorded yet for today.")

# --- Action Handlers ---

def handle_login(email, password):
    """Handles both doctor and patient login validation."""
    # FIX: Cleaned up request data and relies on backend stabilization
    response = api_call("POST", "/users/login", data={"email": email, "password": password, "name": ""})
    
    if response and not response.get('error'):
        user = response['user']
        st.session_state.logged_in = True
        st.session_state.user_role = user['role']
        st.session_state.patient_email = user['email']
        st.success(f"Successfully logged in as {user['role'].capitalize()}!")
    else:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        # Error already displayed by api_call

def handle_registration(name, email, password, role):
    """Handles user registration."""
    response = api_call("POST", "/users/register", data={"name": name, "email": email, "password": password}, params={"role": role})
    
    if response and not response.get('error'):
        st.success(f"{response['message']} You can now log in.")

def handle_token_generation(email):
    """Handles patient generating a token."""
    response = api_call("POST", f"/tokens/generate/{email}")
    
    if response and not response.get('error'):
        st.session_state.token_info = response
        st.balloons()
        st.success(f"Token **{response['token_number']}** generated successfully! Please wait in the queue.")
        st.cache_data.clear()
    else:
        st.error("Failed to generate token. Check API logs.")

def handle_call_next():
    """Handles doctor calling the next waiting patient."""
    response = api_call("POST", "/queue/call-next")
    
    if response and not response.get('error'):
        st.success(f"Called next patient: **{response['token_number']}** - {response.get('patient_name', 'N/A')}")
        st.cache_data.clear()
    elif response and 'error' in response:
        st.warning(response['error']) 

def handle_mark_status(token_id, status):
    """Handles doctor marking a patient as done or skipped."""
    response = api_call("POST", f"/queue/mark-status/{token_id}", params={"status": status})
    
    if response and not response.get('error'):
        st.success(f"Token **{response['token_number']}** marked as **{status.upper()}**.")
        st.cache_data.clear()
    else:
        st.error("Failed to update token status.")

def handle_logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.patient_email = ""
    st.session_state.token_info = None
    st.cache_data.clear()
    st.experimental_rerun()

# --- Main App Layout ---

st.set_page_config(page_title="Clinic Queue System", layout="wide", initial_sidebar_state="expanded")

def main():
    """Main application layout."""
    
    st.sidebar.title("🏥 Clinic Queue System")

    # --- Sidebar Auth ---
    if st.session_state.logged_in:
        st.sidebar.success(f"Logged in as: {st.session_state.user_role.capitalize()}")
        st.sidebar.button("Logout", on_click=handle_logout, use_container_width=True)
        st.sidebar.markdown("---")
        
        if st.session_state.user_role == 'patient':
             st.sidebar.write(f"Patient Email: {st.session_state.patient_email}")

    else:
        st.sidebar.subheader("Login / Registration")
        
        tab_login, tab_register = st.sidebar.tabs(["Login", "Register"])
        
        with tab_login:
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True, type="primary"):
                handle_login(login_email, login_password)

        with tab_register:
            reg_name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email_addr")
            reg_password = st.text_input("Password", type="password", key="reg_password_val")
            reg_role = st.selectbox("Role", options=["patient", "doctor"], index=0, key="reg_role_select")
            
            if st.button("Register", use_container_width=True):
                handle_registration(reg_name, reg_email, reg_password, reg_role)
                
        st.sidebar.markdown("---")
        st.sidebar.info("Doctor Demo Login: `dr.house@clinic.com` / `password123`")

    # --- Main Content Area ---
    queue_data = get_live_queue_status()
    
    if st.session_state.user_role == 'doctor':
        doctor_actions_dashboard(queue_data)
        
    elif st.session_state.user_role == 'patient':
        st.title(f"Patient Portal: {st.session_state.patient_email}")
        
        if not st.session_state.token_info:
            if st.button("Generate Token & Start Queue", type="primary", use_container_width=True):
                handle_token_generation(st.session_state.patient_email)
        else:
             st.subheader(f"Your Token: {st.session_state.token_info['token_number']}")
             st.success("Your token has been issued.")
        
        st.markdown("---")
        render_queue_display(queue_data)
        
    else:
        st.title("Welcome to the Clinic Queue System Demo")
        st.info("Please use the sidebar to Login or Register to access the Patient or Doctor interfaces.")
        st.markdown("---")
        render_queue_display(queue_data) 


if __name__ == "__main__":
    main()
