import hashlib
import logging
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
import mysql.connector as sq
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("Application Started")

# ------------------ Custom CSS for Tab Hover Effect and Headers ------------------
st.markdown(
    """
    <style>
    /* Style for the sidebar navigation tabs */
    .sidebar-tabs {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }

    .sidebar-tabs button {
        width: 100%;
        height: 50px; /* Fixed height for all buttons */
        padding: 10px;
        font-size: 16px;
        font-weight: bold;
        color: #FFFFFF;
        background-color: #4B0082; /* Indigo blue background */
        border: none;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: left;
        display: flex;
        align-items: center;
    }

    /* Hover effect for the tabs */
    .sidebar-tabs button:hover {
        background-color: #87CEEB; /* Sky blue on hover */
        transform: scale(1.02);
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
    }

    /* Active tab style */
    .sidebar-tabs button.active {
        background-color: #87CEEB; /* Sky blue for active tab */
        color: #FFFFFF;
    }

    /* Style for headers containing text boxes */
    .header-lightblue {
        background-color: #E6F7FF; /* Light blue background */
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
    }

    /* Style for text boxes */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stNumberInput > div > div > input {
        background-color: #FFFFFF; /* White background */
        border: 1px solid #87CEEB; /* Sky blue border */
        border-radius: 5px;
        padding: 8px;
    }

    /* Style for buttons */
    .stButton > button {
        background-color: #4B0082; /* Indigo blue background */
        color: #FFFFFF; /* White text */
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    /* Hover effect for buttons */
    .stButton > button:hover {
        background-color: #87CEEB; /* Sky blue on hover */
        transform: scale(1.05);
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
    }

    /* Active button style */
    .stButton > button:active {
        background-color: #87CEEB; /* Sky blue when clicked */
    }

    /* Text input focus effect */
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus, .stNumberInput > div > div > input:focus {
        border: 2px solid #87CEEB;
        background-color: #E6F7FF;
    }

    /* Passcode screen styles */
    .passcode-screen {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .passcode-box {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
        text-align: center;
    }

    .passcode-box input {
        width: 100%;
        padding: 10px;
        margin: 10px 0;
        border: 1px solid #87CEEB;
        border-radius: 5px;
    }

    .passcode-box button {
        background-color: #4B0082;
        color: #FFFFFF;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
    }

    .passcode-box button:hover {
        background-color: #87CEEB;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ------------------ Animated Startup Screen ------------------
def glowing_text(text, size=100, color="#FFFFFF"):  # Set text color to white
    """Returns an HTML string for glowing text effect."""
    return f"""
    <p style="font-size:{size}px; font-weight:bold; text-align:center; color:{color}; 
    text-shadow: 0px 0px 10px #FFFFFF, 0px 0px 20px #FFFFFF, 0px 0px 30px #FFFFFF;">
    {text}</p>"""


def startup_animation():
    messages = [
        "🌟 Welcome To 🌟",
        "🏥 The Hospital Management System 🏥",
        "🚀 Project By 🚀",
        "👨‍💻 YUVRAJ K GOND ‍💻"
    ]

    container = st.empty()
    box_html = """
    <div style='width:100%; height:600px; border: none; border-radius: 50px; 
    background: linear-gradient(45deg, #FF0000, #FF7F00, #FFFF00, #00FF00, #0000FF, #4B0082, #9400D3);
    background-size: 200% 200%; animation: rainbow 5s ease infinite; display:flex; justify-content:center; align-items:center;'>
    {content}
    </div>
    <style>
    @keyframes rainbow {{
        0% {{background-position: 0% 50%;}}
        50% {{background-position: 100% 50%;}}
        100% {{background-position: 0% 50%;}}
    }}
    </style>
    """

    start_time = time.time()
    while time.time() - start_time < 4:
        for msg in messages:
            if time.time() - start_time >= 4:
                break
            container.markdown(
                box_html.format(content=glowing_text(msg, size=48, color="#FFFFFF")),  # Set text color to white
                unsafe_allow_html=True
            )
            time.sleep(1)

    # Clear the animation container
    container.empty()
    st.session_state["startup_done"] = True
    st.rerun()  # Rerun the app to display the login page


# ------------------ Database Connection ------------------
def connection():
    try:
        con = sq.connect(host="localhost", user="root", password=".#RamJi.", database="HospitalManagement")
        if con.is_connected():
            logging.info("Database connection established successfully.")
            return con
        else:
            st.error("Database Not Connected!")
            logging.error("Database connection failed.")
            return None
    except sq.Error as er:
        st.error(f"Error: {er}")
        logging.error(f"Database connection error: {er}")
        return None


# ------------------ Hash Password ------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ------------------ User Authentication ------------------
def register_user(username, password, full_name, user_role):
    """
    Register a new user with the specified role (Admin, Doctor, Receptionist, Nurse, or Patient).
    """
    if not username or not password or not full_name:
        st.error("All fields are required!")
        logging.warning("Registration failed: Missing required fields.")
        return
    try:
        con = connection()
        if con:
            cur = con.cursor()
            hashed_password = hash_password(password)
            cur.execute(
                "INSERT INTO users(username, password_hash, full_name, user_role) VALUES (%s, %s, %s, %s)",
                (username, hashed_password, full_name, user_role)
            )
            con.commit()
            st.success("User Registered Successfully! Please Login.")
            logging.info(f"User {username} registered successfully with role: {user_role}.")
    except sq.Error as er:
        st.error(f"Error: {er}")
        logging.error(f"Error during user registration: {er}")


def login_user(username, password):
    """
    Authenticate a user and set session state based on their role.
    """
    try:
        con = connection()
        if con:
            cur = con.cursor()
            hashed_password = hash_password(password)
            cur.execute(
                "SELECT user_role FROM users WHERE username=%s AND password_hash=%s",
                (username, hashed_password)
            )
            user = cur.fetchone()
            if user:
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = user[0]
                st.session_state['username'] = username
                st.session_state["active_tab"] = "Dashboard"  # Set active tab to Dashboard
                st.success(f"Welcome {username} as a {st.session_state['user_role']}")
                logging.info(f"User {username} logged in successfully with role: {user[0]}.")

                # Log login action and mark attendance
                log_user_action(username, user[0], "login")
                mark_attendance(username, user[0])

                time.sleep(1)
                st.rerun()  # Rerun the app to reflect the changes
                return True
            else:
                st.error("Invalid Credentials!")
                logging.warning(f"Failed login attempt for username: {username}")
                return False
    except sq.Error as er:
        st.error(f"Error: {er}")
        logging.error(f"Error during login: {er}")
        return False


def logout():
    if st.session_state.get('authenticated'):
        # Log logout action
        log_user_action(st.session_state['username'], st.session_state['user_role'], "logout")

    st.session_state.clear()
    st.info("Login Session Terminated")
    st.warning("Please login to the system to access its features.")


# ------------------ Passcode Security ------------------
def check_passcode(passcode):
    """Check if the entered passcode is correct."""
    return passcode == "12345"  # Hardcoded passcode


# ------------------ Passcode Screen ------------------
def show_passcode_screen():
    """Displays the passcode screen with a blurred background."""
    st.markdown(
        """
        <div class="passcode-screen">
            <div class="passcode-box">
                <h3>Enter Passcode</h3>
                <input type="password" id="passcode" placeholder="Enter passcode">
                <button onclick="verifyPasscode()">Submit</button>
            </div>
        </div>
        <script>
        function verifyPasscode() {
            const passcode = document.getElementById('passcode').value;
            if (passcode === '12345') {
                window.location.href = window.location.href + '?passcode_verified=true';
            } else {
                alert('Incorrect Passcode!');
            }
        }
        </script>
        """,
        unsafe_allow_html=True
    )
# -----------------AcessControl-----------------
def access_control():
    """
    Ensure the user is authenticated before accessing any feature.
    """
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if not st.session_state['authenticated']:
        st.warning("Access Denied! Please login to access the Hospital Management System.")
        st.stop()


def check_user_role(required_roles):
    """
    Check if the user has the required role to access a feature.

    Args:
        required_roles (list): List of roles allowed to access the feature.
    """
    if 'user_role' not in st.session_state:
        st.warning("Access Denied! Please login to access this feature.")
        st.stop()

    if st.session_state['user_role'] not in required_roles:
        st.warning(f"Access Denied! This feature is only available to {', '.join(required_roles)}.")
        st.stop()


# ------------------ Feature-Specific Access ------------------
def manage_patients():
    """
    Manage Patients feature.
    Only Admin, Doctor, and Nurse can access this feature.
    """
    check_user_role(["Admin", "Doctor", "Nurse"])
    st.write("Manage Patients Page")


def view_appointments():
    """
    View Appointments feature.
    Only Admin, Doctor, Receptionist, and Nurse can access this feature.
    """
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse","Patient"])
    st.write("View Appointments Page")


# ------------------ Role-Specific Access ------------------
def restrict_access_to_admin():
    """
    Restrict access to Admin-only features.
    """
    check_user_role(["Admin"])


def restrict_access_to_doctor():
    """
    Restrict access to Doctor-only features.
    """
    check_user_role(["Doctor"])


def restrict_access_to_receptionist():
    """
    Restrict access to Receptionist-only features.
    """
    check_user_role(["Receptionist"])


def restrict_access_to_nurse():
    """
    Restrict access to Nurse-only features.
    """
    check_user_role(["Nurse"])


def restrict_access_to_patient():
    """
    Restrict access to Patient-only features.
    """
    check_user_role(["Patient"])


# ------------------ View Patients ------------------
def view_patients():
    """
    View Patients: Accessible to Admin, Doctor, and Nurse.
    """
    check_user_role(["Admin", "Doctor", "Nurse"])
    st.subheader("📋 Patient Records")

    # Fetch and display patient data
    patient_data = fetch_data("SELECT * FROM patients", "patients")
    if patient_data.empty:
        st.warning("No patient records found.")
    else:
        st.dataframe(patient_data)


# ------------------ View Patient History ------------------
def view_patient_history():
    """
    View Patient History: Accessible to Admin, Doctor, and Nurse.
    """
    check_user_role(["Admin", "Doctor", "Nurse"])
    st.subheader("📜 Patient History")

    # Fetch and display patient history
    patient_history = fetch_data("SELECT * FROM patient_history", "patient_history")
    if patient_history.empty:
        st.warning("No patient history records found.")
    else:
        st.dataframe(patient_history)


# ------------------ Fetch Data ------------------
def fetch_data(query, table_name, columns=None, default_columns=None, params=None):
    try:
        con = connection()
        if con:
            cur = con.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            data = cur.fetchall()

            if columns:
                col_names = columns
            else:
                if "COUNT" in query or "SUM" in query or "GROUP BY" in query:
                    col_names = ["category", "count"]
                else:
                    cur.execute(f"SHOW COLUMNS FROM {table_name}")
                    col_names = [col[0] for col in cur.fetchall()]

            con.close()

            if not data:
                return pd.DataFrame(columns=default_columns or col_names)

            if len(data[0]) != len(col_names):
                col_names = col_names[:len(data[0])]

            return pd.DataFrame(data, columns=col_names)
        else:
            return pd.DataFrame(columns=default_columns or columns if columns else [])
    except sq.Error as er:
        st.error(f"Error fetching data: {er}")
        logging.error(f"Error fetching data: {er}")
        return pd.DataFrame(columns=default_columns or columns if columns else [])


# ------------------ Insert Data ------------------
def insert_data(query, values):
    try:
        values = tuple(int(val) if isinstance(val, (np.int64, np.int32)) else val for val in values)
        con = connection()
        if con:
            cur = con.cursor()
            cur.execute(query, values)
            con.commit()
            st.success("Data inserted successfully!")
            logging.info(f"Data inserted successfully: {query}")
    except sq.Error as er:
        st.error(f"Error: {er}")
        logging.error(f"Error inserting data: {er}")


def log_user_action(username, role, action):
    try:
        con = connection()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO user_logs (username, role, action) VALUES (%s, %s, %s)",
            (username, role, action)
        )
        con.commit()
    except sq.Error as er:
        logging.error(f"Error logging user action: {er}")

#--------------AutoAttendenceMArking-----------------------------
def mark_attendance(username, role):
    """Mark attendance for a user if not already marked for the day."""
    try:
        con = connection()
        cur = con.cursor()

        # Check if attendance is already marked for the day
        cur.execute(
            "SELECT id FROM attendance WHERE username = %s AND attendance_date = CURDATE()",
            (username,)
        )
        if cur.fetchone():
            return  # Attendance already marked

        # Mark attendance
        cur.execute(
            "INSERT INTO attendance (username, role, attendance_date) VALUES (%s, %s, CURDATE())",
            (username, role)
        )
        con.commit()
    except sq.Error as er:
        logging.error(f"Error marking attendance: {er}")

def attendance_dashboard():
    st.subheader("📊 Attendance Dashboard")

    # Use tabs instead of radio buttons
    tab1, tab2 = st.tabs(["Last 7 Days", "Monthly Summary"])

    with tab1:
        show_last_7_days_records()

    with tab2:
        show_monthly_summary()


def fetch_last_7_days_records():
    """Fetch attendance records for the last 7 days."""
    query = """
        SELECT 
            username, 
            role, 
            attendance_date 
        FROM 
            attendance 
        WHERE 
            attendance_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        ORDER BY 
            attendance_date DESC
    """
    return fetch_data(query, "attendance", columns=["Username", "Role", "Date"])


def show_last_7_days_records():
    st.write("### Last 7 Days Attendance Records")

    # Fetch data
    last_7_days_data = fetch_last_7_days_records()

    if last_7_days_data.empty:
        st.info("No attendance records found for the last 7 days.")
    else:
        # Display data in a table
        st.dataframe(last_7_days_data)

        # Create a bar chart for last 7 days attendance
        st.write("### Last 7 Days Attendance Visualization")
        fig = px.bar(
            last_7_days_data,
            x="Date",
            y="Username",
            color="Role",
            title="Last 7 Days Attendance by Role",
            labels={"Date": "Date", "Username": "User Count"},
            color_discrete_sequence=px.colors.qualitative.Vivid  # Vibrant colors
        )
        st.plotly_chart(fig)


def fetch_monthly_summary():
    """Fetch monthly attendance summary by role."""
    query = """
        SELECT 
            role, 
            COUNT(DISTINCT username) AS user_count 
        FROM 
            attendance 
        WHERE 
            attendance_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        GROUP BY 
            role
    """
    return fetch_data(query, "attendance", columns=["Role", "User Count"])


def show_monthly_summary():
    st.write("### Monthly Attendance Summary")

    # Fetch data
    monthly_data = fetch_monthly_summary()

    if monthly_data.empty:
        st.info("No attendance records found for the last month.")
    else:
        # Display data in a table
        st.dataframe(monthly_data)

        # Create a pie chart for monthly attendance
        st.write("### Monthly Attendance Visualization")
        fig = px.pie(
            monthly_data,
            values="User Count",
            names="Role",
            title="Monthly Attendance by Role",
            color_discrete_sequence=px.colors.qualitative.Pastel  # Pastel colors
        )
        st.plotly_chart(fig)


# ------------------ Doctor Section ------------------
def doctor_section():
    """
    Doctor Section: Accessible to Admin, Doctor, Receptionist, Nurse, and Patient (view-only).
    """
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])  # Added "Nurse" to allowed roles

    # Add tabs for Doctor section
    if st.session_state['user_role'] == "Patient":
        # Patients can only view doctors (no tabs for adding doctors)
        view_doctors()  # Call the view_doctors function directly
    else:
        # Admin, Doctor, Receptionist, and Nurse can add and view doctors
        doctor_tabs = st.tabs(["Add Doctor", "View Doctors"])  # Removed "Notes" tab
        with doctor_tabs[0]:
            add_doctor()  # Add Doctor page
        with doctor_tabs[1]:
            view_doctors()  # View Doctors page


def view_doctors():
    """
    View Doctors: Accessible to Admin, Doctor, Receptionist, Nurse, and Patient (view-only).
    """
    st.subheader("👨‍⚕️ Doctor Records")
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])

    # Fetch doctor data with staff names, roles, and shifts
    query = """
        SELECT d.id, s.staff_name AS doctor_name, d.department, d.role, s.shift
        FROM doctor d
        JOIN staff s ON d.staff_id = s.id
    """
    doctor_data = fetch_data(query, "doctor", columns=["ID", "Doctor Name", "Department", "Role", "Shift"])

    if doctor_data.empty:
        st.warning("No doctor records found.")
        return

    # Display doctor records
    st.dataframe(doctor_data)

    # Add a download button for exporting the doctor data
    if st.button("📥 Download Doctor Records as CSV"):
        csv = doctor_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="doctor_records.csv",
            mime="text/csv"
        )


def add_doctor():
    """
    Add Doctor: Accessible to Admin, Doctor, Receptionist, and Nurse.
    """
    st.subheader("👨‍⚕️ Add Doctor")
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])  # Added "Nurse" to allowed roles

    # Fetch staff names, IDs, and roles for doctors
    staff_data = fetch_data("SELECT id, staff_name, role FROM staff WHERE role = 'Doctor'", "staff",
                            columns=["Staff ID", "Staff Name", "Role"])

    if staff_data.empty:
        st.warning("No doctors found in the staff table.")
        return

    # Select doctor name
    staff_name = st.selectbox("Select Doctor", staff_data["Staff Name"])
    staff_id = staff_data[staff_data["Staff Name"] == staff_name]["Staff ID"].iloc[0]
    role = staff_data[staff_data["Staff Name"] == staff_name]["Role"].iloc[0]

    # Input department
    department = st.text_input("Department*")

    if st.button("Add Doctor"):
        if not department:
            st.error("Department is required!")
            return

        # Insert doctor data into the doctor table
        insert_data(
            "INSERT INTO doctor (staff_id, department, role) VALUES (%s, %s, %s)",
            (staff_id, department, role)
        )
        st.success("Doctor added successfully!")


# ------------------ Manage Patients Section ------------------
def initialize_rooms_and_ambulances():
    """Initialize 50 general rooms, 25 ICU rooms, and 5 ambulances if they don't exist."""
    con = connection()
    cur = con.cursor()

    # Check if rooms already exist
    cur.execute("SELECT COUNT(*) FROM rooms")
    if cur.fetchone()[0] == 0:
        # Create 50 general rooms (Single, Double, Deluxe)
        for i in range(1, 51):
            room_type = "Single" if i <= 20 else ("Double" if i <= 40 else "Deluxe")
            cur.execute(
                "INSERT INTO rooms (room_number, room_type, availability, is_icu) VALUES (%s, %s, 'Not Booked', FALSE)",
                (f"GEN-{i}", room_type)
            )

        # Create 25 ICU rooms
        for i in range(1, 26):
            cur.execute(
                "INSERT INTO rooms (room_number, room_type, availability, is_icu) VALUES (%s, 'ICU', 'Not Booked', TRUE)",
                (f"ICU-{i}",)
            )

        con.commit()

    # Check if ambulances already exist
    cur.execute("SELECT COUNT(*) FROM ambulances")
    if cur.fetchone()[0] == 0:
        # Create 5 ambulances
        for i in range(1, 6):
            cur.execute(
                "INSERT INTO ambulances (ambulance_number, status) VALUES (%s, 'Available')",
                (f"AMB-{i}",)
            )

        con.commit()

    con.close()


# Call the function to initialize rooms and ambulances
initialize_rooms_and_ambulances()

def add_patient():
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])
    try:
        st.markdown('<div class="header-lightblue"><h3>📝 Add New Patient</h3></div>', unsafe_allow_html=True)

        # Patient Details
        name = st.text_input("Patient Name*")
        age = st.number_input("Age*", min_value=0)
        gender = st.selectbox("Gender*", ["M", "F"])
        address = st.text_area("Address*")
        contact_no = st.text_input("Contact Number*")
        dob = st.date_input("Date of Birth*")

        # Fetch consultant names and departments from the doctor table
        doctor_data = fetch_data(
            """
            SELECT s.staff_name AS consultant_name, d.department 
            FROM doctor d 
            JOIN staff s ON d.staff_id = s.id
            """,
            "doctor",
            columns=["Consultant Name", "Department"]
        )

        if doctor_data.empty:
            st.warning("No doctors found. Please add doctors first.")
            return

        # Select consultant name
        consultant_name = st.selectbox("Consultant Name*", doctor_data["Consultant Name"])

        # Fetch the department for the selected consultant
        department = doctor_data[doctor_data["Consultant Name"] == consultant_name]["Department"].iloc[0]

        # Display the department as a read-only field
        st.text_input("Department*", value=department, disabled=True)

        # Rest of the patient details
        date_of_consultancy = st.date_input("Date of Consultancy*")
        diseases = st.text_input("Disease*")
        fees = st.number_input("Fees*", min_value=0.0, format="%.2f")

        # Fetch medicine from inventory
        inventory_items = fetch_data("SELECT item_name, quantity FROM inventory", "inventory",
                                     ["Item Name", "Quantity"])
        if not inventory_items.empty:
            medicine_options = {f"{row['Item Name']} (Available: {row['Quantity']})": row["Item Name"] for _, row in
                                inventory_items.iterrows()}
            selected_medicine = st.selectbox("Select Medicine", list(medicine_options.keys()))
            medicine_name = medicine_options.get(selected_medicine)
            max_quantity = inventory_items[inventory_items["Item Name"] == medicine_name]["Quantity"].iloc[0]
            quantity = st.number_input("Quantity*", min_value=1, max_value=max_quantity, value=1)
        else:
            st.warning("No medicine available in inventory.")
            medicine_name = None
            quantity = 0

        if st.button("Add Patient"):
            required_fields = [name, age, gender, address, contact_no, dob, consultant_name, date_of_consultancy,
                               department, diseases, fees]
            if not all(required_fields):
                st.error("Please fill all required fields (*)")
                logging.warning("Add Patient: Missing required fields.")
            else:
                # Insert patient data (without role)
                insert_data(
                    """
                    INSERT INTO patients (name, age, gender, address, contact_no, dob, consultant_name, department, date_of_consultancy, diseases, fees, medicine, quantity)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (name, age, gender, address, contact_no, dob, consultant_name, department, date_of_consultancy,
                     diseases, fees, medicine_name, quantity)
                )
                st.success("Patient added successfully!")
                logging.info(f"Patient {name} added successfully.")

                # Deduct the quantity from inventory
                if medicine_name and quantity > 0:
                    insert_data(
                        "UPDATE inventory SET quantity = quantity - %s WHERE item_name = %s",
                        (quantity, medicine_name)
                    )
                    st.success(f"{quantity} units of {medicine_name} deducted from inventory.")
    except Exception as e:
        st.error(f"Error adding patient: {e}")
        logging.error(f"Error adding patient: {e}")


def view_patients():
    st.subheader("📋 Patient Records with Room and Medicine Details")
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])

    # Fetch patient data with room and medicine details
    query = """
        SELECT 
            p.id AS 'Patient ID',
            p.name AS 'Patient Name',
            p.age AS 'Age',
            p.gender AS 'Gender',
            p.address AS 'Address',
            p.contact_no AS 'Contact No',
            p.dob AS 'Date of Birth',
            p.consultant_name AS 'Consultant',
            p.date_of_consultancy AS 'Consultancy Date',
            p.department AS 'Department',
            p.diseases AS 'Disease',
            p.fees AS 'Fees',
            p.medicine AS 'Medicine',
            p.quantity AS 'Quantity',
            COALESCE(r.room_number, 'N/A') AS 'Room Number',
            COALESCE(r.room_type, 'N/A') AS 'Room Type'
        FROM 
            patients p
        LEFT JOIN 
            rooms r ON p.id = r.patient_id
    """
    patient_data = fetch_data(query, "patients", columns=[
        "Patient ID", "Patient Name", "Age", "Gender", "Address", "Contact No",
        "Date of Birth", "Consultant", "Consultancy Date", "Department",
        "Disease", "Fees", "Medicine", "Quantity", "Room Number", "Room Type"
    ])

    if patient_data.empty:
        st.info("No patient records found.")
    else:
        # Add search and filter functionality
        st.markdown("### 🔍 Search and Filter Patients")
        col1, col2 = st.columns(2)

        with col1:
            search_query = st.text_input("Search by Patient Name or ID")

        with col2:
            filter_department = st.selectbox("Filter by Department",
                                             ["All"] + list(patient_data["Department"].unique()))

        # Apply search and filter
        if search_query:
            patient_data = patient_data[
                patient_data["Patient Name"].str.contains(search_query, case=False) |
                patient_data["Patient ID"].astype(str).str.contains(search_query)
                ]

        if filter_department != "All":
            patient_data = patient_data[patient_data["Department"] == filter_department]

        # Display the filtered data
        st.dataframe(patient_data)

        # Add a download button for exporting the patient data
        if st.button("📥 Download Patient Records as CSV"):
            csv = patient_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="patient_records.csv",
                mime="text/csv"
            )

        # Add a simple visualization
        st.markdown("### 📊 Patient Distribution by Department")
        if not patient_data.empty:
            department_counts = patient_data["Department"].value_counts().reset_index()
            department_counts.columns = ["Department", "Number of Patients"]

            fig = px.bar(
                department_counts,
                x="Department",
                y="Number of Patients",
                title="Patient Distribution by Department",
                labels={"Department": "Department", "Number of Patients": "Number of Patients"},
                color="Department",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig)
        else:
            st.info("No data available for visualization.")


def discharge_patient():
    """Discharge patient, free up room, and record discharge details with reason."""
    st.subheader("\U0001F3E2 Discharge Patient from Room")
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])

    # Fetch the list of patients currently allocated to rooms (both general and ICU)
    query = """
        SELECT 
            COALESCE(r.patient_id, ep.id) AS 'Patient ID',  -- General patient_id or ICU patient's emergency_patients.id
            COALESCE(p.name, ep.name) AS 'Patient Name',    -- Patient name from either table
            r.room_number AS 'Room Number', 
            r.room_type AS 'Room Type', 
            r.is_icu AS 'ICU Room',
            ep.id AS 'Emergency Patient ID'  -- Explicitly fetch emergency_patient_id
        FROM rooms r
        LEFT JOIN patients p ON r.patient_id = p.id
        LEFT JOIN emergency_patients ep ON r.id = ep.room_id
        WHERE r.availability = 'Booked'
    """
    patient_data = fetch_data(
        query,
        "patients",
        ["Patient ID", "Patient Name", "Room Number", "Room Type", "ICU Room", "Emergency Patient ID"]
    )

    # Check if there are any patients to discharge
    if patient_data.empty:
        st.info("No patients currently allocated to rooms.")
        return

    # Create a dropdown for selecting a patient to discharge
    patient_options = {
        f"{row['Patient Name']} (ID: {row['Patient ID']}) - {row['Room Number']} ({'ICU' if row['ICU Room'] else 'General'})":
            (row["Patient ID"], row["Emergency Patient ID"], row["Room Number"], row["ICU Room"])
        for _, row in patient_data.iterrows()
    }
    selected_patient = st.selectbox("Select Patient to Discharge", list(patient_options.keys()))
    patient_id, emergency_patient_id, room_number, is_icu = patient_options.get(selected_patient, (None, None, None, None))

    if selected_patient:
        # Fetch the selected patient's details
        patient_info = patient_data[
            (patient_data["Patient ID"] == patient_id) |
            (patient_data["Emergency Patient ID"] == emergency_patient_id)
        ]

        if not patient_info.empty:
            patient_info = patient_info.iloc[0]
            patient_id = int(patient_info["Patient ID"]) if not pd.isna(patient_info["Patient ID"]) else None
            emergency_patient_id = int(patient_info["Emergency Patient ID"]) if not pd.isna(patient_info["Emergency Patient ID"]) else None
            room_number = str(patient_info["Room Number"])
            room_type = str(patient_info["Room Type"])
            is_icu = bool(patient_info["ICU Room"])

            # Display patient details
            st.write(f"**Patient Name:** {patient_info['Patient Name']}")
            st.write(f"**Room Number:** {room_number}")
            st.write(f"**Room Type:** {room_type}")
            st.write(f"**ICU Room:** {'Yes' if is_icu else 'No'}")

            discharge_reason = st.text_area("Enter Discharge Reason")

            if st.button("Confirm Discharge"):
                if not discharge_reason.strip():
                    st.warning("Discharge Reason cannot be empty!")
                    return

                con = connection()
                cur = con.cursor()
                try:
                    # Insert discharge record based on patient type
                    if is_icu:
                        # Use emergency_patient_id for ICU patients and set patient_id to NULL
                        cur.execute(
                            """
                            INSERT INTO discharged_patients 
                            (patient_id, emergency_patient_id, patient_name, room_number, room_type, discharge_date, discharge_time, discharge_reason, is_icu)
                            VALUES (NULL, %s, %s, %s, %s, CURDATE(), CURTIME(), %s, %s)
                            """,
                            (emergency_patient_id, patient_info["Patient Name"], room_number, room_type, discharge_reason, is_icu)
                        )
                    else:
                        # Use patient_id for general patients and set emergency_patient_id to NULL
                        cur.execute(
                            """
                            INSERT INTO discharged_patients 
                            (patient_id, emergency_patient_id, patient_name, room_number, room_type, discharge_date, discharge_time, discharge_reason, is_icu)
                            VALUES (%s, NULL, %s, %s, %s, CURDATE(), CURTIME(), %s, %s)
                            """,
                            (patient_id, patient_info["Patient Name"], room_number, room_type, discharge_reason, is_icu)
                        )

                    # Update room status
                    cur.execute(
                        "UPDATE rooms SET availability = 'Not Booked', patient_id = NULL WHERE room_number = %s",
                        (room_number,)
                    )

                    con.commit()
                    st.success(f"✅ {patient_info['Patient Name']} discharged successfully! Room {room_number} is now available.")
                    st.rerun()
                except Exception as e:
                    con.rollback()
                    st.error(f"Error during discharge: {e}")
                    logging.error(f"Discharge Error: {e}")
                finally:
                    con.close()
        else:
            st.error("Selected patient not found in the records.")
    else:
        st.warning("Please select a patient to discharge.")

def view_discharged_patients():
    st.subheader("\U0001F4DC Discharged Patients Records")
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])

    # Fetch discharged patient records
    discharged_data = fetch_data(
        """
        SELECT 
            COALESCE(patient_id, emergency_patient_id) AS 'Patient ID',
            patient_name AS 'Patient Name',
            room_number AS 'Room Number',
            room_type AS 'Room Type',
            is_icu AS 'ICU Room',
            discharge_date AS 'Discharge Date',
            discharge_time AS 'Discharge Time',
            discharge_reason AS 'Discharge Reason'
        FROM discharged_patients
        """,
        "discharged_patients",
        ["Patient ID", "Patient Name", "Room Number", "Room Type", "ICU Room", "Discharge Date", "Discharge Time",
         "Discharge Reason"]
    )

    # Check if there are any discharged patients
    if discharged_data.empty:
        st.info("No discharged patient records found.")
    else:
        # Display the ICU room status
        discharged_data["ICU Room"] = discharged_data["ICU Room"].apply(lambda x: "Yes" if x else "No")
        st.dataframe(discharged_data)

def allocate_room():
    try:
        st.markdown('<div class="header-lightblue"><h3>\U0001F3E2 Allocate Room to Patient</h3></div>', unsafe_allow_html=True)

        # Fetch patients without allocated rooms
        patients_without_rooms = fetch_data(
            "SELECT id, name FROM patients WHERE id NOT IN (SELECT patient_id FROM rooms WHERE patient_id IS NOT NULL)",
            "patients",
            ["Patient ID", "Patient Name"]
        )

        if not patients_without_rooms.empty:
            # Convert to native Python types
            patient_options = {
                f"{row['Patient Name']} (ID: {int(row['Patient ID'])})": int(row['Patient ID'])
                for _, row in patients_without_rooms.iterrows()
            }
            selected_patient = st.selectbox("Select Patient", list(patient_options.keys()))
            patient_id = patient_options.get(selected_patient)

            # Fetch available general rooms
            available_rooms = fetch_data(
                "SELECT id, room_number, room_type FROM rooms WHERE availability = 'Not Booked' AND is_icu = FALSE",
                "rooms",
                ["Room ID", "Room Number", "Room Type"]
            )

            if not available_rooms.empty:
                room_options = {
                    f"{row['Room Number']} ({row['Room Type']})": int(row['Room ID'])
                    for _, row in available_rooms.iterrows()
                }
                selected_room = st.selectbox("Select Room", list(room_options.keys()))
                room_id = room_options.get(selected_room)

                if st.button("Allocate Room") and patient_id and room_id:
                    # Convert to native Python int
                    patient_id = int(patient_id)
                    room_id = int(room_id)

                    insert_data(
                        "UPDATE rooms SET availability = 'Booked', patient_id = %s WHERE id = %s",
                        (patient_id, room_id)
                    )
                    st.success(f"Room {selected_room} allocated to {selected_patient}!")
            else:
                st.warning("No general rooms available.")
        else:
            st.info("No patients needing room allocation.")
    except Exception as e:
        st.error(f"Error allocating room: {e}")

# New function to handle discharging patients
def discharge_patient_ui():
    st.subheader("🚪 Discharge Patient")

    # Fetch all patients with allocated rooms (including ICU)
    patients_with_rooms = fetch_data(
        """
        SELECT p.id AS 'Patient ID', p.name AS 'Patient Name', r.room_number AS 'Room Number'
        FROM patients p
        JOIN rooms r ON p.id = r.patient_id
        WHERE r.availability = 'Booked'  <--- ADDED THIS LINE
        """,
        "patients",
        ["Patient ID", "Patient Name", "Room Number"]
    )

    if not patients_with_rooms.empty:
        # Create dropdown options with unique identifiers
        patient_options = {
            f"{row['Patient Name']} (ID: {int(row['Patient ID'])}) - Room {row['Room Number']}": int(row['Patient ID'])
            for _, row in patients_with_rooms.iterrows()
        }

        selected_patient = st.selectbox("Select Patient to Discharge", list(patient_options.keys()))
        patient_id = patient_options.get(selected_patient)

        if st.button("Discharge Patient") and patient_id:
            # Convert to native Python int
            patient_id = int(patient_id)
            result = discharge_patient(patient_id)
            st.success(result)
    else:
        st.info("No patients with allocated rooms found.")

#---------------------------Emergency Unit-----------------------
def add_emergency_patient():
    st.markdown('<div class="header-lightblue"><h3>🚨 Add Emergency Patient</h3></div>', unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])

    # Patient Details
    name = st.text_input("Patient Name*")
    contact_no = st.text_input("Contact Number*")
    address = st.text_area("Address*")
    blood_type = st.selectbox("Blood Type*", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])

    # Fetch available ICU rooms
    available_icu_rooms = fetch_data(
        "SELECT id, room_number FROM rooms WHERE is_icu = TRUE AND availability = 'Not Booked'",
        "rooms",
        ["ID", "Room Number"]
    )

    room_options = {
        f"{row['Room Number']}": int(row['ID'])  # Convert to native Python int
        for _, row in available_icu_rooms.iterrows()
    }
    selected_room = st.selectbox("Assign ICU Room*", ["NA"] + list(room_options.keys()))

    # Doctor Assignment
    available_doctors = fetch_data(
        "SELECT id, staff_name FROM staff WHERE role = 'Doctor'",
        "staff",
        ["ID", "Doctor Name"]
    )
    doctor_options = {
        f"{row['Doctor Name']}": int(row['ID'])  # Convert to native Python int
        for _, row in available_doctors.iterrows()
    }
    selected_doctor = st.selectbox("Assign Doctor*", list(doctor_options.keys()))
    doctor_id = doctor_options.get(selected_doctor)

    if st.button("Add Emergency Patient"):
        required_fields = [name, contact_no, address, blood_type, selected_doctor]
        if not all(required_fields):
            st.error("Please fill all required fields (*)")
        elif selected_room == "NA":
            st.error("ICU Room selection is mandatory")
        else:
            # Get room_id from options
            room_id = room_options.get(selected_room)

            # Insert emergency patient
            insert_data(
                """
                INSERT INTO emergency_patients (name, contact_no, address, blood_type, room_id, doctor_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (name, contact_no, address, blood_type, room_id, doctor_id)
            )

            # Update ICU room status
            insert_data(
                "UPDATE rooms SET availability = 'Booked' WHERE id = %s",
                (room_id,)
            )

            st.success("Emergency patient added successfully!")

def view_emergency_patients():
    st.subheader("🚨 Emergency Patients")
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])

    # Get ICU room status
    total_icu = fetch_data(
        "SELECT COUNT(*) FROM rooms WHERE is_icu = TRUE",
        "rooms"
    ).iloc[0, 0]

    available_icu = fetch_data(
        "SELECT COUNT(*) FROM rooms WHERE is_icu = TRUE AND availability = 'Not Booked'",
        "rooms"
    ).iloc[0, 0]

    st.write(f"**ICU Rooms:** {available_icu} Available / {total_icu} Total")

    # Fetch emergency patient data with room numbers
    query = """
        SELECT 
            ep.id AS 'ID',
            ep.name AS 'Patient Name',
            ep.contact_no AS 'Contact No',
            ep.address AS 'Address',
            ep.blood_type AS 'Blood Type',
            r.room_number AS 'Room Number',
            s.staff_name AS 'Assigned Doctor',
            ep.admission_date AS 'Admission Date'
        FROM 
            emergency_patients ep
        LEFT JOIN 
            rooms r ON ep.room_id = r.id
        LEFT JOIN 
            staff s ON ep.doctor_id = s.id
    """
    emergency_data = fetch_data(query, "emergency_patients")

    if emergency_data.empty:
        st.info("No emergency patient records found.")
    else:
        st.dataframe(emergency_data)

def allocate_icu_room_to_emergency_patient(patient_id):
    """Allocate an ICU room to an emergency patient from Emergency Unit section."""
    con = connection()
    cur = con.cursor()

    # Get available ICU room
    cur.execute("SELECT id, room_number FROM rooms WHERE availability = 'Not Booked' AND is_icu = TRUE LIMIT 1")
    room = cur.fetchone()
    if room:
        room_id, room_number = room

        # Assign room to patient
        cur.execute("UPDATE rooms SET availability = 'Booked', patient_id = %s WHERE id = %s", (patient_id, room_id))
        con.commit()
        return f"ICU Room {room_number} allocated successfully!"
    else:
        return "No ICU rooms available!"


# New function to handle discharging emergency patients
def discharge_emergency_patient_ui():
    st.subheader("🚪 Discharge Emergency Patient")

    # Fetch all emergency patients with allocated ICU rooms
    emergency_patients_with_rooms = fetch_data(
        """
        SELECT ep.id AS 'Patient ID', ep.name AS 'Patient Name', r.room_number AS 'Room Number'
        FROM emergency_patients ep
        JOIN rooms r ON ep.room_id = r.id
        WHERE r.is_icu = TRUE AND r.availability = 'Booked'  <--- ADDED AVAILABILITY CHECK
        """,
        "emergency_patients",
        ["Patient ID", "Patient Name", "Room Number"]
    )

    if not emergency_patients_with_rooms.empty:
        # Create dropdown options with unique identifiers
        patient_options = {
            f"{row['Patient Name']} (ID: {int(row['Patient ID'])}) - Room {row['Room Number']}": int(row['Patient ID'])
            for _, row in emergency_patients_with_rooms.iterrows()
        }

        selected_patient = st.selectbox("Select Emergency Patient to Discharge", list(patient_options.keys()))
        patient_id = patient_options.get(selected_patient)

        if st.button("Discharge Emergency Patient") and patient_id:
            # Convert to native Python int
            patient_id = int(patient_id)
            result = discharge_patient(patient_id)
            st.success(result)
    else:
        st.info("No emergency patients with allocated ICU rooms found.")

def emergency_summary_metrics():
    st.subheader("📊 Emergency Summary Metrics")

    # Total Emergency Patients
    total_patients = fetch_data("SELECT COUNT(*) FROM emergency_patients", "emergency_patients", columns=["count"])
    total_patients = total_patients.iloc[0, 0] if not total_patients.empty else 0

    # Available ICU Rooms
    available_icu_rooms = fetch_data(
        "SELECT COUNT(*) FROM rooms WHERE is_icu = TRUE AND availability = 'Not Booked'",
        "rooms",
        columns=["count"]
    )
    available_icu_rooms = available_icu_rooms.iloc[0, 0] if not available_icu_rooms.empty else 0

    # Assigned Doctors
    assigned_doctors = fetch_data(
        "SELECT COUNT(DISTINCT doctor_id) FROM emergency_patients",
        "emergency_patients",
        columns=["count"]
    )
    assigned_doctors = assigned_doctors.iloc[0, 0] if not assigned_doctors.empty else 0

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Emergency Patients", total_patients)
    with col2:
        st.metric("Available ICU Rooms", available_icu_rooms)
    with col3:
        st.metric("Assigned Doctors", assigned_doctors)


def emergency_patients_by_blood_type():
    st.write("### Emergency Patients by Blood Type")

    # Fetch data
    blood_type_data = fetch_data(
        "SELECT blood_type, COUNT(*) as count FROM emergency_patients GROUP BY blood_type",
        "emergency_patients",
        columns=["Blood Type", "Count"]
    )

    if not blood_type_data.empty:
        # Create pie chart
        fig = px.pie(
            blood_type_data,
            values="Count",
            names="Blood Type",
            title="Emergency Patients by Blood Type",
            color_discrete_sequence=px.colors.qualitative.Pastel  # Attractive colors
        )
        st.plotly_chart(fig)
    else:
        st.info("No blood type data available.")


def emergency_patients_over_time():
    st.write("### Emergency Patients Over Time")

    # Fetch data
    patients_over_time = fetch_data(
        "SELECT DATE(admission_date) as date, COUNT(*) as count FROM emergency_patients GROUP BY DATE(admission_date)",
        "emergency_patients",
        columns=["Date", "Count"]
    )

    if not patients_over_time.empty:
        # Create line chart
        fig = px.line(
            patients_over_time,
            x="Date",
            y="Count",
            title="Emergency Patients Over Time",
            labels={"Date": "Date", "Count": "Number of Patients"},
            color_discrete_sequence=["#FFA07A"]  # Light coral color
        )
        st.plotly_chart(fig)
    else:
        st.info("No admission data available.")


def icu_room_utilization():
    st.write("### ICU Room Utilization")

    # Fetch data
    room_utilization = fetch_data(
        "SELECT availability, COUNT(*) as count FROM rooms WHERE is_icu = TRUE GROUP BY availability",
        "rooms",
        columns=["Status", "Count"]
    )

    if not room_utilization.empty:
        # Create bar chart
        fig = px.bar(
            room_utilization,
            x="Status",
            y="Count",
            title="ICU Room Utilization",
            labels={"Status": "Room Status", "Count": "Number of Rooms"},
            color="Status",
            color_discrete_sequence=["#87CEEB", "#FF6347"]  # Sky blue and tomato colors
        )
        st.plotly_chart(fig)
    else:
        st.info("No ICU room data available.")


def emergency_dashboard():
    st.subheader("🚨 Emergency Unit Dashboard")
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])

    # Display summary metrics
    emergency_summary_metrics()

    # Display visualizations
    col1, col2 = st.columns(2)
    with col1:
        emergency_patients_by_blood_type()
    with col2:
        icu_room_utilization()

    emergency_patients_over_time()


# ------------------ Room Info Section ------------------
def room_info_section():
    """Manage Room Information Section."""
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])
    st.subheader("\U0001F3E2 Room Info")
    room_tabs = st.tabs(["Allocate Room", "View Rooms", "Discharge Patient", "View Discharged Patients"])

    with room_tabs[0]:
        allocate_room()

    with room_tabs[1]:
        view_rooms()

    with room_tabs[2]:
        discharge_patient()

    with room_tabs[3]:
        view_discharged_patients()

def view_rooms():
    st.subheader("\U0001F3E2 Room Availability")
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])
    # Fetch total number of general rooms
    total_gen = fetch_data(
        "SELECT COUNT(*) FROM rooms WHERE room_type = 'Single' OR room_type = 'Double' OR room_type = 'Deluxe'",
        "rooms"
    ).iloc[0, 0]

    # Fetch number of available general rooms
    available_gen = fetch_data(
        "SELECT COUNT(*) FROM rooms WHERE (room_type = 'Single' OR room_type = 'Double' OR room_type = 'Deluxe') AND availability = 'Not Booked'",
        "rooms"
    ).iloc[0, 0]

    # Calculate allocated general rooms
    allocated_gen = total_gen - available_gen

    # Display the results
    st.write(f"**General Rooms:** {available_gen} Available | {allocated_gen} Allocated | {total_gen} Total")

    df = fetch_data(
        """
        SELECT 
            id AS 'ID', 
            room_number AS 'Room Number', 
            room_type AS 'Room Type', 
            availability AS 'Status', 
            is_icu AS 'ICU Room',
            patient_id AS 'Patient ID'
        FROM rooms
        """,
        "rooms",
        ["ID", "Room Number", "Room Type", "Status", "ICU Room", "Patient ID"]
    )
    if df.empty:
        st.info("No room records found.")
    else:
        # Replace NULL patient_id with "N/A" for better readability
        df["Patient ID"] = df["Patient ID"].fillna("N/A")
        st.dataframe(df)


# ------------------ Billing Section ------------------
def add_bill():
    try:
        st.markdown('<div class="header-lightblue"><h3>💸 Add New Bill</h3></div>', unsafe_allow_html=True)

        # Fetch patient data
        patient_data = fetch_data("SELECT id, name FROM patients", "patients", ["id", "name"])

        if not patient_data.empty:
            # Select patient
            patient_name = st.selectbox("Select Patient", patient_data["name"])
            patient_id = int(patient_data.loc[patient_data["name"] == patient_name, "id"].values[0])

            # Fetch patient details
            con = connection()
            cur = con.cursor()
            cur.execute("SELECT contact_no, fees FROM patients WHERE id = %s", (patient_id,))
            patient_info = cur.fetchone()
            contact_no = patient_info[0]
            doctor_fees = patient_info[1]

            # Input fields for bill details
            room_charges = st.number_input("Room Charges", min_value=0.0, format="%.2f")
            pathology_fees = st.number_input("Pathology Fees", min_value=0.0, format="%.2f")
            medicine_charges = st.number_input("Medicine Charges", min_value=0.0, format="%.2f")

            # Room type dropdown with allowed values
            room_type = st.selectbox("Room Type", ["NA","Single", "Double", "ICU", "Deluxe"])

            # Calculate total amount
            total_amount = float(room_charges) + float(pathology_fees) + float(medicine_charges) + float(doctor_fees)
            st.write(f"### Total Amount: ₹ {total_amount:.2f}")

            # Add Bill button
            if st.button("Add Bill"):
                try:
                    # Handle "NA" room type
                    if room_type == "NA":
                        room_type = "NA"

                    # Insert bill details into the database
                    insert_data("""
                        INSERT INTO bill_details 
                        (bill_date, patient_id, name, contact_no, room_charges, pathology_fees, medicine_charges, doctor_fees, room_type, total_amount)
                        VALUES (CURDATE(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                    patient_id, patient_name, contact_no, room_charges, pathology_fees, medicine_charges, doctor_fees,
                    room_type, total_amount))

                    st.success("Bill added successfully!")
                    logging.info(f"Bill added for patient {patient_name}.")
                except Exception as e:
                    st.error(f"Error adding bill: {e}")
                    logging.error(f"Error adding bill: {e}")
        else:
            st.warning("No patient records found. Please add a patient first.")
            logging.warning("No patient records found for billing.")
    except Exception as e:
        st.error(f"Error in billing section: {e}")
        logging.error(f"Error in billing section: {e}")

def view_bills():
    st.subheader("\U0001F4B8 Billing Information")

    # Fetch billing data along with patient details
    query = """
        SELECT 
            b.bill_no AS 'Bill No', 
            b.bill_date AS 'Bill Date', 
            b.patient_id AS 'Patient ID', 
            p.name AS 'Patient Name', 
            p.age AS 'Age', 
            p.gender AS 'Gender', 
            p.address AS 'Address', 
            p.contact_no AS 'Contact No', 
            p.dob AS 'Date of Birth', 
            p.consultant_name AS 'Consultant', 
            p.department AS 'Department', 
            p.diseases AS 'Disease', 
            p.fees AS 'Fees',
            p.medicine AS 'Medicine',
            p.quantity AS 'Quantity',
            b.room_charges AS 'Room Charges', 
            b.pathology_fees AS 'Pathology Fees', 
            b.medicine_charges AS 'Medicine Charges', 
            b.doctor_fees AS 'Doctor Fees', 
            b.total_amount AS 'Total Amount', 
            b.room_type AS 'Room Type'
        FROM bill_details b
        JOIN patients p ON b.patient_id = p.id
    """
    columns = [
        "Bill No", "Bill Date", "Patient ID", "Patient Name", "Age", "Gender",
        "Address", "Contact No", "Date of Birth", "Consultant", "Department",
        "Disease", "Fees", "Medicine", "Quantity", "Room Charges", "Pathology Fees",
        "Medicine Charges", "Doctor Fees", "Total Amount", "Room Type"
    ]
    df = fetch_data(query, "bill_details", columns)

    if df.empty:
        st.info("No billing records found.")
    else:
        st.dataframe(df)

# ------------------ Dashboard Section ------------------
def show_dashboard():
    # Key Metrics Section
    st.markdown("### 📊Hospital Dashboard")
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])
    col1, col2, col3 = st.columns(3)

    with col1:
        data = fetch_data("SELECT COUNT(*) FROM patients WHERE DATE(date_of_consultancy) = CURDATE()", "patients")
        total_patients_today = data.iloc[0, 0] if not data.empty else 0
        st.metric("Total Patients Admitted Today", total_patients_today)

    with col2:
        data = fetch_data("SELECT COUNT(*) FROM rooms WHERE room_type = 'ICU' AND availability = 'Not Booked'", "rooms")
        available_icu_rooms = data.iloc[0, 0] if not data.empty else 0
        st.metric("Available ICU Rooms", available_icu_rooms)

    with col3:
        data = fetch_data("SELECT SUM(total_amount) FROM bill_details WHERE MONTH(bill_date) = MONTH(CURDATE())",
                          "bill_details")
        total_revenue_value = data.iloc[0, 0] if not data.empty and data.iloc[0, 0] is not None else 0.0
        total_revenue = f"₹ {total_revenue_value:.2f}"
        st.metric("Total Revenue This Month", total_revenue)

    # Alerts Section (Only Display When Necessary)
    st.markdown("### ⚠️ Alerts")
    total_icu_rooms = fetch_data("SELECT COUNT(*) FROM rooms WHERE is_icu = TRUE", "rooms").iloc[0, 0]
    occupied_icu_rooms = \
    fetch_data("SELECT COUNT(*) FROM rooms WHERE is_icu = TRUE AND availability = 'Booked'", "rooms").iloc[0, 0]
    icu_occupancy_rate = (occupied_icu_rooms / total_icu_rooms) * 100 if total_icu_rooms else 0

    # Display ICU Occupancy Alert Only if Occupancy > 80%
    if icu_occupancy_rate > 80:
        st.warning(f"⚠️ ICU Room Occupancy is at {icu_occupancy_rate:.2f}%. Consider expanding capacity.")

    # Display Low Stock Alert Only if Low Stock Items Exist
    low_stock_items = fetch_data("SELECT COUNT(*) FROM inventory WHERE quantity < 5", "inventory").iloc[0, 0]
    if low_stock_items > 0:
        st.warning(f"⚠️ {low_stock_items} critical inventory items have low stock levels!")
    # 🔹 Enhanced Visualizations Section
    st.markdown("### 📊 Hospital Summarized Visulization")

    # Patient Demographics Card
    patient_demographics_card()

    # Revenue Trend Sparkline
    revenue_trend_sparkline()

    # Doctor-Patient Ratio Donut
    doctor_patient_ratio_donut()

    # Room Utilization Heatmap
    room_utilization_heatmap()

    # Staff Shift Sunburst
    staff_shift_sunburst()

    # Patient Age Distribution
    patient_age_distribution()

    # Live Inventory Gauge
    live_inventory_gauge()

    # Appointment Calendar
    appointment_calendar()

    # ICU and General Rooms Details
    st.markdown("### 🏨 Room Details")
    room_tabs = st.tabs(["ICU Rooms", "General Rooms"])

    with room_tabs[0]:
        icu_room_details()

    with room_tabs[1]:
        general_room_details()

    # Discharge Patients Graph
    st.markdown("### 📉 Discharge Patients Over Time")
    discharge_patients_graph()

    # Add Patients Graph
    st.markdown("### 📈 Patients Added Over Time")
    add_patients_graph()

    # Disease Word Cloud
    st.markdown("### 🦠 Disease Frequency")
    disease_word_cloud()

    # Emergency Response Time
    st.markdown("### 🚨 Emergency Response Time")
    emergency_response_time()

    # Patient Gender Ratio
    st.markdown("### ⚕️ Patient Gender Ratio")
    patient_gender_ratio()

    # Patient Department Distribution
    st.markdown("### 🏥 Patients per Department")
    patient_department_distribution()

    # Room Allocation Chart
    st.markdown("### 🏨 Room Allocation by Type")
    room_allocation_chart()


def patient_demographics_card():
    """Enhanced patient demographics card with more detailed information."""
    try:
        # Fetch data
        patient_count_data = fetch_data("SELECT COUNT(*) FROM patients", "patients")
        avg_age_data = fetch_data("SELECT AVG(age) FROM patients", "patients")
        top_disease_data = fetch_data("SELECT diseases FROM patients GROUP BY diseases ORDER BY COUNT(*) DESC LIMIT 1",
                                      "patients")
        top_department_data = fetch_data(
            "SELECT department FROM patients GROUP BY department ORDER BY COUNT(*) DESC LIMIT 1", "patients")

        # Handle empty data
        patient_count = patient_count_data.iloc[0, 0] if not patient_count_data.empty else 0
        avg_age = avg_age_data.iloc[0, 0] if not avg_age_data.empty and avg_age_data.iloc[0, 0] is not None else 0.0
        top_disease = top_disease_data.iloc[0, 0] if not top_disease_data.empty else "No data"
        top_department = top_department_data.iloc[0, 0] if not top_department_data.empty else "No data"

        # Display the card
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; backdrop-filter: blur(10px); box-shadow: 0 8px 32px 0 rgba(135, 206, 235, 0.3);">
            <h3>👥 Patient Demographics</h3>
            <p>Total Patients: <span style="color: #87CEEB;">{patient_count}</span></p>
            <p>Avg Age: <span style="color: #FF6B6B;">{avg_age:.1f}</span></p>
            <p>Top Disease: <span style="color: #6BFF6B;">{top_disease}</span></p>
            <p>Most Common Department: <span style="color: #FFD700;">{top_department}</span></p>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error fetching patient demographics: {e}")
        logging.error(f"Error in patient_demographics_card: {e}")


def icu_room_details():
    """Display ICU room details with availability and allocation."""
    try:
        # Fetch ICU room data
        icu_data = fetch_data(
            "SELECT room_number, availability FROM rooms WHERE is_icu = TRUE",
            "rooms",
            columns=["Room Number", "Status"]
        )

        # Check if ICU data is empty
        if icu_data.empty:
            st.warning("No ICU room data available.")
            return

        # Create a bar chart for ICU room status
        fig = px.bar(
            icu_data,
            x="Room Number",
            y="Status",
            title="🏥 ICU Room Status",
            color="Status",
            color_discrete_sequence=["#FF6347", "#87CEEB"],  # Red for booked, Blue for available
            labels={"Room Number": "Room Number", "Status": "Status"}
        )
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error fetching ICU room details: {e}")
        logging.error(f"Error in icu_room_details: {e}")


def general_room_details():
    """Display general room details with availability and allocation."""
    try:
        # Fetch general room data
        general_data = fetch_data(
            "SELECT room_number, availability FROM rooms WHERE is_icu = FALSE",
            "rooms",
            columns=["Room Number", "Status"]
        )

        # Check if general room data is empty
        if general_data.empty:
            st.warning("No general room data available.")
            return

        # Create a bar chart for general room status
        fig = px.bar(
            general_data,
            x="Room Number",
            y="Status",
            title="🏨 General Room Status",
            color="Status",
            color_discrete_sequence=["#FF6347", "#87CEEB"],  # Red for booked, Blue for available
            labels={"Room Number": "Room Number", "Status": "Status"}
        )
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error fetching general room details: {e}")
        logging.error(f"Error in general_room_details: {e}")


def revenue_trend_sparkline():
    """Enhanced revenue trend visualization with annotations and better formatting."""
    revenue_data = fetch_data(
        "SELECT DATE_FORMAT(bill_date, '%Y-%m') AS month, SUM(total_amount) AS total_amount FROM bill_details GROUP BY month",
        "bill_details",
        columns=["month", "total_amount"]
    )

    # Check if revenue_data is empty
    if revenue_data.empty:
        st.warning("No revenue data available to display.")
        return

    # Create the line chart
    fig = px.line(revenue_data, x='month', y='total_amount',
                  title="💰 Monthly Revenue Trend",
                  line_shape="spline",
                  color_discrete_sequence=["#BA68C8"],
                  labels={"month": "Month", "total_amount": "Revenue (₹)"})
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Month", yaxis_title="Revenue (₹)",
                      hovermode="x unified")

    # Add annotation for the last data point
    last_month = revenue_data['month'].iloc[-1]
    last_revenue = revenue_data['total_amount'].iloc[-1]
    fig.add_annotation(
        x=last_month,
        y=last_revenue,
        text=f"₹ {last_revenue:.2f}",
        showarrow=True,
        arrowhead=1
    )

    # Display the chart
    st.plotly_chart(fig)


def doctor_patient_ratio_donut():
    """Enhanced doctor-patient ratio visualization with dynamic colors."""
    doctor_count = fetch_data("SELECT COUNT(*) FROM staff WHERE role = 'Doctor'", "staff").iloc[0, 0]
    patient_count = fetch_data("SELECT COUNT(*) FROM patients", "patients").iloc[0, 0]
    fig = px.pie(values=[doctor_count, patient_count],
                 names=["Doctors", "Patients"],
                 hole=0.6,
                 title="⚕️ Doctor-Patient Ratio",
                 color_discrete_sequence=["#4B0082", "#87CEEB"],
                 labels={"value": "Count", "names": "Category"})
    fig.update_traces(textposition='inside', textinfo='percent+label', pull=[0.1, 0])
    st.plotly_chart(fig)


def patient_department_distribution():
    """Enhanced department distribution visualization with interactive filtering."""
    department_data = fetch_data(
        "SELECT department, COUNT(*) as count FROM patients GROUP BY department",
        "patients",
        columns=["Department", "Count"]
    )
    if not department_data.empty:
        fig = px.bar(department_data, x="Department", y="Count",
                     title="🏥 Patients per Department",
                     color="Count", color_continuous_scale="Blues",
                     labels={"Count": "Number of Patients", "Department": "Department"})
        fig.update_layout(xaxis_tickangle=-45, hovermode="x unified")
        st.plotly_chart(fig)
    else:
        st.warning("No department data available.")


def room_allocation_chart():
    """Enhanced room allocation visualization with dynamic filtering."""
    room_data = fetch_data(
        "SELECT room_type, COUNT(*) as count FROM rooms WHERE availability = 'Booked' GROUP BY room_type",
        "rooms",
        columns=["Room Type", "Count"]
    )
    if not room_data.empty:
        fig = px.pie(room_data, values="Count", names="Room Type",
                     title="🏨 Room Allocation by Type",
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel,
                     labels={"Count": "Number of Rooms", "Room Type": "Room Type"})
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig)
    else:
        st.warning("No room allocation data available.")


def patient_gender_ratio():
    """Enhanced gender ratio visualization with dynamic colors."""
    gender_data = fetch_data(
        "SELECT gender, COUNT(*) as count FROM patients GROUP BY gender",
        "patients",
        columns=["Gender", "Count"]
    )
    if not gender_data.empty:
        gender_map = {"M": "Male", "F": "Female"}
        gender_data["Gender"] = gender_data["Gender"].map(gender_map)
        fig = px.pie(gender_data, values="Count", names="Gender",
                     title="⚕️ Patient Gender Ratio",
                     color_discrete_sequence=["#3498db", "#e74c3c"],
                     labels={"Count": "Number of Patients", "Gender": "Gender"})
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig)
    else:
        st.warning("No gender data available.")


def room_utilization_heatmap():
    """Enhanced room utilization heatmap with better color scaling."""
    room_status_matrix = fetch_data(
        "SELECT room_type, availability, COUNT(*) as count FROM rooms GROUP BY room_type, availability",
        "rooms",
        columns=["Room Type", "Status", "Count"]
    ).pivot(index="Room Type", columns="Status", values="Count")
    fig = px.imshow(room_status_matrix,
                    labels=dict(x="Status", y="Room Type", color="Count"),
                    color_continuous_scale=["#FF0000", "#00FF00"],
                    title="🏨 Room Utilization Heatmap")
    fig.update_xaxes(side="top")
    st.plotly_chart(fig)


def discharge_patients_graph():
    """Display discharge patients over time."""
    try:
        # Fetch discharge data
        discharge_data = fetch_data(
            "SELECT DATE(discharge_date) as date, COUNT(*) as count FROM discharged_patients GROUP BY DATE(discharge_date)",
            "discharged_patients",
            columns=["Date", "Count"]
        )

        # Check if discharge data is empty
        if discharge_data.empty:
            st.warning("No discharge data available.")
            return

        # Create a line chart for discharge patients over time
        fig = px.line(
            discharge_data,
            x="Date",
            y="Count",
            title="📉 Discharge Patients Over Time",
            line_shape="spline",
            color_discrete_sequence=["#FF10F0"],  # Pink color
            labels={"Date": "Date", "Count": "Number of Discharges"}
        )
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating discharge patients graph: {e}")
        logging.error(f"Error in discharge_patients_graph: {e}")


def add_patients_graph():
    """Display patients added over time."""
    try:
        # Fetch patient addition data
        add_data = fetch_data(
            "SELECT DATE(date_of_consultancy) as date, COUNT(*) as count FROM patients GROUP BY DATE(date_of_consultancy)",
            "patients",
            columns=["Date", "Count"]
        )

        # Check if patient addition data is empty
        if add_data.empty:
            st.warning("No patient addition data available.")
            return

        # Create a line chart for patients added over time
        fig = px.line(
            add_data,
            x="Date",
            y="Count",
            title="📈 Patients Added Over Time",
            line_shape="spline",
            color_discrete_sequence=["#BA68C8"],  # Purple color
            labels={"Date": "Date", "Count": "Number of Patients Added"}
        )
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating patients added graph: {e}")
        logging.error(f"Error in add_patients_graph: {e}")


def staff_shift_sunburst():
    """Enhanced staff shift visualization with dynamic colors."""
    try:
        # Fetch staff shift data
        staff_data = fetch_data(
            "SELECT role, shift, COUNT(*) as count FROM staff GROUP BY role, shift",
            "staff",
            columns=["Role", "Shift", "Count"]
        )

        # Check if staff_data is empty
        if staff_data.empty:
            st.warning("No staff shift data available to display.")
            return

        # Create the sunburst chart
        fig = px.sunburst(
            staff_data,
            path=['Role', 'Shift'],
            color='Role',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title="🌌 Staff Shift Distribution",
            labels={"Count": "Number of Staff"}
        )
        fig.update_traces(textinfo="label+percent parent")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating staff shift sunburst chart: {e}")
        logging.error(f"Error in staff_shift_sunburst: {e}")


def patient_age_distribution():
    """Enhanced age distribution visualization with dynamic age groups."""
    age_data = fetch_data(
        """
        SELECT 
            CASE 
                WHEN age BETWEEN 0 AND 18 THEN '0-18'
                WHEN age BETWEEN 19 AND 30 THEN '19-30'
                WHEN age BETWEEN 31 AND 50 THEN '31-50'
                ELSE '51+' 
            END AS age_group, 
            COUNT(*) as count 
        FROM patients 
        GROUP BY age_group
        """,
        "patients",
        columns=["Age Group", "Count"]
    )
    if not age_data.empty:
        fig = px.bar(age_data, x="Age Group", y="Count",
                     title="📊 Patient Age Distribution",
                     color="Count", color_continuous_scale="Sunset",
                     labels={"Count": "Number of Patients", "Age Group": "Age Group"})
        fig.update_layout(coloraxis_showscale=False, hovermode="x unified")
        st.plotly_chart(fig)
    else:
        st.warning("No patient age data available.")


def live_inventory_gauge():
    """Enhanced inventory gauge with dynamic thresholds."""
    low_stock_percent_data = fetch_data(
        "SELECT COUNT(*) * 100.0 / (SELECT COUNT(*) FROM inventory) as percent FROM inventory WHERE quantity < 10",
        "inventory"
    )
    low_stock_percent = low_stock_percent_data.iloc[0, 0] if not low_stock_percent_data.empty else 0
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=low_stock_percent,
        title="⚠️ Critical Inventory",
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#FF10F0"},
            'steps': [
                {'range': [0, 50], 'color': "#87CEEB"},
                {'range': [50, 100], 'color': "#4B0082"}
            ]
        }
    ))
    st.plotly_chart(fig)


def appointment_calendar():
    appointment_data = fetch_data(
        "SELECT DAY(appointment_date) as day, MONTH(appointment_date) as month, COUNT(*) as count FROM appointments GROUP BY day, month",
        "appointments",
        columns=["Day", "Month", "Count"]
    )
    fig = px.density_heatmap(appointment_data, x='Day', y='Month', z='Count',
                             title="📅 Appointment Calendar",
                             color_continuous_scale="Plasma",
                             labels={"Day": "Day of Month", "Month": "Month", "Count": "Number of Appointments"})
    fig.update_layout(yaxis_nticks=12, hovermode="x unified")
    st.plotly_chart(fig)


def disease_word_cloud():
    disease_freq_data = fetch_data(
        "SELECT diseases, COUNT(*) as count FROM patients GROUP BY diseases",
        "patients",
        columns=["Disease", "Count"]
    )
    if not disease_freq_data.empty:
        fig = px.bar(disease_freq_data, x="Disease", y="Count",
                     title="🦠 Disease Frequency",
                     labels={"Disease": "Disease Name", "Count": "Number of Cases"},
                     color="Count",
                     color_continuous_scale="Viridis")
        fig.update_layout(xaxis_tickangle=-45, hovermode="x unified")
        st.plotly_chart(fig)
    else:
        st.warning("No disease data available to display.")


def emergency_response_time():
    response_time_data = fetch_data(
        "SELECT AVG(TIMESTAMPDIFF(MINUTE, admission_date, NOW())) FROM emergency_patients",
        "emergency_patients"
    )
    response_time = response_time_data.iloc[0, 0] if not response_time_data.empty and response_time_data.iloc[
        0, 0] is not None else 0
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=response_time,
        title="🚨 Emergency Response Time (Minutes)",
        gauge={
            'axis': {'range': [0, 30]},
            'bar': {'color': "#FF0000"},
            'steps': [
                {'range': [0, 10], 'color': "#FFD700"},
                {'range': [10, 30], 'color': "#FF4500"}
            ]
        }
    ))
    st.plotly_chart(fig)


# ------------------ Advanced Search ------------------
def advanced_search():
    st.subheader("🔍 Advanced Search")


    # Define search options based on user role
    if st.session_state['user_role'] == "Patient":
        search_options = ["Patients", "Appointments", "Discharged Patients", "Bills"]
    else:
        search_options = [
            "Patients", "Staff", "Rooms", "Bills", "Appointments", "Inventory",
            "Emergency Patients", "Ambulance Service", "Discharged Patients", "Doctors"
        ]

    # Add a search type dropdown with dynamic options
    search_type = st.selectbox("Select Search Type", search_options)

    # Add a search query input field
    search_query = st.text_input(f"Enter {search_type} Name, ID, or Keyword")

    # Add a search button
    if st.button(f"Search {search_type}"):
        if not search_query.strip():
            st.warning("Please enter a search query!")
            return

        # Initialize results as an empty DataFrame
        results = pd.DataFrame()

        # Define the base query for each search type
        if search_type == "Patients":
            query = f"""
                SELECT 
                    p.id AS 'Patient ID', 
                    p.name AS 'Patient Name', 
                    p.age AS 'Age', 
                    p.gender AS 'Gender', 
                    p.address AS 'Address', 
                    p.contact_no AS 'Contact No', 
                    p.dob AS 'Date of Birth', 
                    p.consultant_name AS 'Consultant', 
                    p.date_of_consultancy AS 'Consultancy Date', 
                    p.department AS 'Department', 
                    p.diseases AS 'Disease', 
                    p.fees AS 'Fees',
                    p.medicine AS 'Medicine',
                    p.quantity AS 'Quantity',
                    COALESCE(r.room_number, 'N/A') AS 'Room Number',
                    COALESCE(r.room_type, 'N/A') AS 'Room Type',
                    COALESCE(d.discharge_date, 'N/A') AS 'Discharge Date',
                    COALESCE(d.discharge_reason, 'N/A') AS 'Discharge Reason'
                FROM patients p
                LEFT JOIN rooms r ON p.id = r.patient_id
                LEFT JOIN discharged_patients d ON p.id = d.patient_id
                WHERE p.name LIKE '%{search_query}%' 
                    OR p.id = '{search_query}'
                    OR p.medicine LIKE '%{search_query}%'
                    OR p.quantity = '{search_query}'
            """
            # Define the columns for the query results
            columns = [
                "Patient ID", "Patient Name", "Age", "Gender", "Address", "Contact No",
                "Date of Birth", "Consultant", "Consultancy Date", "Department",
                "Disease", "Fees", "Medicine", "Quantity", "Room Number", "Room Type",
                "Discharge Date", "Discharge Reason"
            ]
            results = fetch_data(query, "patients", columns)

        elif search_type == "Doctors":
            query = f"""
                SELECT 
                    d.id AS 'Doctor ID', 
                    s.staff_name AS 'Doctor Name', 
                    d.department AS 'Department', 
                    s.shift AS 'Shift', 
                    d.role AS 'Role'
                FROM doctor d
                JOIN staff s ON d.staff_id = s.id
                WHERE s.staff_name LIKE '%{search_query}%' 
                    OR d.id = '{search_query}'
                    OR d.department LIKE '%{search_query}%'
            """
            # Define the columns for the query results
            columns = ["Doctor ID", "Doctor Name", "Department", "Shift", "Role"]
            results = fetch_data(query, "doctor", columns)

        elif search_type == "Appointments":
            query = f"""
                SELECT 
                    a.id AS 'Appointment ID', 
                    a.patient_name AS 'Patient Name', 
                    a.doctor_name AS 'Doctor Name', 
                    a.appointment_date AS 'Appointment Date', 
                    a.appointment_time AS 'Appointment Time'
                FROM appointments a
                WHERE a.patient_name LIKE '%{search_query}%' 
                    OR a.doctor_name LIKE '%{search_query}%'
                    OR a.id = '{search_query}'
            """
            # Define the columns for the query results
            columns = ["Appointment ID", "Patient Name", "Doctor Name", "Appointment Date", "Appointment Time"]
            results = fetch_data(query, "appointments", columns)

        elif search_type == "Bills":
            query = f"""
                SELECT 
                    b.bill_no AS 'Bill No', 
                    b.bill_date AS 'Bill Date', 
                    b.patient_id AS 'Patient ID', 
                    b.name AS 'Patient Name', 
                    b.contact_no AS 'Contact No', 
                    b.room_charges AS 'Room Charges', 
                    b.pathology_fees AS 'Pathology Fees', 
                    b.medicine_charges AS 'Medicine Charges', 
                    b.doctor_fees AS 'Doctor Fees', 
                    b.total_amount AS 'Total Amount', 
                    b.room_type AS 'Room Type'
                FROM bill_details b
                WHERE b.name LIKE '%{search_query}%' 
                    OR b.patient_id = '{search_query}'
                    OR b.bill_no = '{search_query}'
            """
            # Define the columns for the query results
            columns = [
                "Bill No", "Bill Date", "Patient ID", "Patient Name", "Contact No",
                "Room Charges", "Pathology Fees", "Medicine Charges", "Doctor Fees",
                "Total Amount", "Room Type"
            ]
            results = fetch_data(query, "bill_details", columns)

        elif search_type == "Discharged Patients":
            query = f"""
                SELECT 
                    d.patient_id AS 'Patient ID', 
                    d.patient_name AS 'Patient Name', 
                    d.room_number AS 'Room Number', 
                    d.room_type AS 'Room Type', 
                    d.discharge_date AS 'Discharge Date', 
                    d.discharge_time AS 'Discharge Time', 
                    d.discharge_reason AS 'Discharge Reason', 
                    d.is_icu AS 'ICU Room'
                FROM discharged_patients d
                WHERE d.patient_name LIKE '%{search_query}%' 
                    OR d.patient_id = '{search_query}'
                    OR d.room_number = '{search_query}'
            """
            # Define the columns for the query results
            columns = [
                "Patient ID", "Patient Name", "Room Number", "Room Type",
                "Discharge Date", "Discharge Time", "Discharge Reason", "ICU Room"
            ]
            results = fetch_data(query, "discharged_patients", columns)

        elif search_type == "Emergency Patients":
            query = f"""
                SELECT 
                    ep.id AS 'ID', 
                    ep.name AS 'Patient Name', 
                    ep.contact_no AS 'Contact No', 
                    ep.address AS 'Address', 
                    ep.blood_type AS 'Blood Type', 
                    r.room_number AS 'Room Number', 
                    s.staff_name AS 'Assigned Doctor', 
                    ep.admission_date AS 'Admission Date'
                FROM emergency_patients ep
                LEFT JOIN rooms r ON ep.room_id = r.id
                LEFT JOIN staff s ON ep.doctor_id = s.id
                WHERE ep.name LIKE '%{search_query}%' 
                    OR ep.id = '{search_query}'
                    OR ep.contact_no = '{search_query}'
            """
            # Define the columns for the query results
            columns = [
                "ID", "Patient Name", "Contact No", "Address", "Blood Type",
                "Room Number", "Assigned Doctor", "Admission Date"
            ]
            results = fetch_data(query, "emergency_patients", columns)

        elif search_type == "Ambulance Service":
            query = f"""
                SELECT 
                    a.id AS 'Service ID', 
                    a.patient_name AS 'Patient Name', 
                    a.address AS 'Address', 
                    a.blood_type AS 'Blood Type', 
                    am.ambulance_number AS 'Ambulance Number', 
                    a.dispatch_time AS 'Dispatch Time', 
                    a.return_time AS 'Return Time'
                FROM ambulance_service a
                LEFT JOIN ambulances am ON a.ambulance_id = am.id
                WHERE a.patient_name LIKE '%{search_query}%' 
                    OR a.id = '{search_query}'
                    OR am.ambulance_number = '{search_query}'
            """
            # Define the columns for the query results
            columns = [
                "Service ID", "Patient Name", "Address", "Blood Type",
                "Ambulance Number", "Dispatch Time", "Return Time"
            ]
            results = fetch_data(query, "ambulance_service", columns)

        elif search_type == "Rooms":
            query = f"""
                SELECT 
                    r.id AS 'Room ID', 
                    r.room_number AS 'Room Number', 
                    r.room_type AS 'Room Type', 
                    r.availability AS 'Status', 
                    r.patient_id AS 'Patient ID'
                FROM rooms r
                WHERE r.room_number LIKE '%{search_query}%' 
                    OR r.id = '{search_query}'
                    OR r.patient_id = '{search_query}'
            """
            # Define the columns for the query results
            columns = ["Room ID", "Room Number", "Room Type", "Status", "Patient ID"]
            results = fetch_data(query, "rooms", columns)

        elif search_type == "Inventory":
            query = f"""
                SELECT 
                    i.id AS 'Item ID', 
                    i.item_name AS 'Item Name', 
                    i.quantity AS 'Quantity', 
                    i.expiry_date AS 'Expiry Date'
                FROM inventory i
                WHERE i.item_name LIKE '%{search_query}%' 
                    OR i.id = '{search_query}'
            """
            # Define the columns for the query results
            columns = ["Item ID", "Item Name", "Quantity", "Expiry Date"]
            results = fetch_data(query, "inventory", columns)

        elif search_type == "Staff":
            query = f"""
                SELECT 
                    s.id AS 'Staff ID', 
                    s.staff_name AS 'Staff Name', 
                    s.role AS 'Role', 
                    s.shift AS 'Shift'
                FROM staff s
                WHERE s.staff_name LIKE '%{search_query}%' 
                    OR s.id = '{search_query}'
            """
            # Define the columns for the query results
            columns = ["Staff ID", "Staff Name", "Role", "Shift"]
            results = fetch_data(query, "staff", columns)

        # Display the search results
        if not results.empty:
            st.success(f"Found {len(results)} matching records!")
            st.dataframe(results)
        else:
            st.warning("No matching records found.")

# ------------------ Schedule and View Appointments ------------------
def schedule_appointment():
    """
    Schedule Appointment: Accessible to Admin, Doctor, Receptionist, and Nurse.
    """
    st.markdown('<div class="header-lightblue"><h3>📅 Schedule Appointment</h3></div>', unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])

    # Fetch patient names
    patient_data = fetch_data("SELECT id, name FROM patients", "patients", columns=["id", "name"])

    if patient_data.empty:
        st.warning("No patients found. Please add patients first.")
        return

    # Select patient
    patient_name = st.selectbox("Select Patient", patient_data["name"])

    # Fetch unique departments from the doctor table
    department_data = fetch_data("SELECT DISTINCT department FROM doctor", "doctor", columns=["Department"])

    if department_data.empty:
        st.warning("No departments found. Please add doctors first.")
        return

    # Select department
    department = st.selectbox("Select Department", department_data["Department"])

    # Fetch doctors and shifts in the selected department
    query = f"""
        SELECT s.staff_name AS doctor_name, s.shift
        FROM doctor d
        JOIN staff s ON d.staff_id = s.id
        WHERE d.department = '{department}'
    """
    doctor_data = fetch_data(query, "doctor", columns=["Doctor Name", "Shift"])

    if doctor_data.empty:
        st.warning(f"No doctors found in the {department} department.")
        return

    # Select doctor
    doctor_name = st.selectbox("Select Doctor", doctor_data["Doctor Name"])

    # Fetch the shift for the selected doctor
    shift = doctor_data[doctor_data["Doctor Name"] == doctor_name]["Shift"].iloc[0]

    # Input appointment date and time
    appointment_date = st.date_input("Appointment Date*")
    appointment_time = st.time_input("Appointment Time*")

    if st.button("Schedule Appointment"):
        # Insert appointment data
        insert_data(
            """
            INSERT INTO appointments (patient_name, doctor_name, appointment_date, appointment_time)
            VALUES (%s, %s, %s, %s)
            """,
            (patient_name, doctor_name, appointment_date, appointment_time)
        )
        st.success("Appointment scheduled successfully!")


def view_appointments():
    """
    View Appointments: Accessible to Admin, Doctor, Receptionist, and Nurse.
    """
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse","Patient"])
    st.subheader("📅 Appointment Records")

    # Fetch appointment data with department and shift from the doctor and staff tables
    query = """
        SELECT a.id AS 'Appointment ID', 
               a.patient_name AS 'Patient Name', 
               s.staff_name AS 'Doctor Name', 
               d.department AS 'Department', 
               s.shift AS 'Shift', 
               a.appointment_date AS 'Appointment Date', 
               a.appointment_time AS 'Appointment Time',
               a.created_at AS 'Created At'
        FROM appointments a
        JOIN staff s ON a.doctor_name = s.staff_name  -- Join appointments with staff using doctor_name
        JOIN doctor d ON s.id = d.staff_id  -- Join staff with doctor using staff_id
    """
    columns = ["Appointment ID", "Patient Name", "Doctor Name", "Department", "Shift", "Appointment Date",
               "Appointment Time", "Created At"]
    df = fetch_data(query, "appointments", columns)

    if df.empty:
        st.info("No appointment records found.")
    else:
        # Display appointment records
        st.dataframe(df)

        # Add a download button for exporting the appointment data
        if st.button("📥 Download Appointment Records as CSV"):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="appointment_records.csv",
                mime="text/csv"
            )

# ------------------ Inventory Management Section ------------------
def manage_inventory():
    check_user_role(["Admin", "Doctor", "Nurse"])
    st.subheader("💊 Inventory Management")
    item_name = st.text_input("Item Name")
    quantity = st.number_input("Quantity", min_value=0)
    expiry_date = st.date_input("Expiry Date")
    if st.button("Add Item"):
        insert_data("INSERT INTO inventory (item_name, quantity, expiry_date) VALUES (%s, %s, %s)",
                    (item_name, quantity, expiry_date))
        st.success("Item Added to Inventory!")


def view_inventory():
    st.subheader("💊 Inventory Records")
    check_user_role(["Admin", "Doctor", "Nurse","Receptionist"])

    # Define all 5 columns to match the inventory table structure
    columns = ["Item ID", "Item Name", "Quantity", "Expiry Date", "Created At"]

    # Fetch data from the inventory table
    df = fetch_data("SELECT * FROM inventory", "inventory", columns)

    if df.empty:
        st.info("No inventory records found.")
    else:
        # Display the DataFrame
        st.dataframe(df)

        # Add a download button for exporting the inventory data
        if st.button("📥 Download Inventory as CSV"):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="inventory_records.csv",
                mime="text/csv"
            )

# ------------------ Staff Management Section ------------------
def manage_staff():
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])
    st.subheader("👨‍⚕️ Staff Management")
    staff_name = st.text_input("Staff Name")
    role = st.selectbox("Role", ["Doctor", "Nurse", "Receptionist", "Admin"])
    shift = st.selectbox("Shift", ["Morning", "Afternoon", "Night"])
    if st.button("Add Staff"):
        insert_data("INSERT INTO staff (staff_name, role, shift) VALUES (%s, %s, %s)",
                    (staff_name, role, shift))
        st.success("Staff Added Successfully!")


def view_staff():
    st.subheader("👨‍⚕️ Staff Records")
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])
    # Define all 5 columns to match the query result
    columns = ["Staff ID", "Staff Name", "Role", "Shift", "Created At"]

    # Fetch data from the staff table
    df = fetch_data("SELECT * FROM staff", "staff", columns)

    if df.empty:
        st.info("No staff records found.")
    else:
        # Display the DataFrame
        st.dataframe(df)


# ------------------ Patient History Section -----------------
def view_patient_history():
    """
    Enhanced Patient History Functionality with discharge details, room allocation details, emergency history, and medicine/quantity.
    """
    st.subheader("📜 Patient History")
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])

    # Search Box for Filtering Patients
    search_query = st.text_input("Search by Patient Name, ID, Medicine, or Quantity", "")

    # SQL query to get combined patient history
    query = """
        SELECT 
            p.id AS 'Patient ID',
            p.name AS 'Patient Name',
            p.dob AS 'Date of Birth',
            p.contact_no AS 'Contact No',
            p.consultant_name AS 'Consultant',
            p.gender AS 'Gender',
            p.department AS 'Department',
            p.diseases AS 'Disease',
            p.fees AS 'Fees',
            p.medicine AS 'Medicine',
            p.quantity AS 'Quantity',
            GROUP_CONCAT(DISTINCT b.bill_no) AS 'Bill Numbers',
            GROUP_CONCAT(DISTINCT b.total_amount) AS 'Bill Amounts',
            GROUP_CONCAT(DISTINCT r.room_number) AS 'Room Numbers',
            GROUP_CONCAT(DISTINCT r.room_type) AS 'Room Types',
            GROUP_CONCAT(DISTINCT d.discharge_date) AS 'Discharge Dates',
            GROUP_CONCAT(DISTINCT d.discharge_reason) AS 'Discharge Reasons',
            GROUP_CONCAT(DISTINCT ep.admission_date) AS 'Emergency Admission Dates',
            GROUP_CONCAT(DISTINCT ep.blood_type) AS 'Emergency Blood Types',
            GROUP_CONCAT(DISTINCT s.staff_name) AS 'Assigned Doctors'  # Fetch doctor names from staff table
        FROM 
            patients p
        LEFT JOIN 
            bill_details b ON p.id = b.patient_id
        LEFT JOIN 
            rooms r ON p.id = r.patient_id
        LEFT JOIN 
            discharged_patients d ON p.id = d.patient_id
        LEFT JOIN 
            emergency_patients ep ON p.id = ep.id
        LEFT JOIN 
            doctor doc ON p.consultant_name = doc.staff_id  # Join with doctor table
        LEFT JOIN 
            staff s ON doc.staff_id = s.id  # Join with staff table to get doctor names
        GROUP BY 
            p.id, p.name, p.dob, p.contact_no, p.consultant_name, p.gender, 
            p.department, p.diseases, p.fees, p.medicine, p.quantity
    """

    columns = [
        "Patient ID", "Patient Name", "Date of Birth", "Contact No",
        "Consultant", "Gender", "Department", "Disease", "Fees",
        "Medicine", "Quantity", "Bill Numbers", "Bill Amounts",
        "Room Numbers", "Room Types", "Discharge Dates",
        "Discharge Reasons", "Emergency Admission Dates", "Emergency Blood Types",
        "Assigned Doctors"  # Added assigned doctors
    ]

    df = fetch_data(query, "patients", columns)

    if df.empty:
        st.info("No patient history records found.")
    else:
        # Clean and format data
        df = df.fillna('N/A')

        # Convert date format for Date of Birth
        if 'Date of Birth' in df.columns:
            df['Date of Birth'] = pd.to_datetime(df['Date of Birth'], errors='coerce').dt.strftime('%Y-%m-%d')

        # Convert date format for Discharge Dates
        if 'Discharge Dates' in df.columns:
            df['Discharge Dates'] = df['Discharge Dates'].apply(
                lambda x: ', '.join(
                    [pd.to_datetime(date, errors='coerce').strftime('%Y-%m-%d') for date in x.split(',') if
                     date != 'N/A']) if x != 'N/A' else 'N/A'
            )

        # Convert date format for Emergency Admission Dates
        if 'Emergency Admission Dates' in df.columns:
            df['Emergency Admission Dates'] = df['Emergency Admission Dates'].apply(
                lambda x: ', '.join(
                    [pd.to_datetime(date, errors='coerce').strftime('%Y-%m-%d') for date in x.split(',') if
                     date != 'N/A']) if x != 'N/A' else 'N/A'
            )

        # Apply Search Filter if Query is Entered
        if search_query:
            df = df[df.apply(
                lambda row: (
                        search_query.lower() in str(row['Patient ID']).lower() or
                        search_query.lower() in row['Patient Name'].lower() or
                        search_query.lower() in str(row['Medicine']).lower() or
                        search_query.lower() in str(row['Quantity']).lower() or
                        search_query.lower() in str(row['Assigned Doctors']).lower()
                # Added search for assigned doctors
                ), axis=1
            )]

        # Display the patient history data
        st.dataframe(df)

        # Add a download button for exporting the patient history
        if st.button("📥 Download Patient History as CSV"):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="patient_history.csv",
                mime="text/csv"
            )

# ------------------ Ambulance Service Section ------------------
def ambulance_service_section():
    st.subheader("🚑 Ambulance Service")
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])

    # Initialize 5 ambulances (run once)
    def initialize_ambulances():
        con = connection()
        cur = con.cursor()
        # Check if ambulances exist
        cur.execute("SELECT COUNT(*) FROM ambulances")
        if cur.fetchone()[0] == 0:
            # Create 5 ambulances
            for i in range(1, 6):
                cur.execute("INSERT INTO ambulances (ambulance_number, status) VALUES (%s, 'Available')",
                            (f"AMB-00{i}",))
            con.commit()

    initialize_ambulances()

    # Add tabs for Ambulance Service section
    ambulance_tabs = st.tabs(["Add Request & Dispatch", "View Status"])

    with ambulance_tabs[0]:
        st.markdown('<div class="header-lightblue"><h3>📝 Add Ambulance Request</h3></div>', unsafe_allow_html=True)
        patient_name = st.text_input("Patient Name*")
        address = st.text_area("Address*")
        blood_type = st.selectbox("Blood Type*", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])

        if st.button("Save Request"):
            if not patient_name or not address or not blood_type:
                st.error("Please fill all required fields (*)")
            else:
                # Save the request
                insert_data(
                    """
                    INSERT INTO ambulance_service (patient_name, address, blood_type)
                    VALUES (%s, %s, %s)
                    """,
                    (str(patient_name), str(address), str(blood_type))  # Convert to native Python types
                )
                st.success("Ambulance request saved successfully!")

        st.markdown('<div class="header-lightblue"><h3>🚨 Dispatch Ambulance</h3></div>', unsafe_allow_html=True)

        # Fetch saved requests without dispatched ambulances
        requests = fetch_data(
            "SELECT id, patient_name, address, blood_type FROM ambulance_service WHERE ambulance_id IS NULL",
            "ambulance_service",
            ["ID", "Patient Name", "Address", "Blood Type"]
        )

        if not requests.empty:
            request_options = {f"{row['Patient Name']} - {row['Address']}": row["ID"] for _, row in requests.iterrows()}
            selected_request = st.selectbox("Select Request to Dispatch", list(request_options.keys()))
            request_id = request_options.get(selected_request)

            if st.button("Dispatch Ambulance"):
                # Find an available ambulance
                available_ambulance = fetch_data(
                    "SELECT id, ambulance_number FROM ambulances WHERE status = 'Available' LIMIT 1",
                    "ambulances",
                    ["ID", "Ambulance Number"]
                )

                if not available_ambulance.empty:
                    ambulance_id = int(available_ambulance.iloc[0]["ID"])  # Convert to native Python int
                    ambulance_number = str(
                        available_ambulance.iloc[0]["Ambulance Number"])  # Convert to native Python str

                    # Update ambulance status and assign to request
                    insert_data(
                        "UPDATE ambulances SET status = 'On Service' WHERE id = %s",
                        (ambulance_id,)  # Pass as native Python int
                    )
                    insert_data(
                        "UPDATE ambulance_service SET ambulance_id = %s, dispatch_time = NOW() WHERE id = %s",
                        (ambulance_id, int(request_id))  # Convert request_id to native Python int
                    )
                    st.success(f"Ambulance {ambulance_number} dispatched successfully!")
                else:
                    st.warning("No ambulances available for dispatch!")
        else:
            st.info("No pending ambulance requests.")

    with ambulance_tabs[1]:
        st.markdown('<div class="header-lightblue"><h3>🚑 Ambulance Status</h3></div>', unsafe_allow_html=True)

        # Fetch all ambulances
        ambulances = fetch_data(
            "SELECT id, ambulance_number, status FROM ambulances",
            "ambulances",
            ["ID", "Ambulance Number", "Status"]
        )

        if not ambulances.empty:
            # Add countdown timer for ambulances on service
            for index, row in ambulances.iterrows():
                if row["Status"] == "On Service":
                    # Fetch dispatch time
                    dispatch_time = fetch_data(
                        f"SELECT dispatch_time FROM ambulance_service WHERE ambulance_id = {int(row['ID'])} ORDER BY dispatch_time DESC LIMIT 1",
                        # Convert to native Python int
                        "ambulance_service",
                        ["Dispatch Time"]
                    ).iloc[0, 0]

                    if dispatch_time:
                        # Calculate remaining time (10 minutes countdown)
                        remaining_time = 600 - (datetime.now() - dispatch_time).total_seconds()
                        if remaining_time > 0:
                            ambulances.at[
                                index, "Status"] = f"On Service (Returning in {int(remaining_time // 60)}:{int(remaining_time % 60):02d})"
                        else:
                            # Automatically mark ambulance as available after 10 minutes
                            insert_data(
                                "UPDATE ambulances SET status = 'Available' WHERE id = %s",
                                (int(row["ID"]),)  # Convert to native Python int
                            )
                            insert_data(
                                "UPDATE ambulance_service SET return_time = NOW() WHERE ambulance_id = %s AND return_time IS NULL",
                                (int(row["ID"]),)  # Convert to native Python int
                            )
                            ambulances.at[index, "Status"] = "Available"

            # Display ambulance status table
            st.dataframe(ambulances)
        else:
            st.info("No ambulances found.")

        # Display Ambulance Availability
        total_ambulances = 5
        available_ambulances = fetch_data(
            "SELECT COUNT(*) FROM ambulances WHERE status = 'Available'",
            "ambulances"
        ).iloc[0, 0]

        if available_ambulances == 0:
            st.error("No ambulances are available right now!")
        else:
            st.write(
                f"**Ambulance Availability:** {int(available_ambulances)} Available / {total_ambulances} Total")  # Convert to native Python int

        # View Ambulance Records
        st.markdown('<div class="header-lightblue"><h3>📋 View Ambulance Records</h3></div>', unsafe_allow_html=True)

        # Fetch all ambulance service records
        records = fetch_data(
            """
            SELECT 
                s.id AS 'Service ID',
                s.patient_name AS 'Patient Name',
                s.address AS 'Address',
                s.blood_type AS 'Blood Type',
                a.ambulance_number AS 'Ambulance Number',
                s.dispatch_time AS 'Dispatch Time',
                s.return_time AS 'Return Time'
            FROM 
                ambulance_service s
            LEFT JOIN 
                ambulances a ON s.ambulance_id = a.id
            """,
            "ambulance_service",
            ["Service ID", "Patient Name", "Address", "Blood Type", "Ambulance Number", "Dispatch Time", "Return Time"]
        )

        if records.empty:
            st.info("No ambulance service records found.")
        else:
            st.dataframe(records)


# ----------------Reports ------------------
def generate_pdf_report(data, title, filename):
    """Generate a PDF report from the given data with improved formatting."""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add title to the PDF
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=title, ln=True, align="C")
        pdf.ln(10)  # Add some space after the title

        # Set font for the table
        pdf.set_font("Arial", size=10)

        # Calculate column widths dynamically based on content
        col_widths = [pdf.get_string_width(str(col)) + 10 for col in data.columns]

        # Add table headers
        for i, col in enumerate(data.columns):
            pdf.cell(col_widths[i], 10, txt=col, border=1, align="C")
        pdf.ln()

        # Add table rows
        for index, row in data.iterrows():
            for i, col in enumerate(data.columns):
                pdf.cell(col_widths[i], 10, txt=str(row[col]), border=1, align="C")
            pdf.ln()

        # Save the PDF to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_file.name)
        return temp_file.name
    except Exception as e:
        st.error(f"Error generating PDF report: {e}")
        return None


def download_report(data, title, filename):
    """Generate and download a PDF report with improved error handling."""
    if not data.empty:
        pdf_file = generate_pdf_report(data, title, filename)
        if pdf_file:
            try:
                with open(pdf_file, "rb") as file:
                    st.download_button(
                        label="📥 Download Report",
                        data=file,
                        file_name=filename,
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Error downloading report: {e}")
            finally:
                # Clean up the temporary file
                import os
                os.unlink(pdf_file)
    else:
        st.warning("No data available to generate the report.")


def generate_reports():
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])
    """Generate reports with improved formatting and error handling."""
    st.subheader("📄 Generate Reports")
    report_type = st.selectbox("Select Report Type", [
        "Patient History", "Billing", "Staff", "Inventory", "Appointments",
        "Emergency Patients", "Rooms", "Doctors"
    ])

    try:
        if report_type == "Patient History":
            # Include medicine and quantity in the patient history report
            data = fetch_data("SELECT * FROM patients", "patients")
            download_report(data, "Patient History Report", "patient_history_report.pdf")

        elif report_type == "Billing":
            data = fetch_data("SELECT * FROM bill_details", "bill_details")
            download_report(data, "Billing Report", "billing_report.pdf")

        elif report_type == "Staff":
            data = fetch_data("SELECT * FROM staff", "staff")
            download_report(data, "Staff Report", "staff_report.pdf")

        elif report_type == "Inventory":
            data = fetch_data("SELECT * FROM inventory", "inventory")
            download_report(data, "Inventory Report", "inventory_report.pdf")

        elif report_type == "Appointments":
            data = fetch_data("SELECT * FROM appointments", "appointments")
            download_report(data, "Appointments Report", "appointments_report.pdf")

        elif report_type == "Emergency Patients":
            data = fetch_data("SELECT * FROM emergency_patients", "emergency_patients")
            download_report(data, "Emergency Patients Report", "emergency_patients_report.pdf")

        elif report_type == "Rooms":
            data = fetch_data("SELECT * FROM rooms", "rooms")
            download_report(data, "Rooms Report", "rooms_report.pdf")

        elif report_type == "Doctors":
            data = fetch_data("SELECT * FROM doctor", "doctor")
            download_report(data, "Doctors Report", "doctors_report.pdf")
    except Exception as e:
        st.error(f"Error fetching data for report generation: {e}")


# ------------------ Export Data Section ------------------
def export_data():
    check_user_role(["Admin","Doctor", "Receptionist", "Nurse"])
    try:
        st.subheader("📤 Export Data")

        # Dropdown to select data type
        data_type = st.selectbox("Select Data to Export", [
            "Patients", "Rooms", "Bills", "Appointments", "Staff", "Inventory",
            "Emergency Patients", "Discharged Patients", "Doctors"
        ])

        # Button to trigger export
        if st.button("Export to Excel"):
            # Define the downloads folder
            downloads_folder = str(Path.home() / "Downloads")

            # Mapping of data types to SQL queries and table names
            query_mapping = {
                "Patients": ("SELECT * FROM patients", "patients"),
                "Rooms": ("SELECT * FROM rooms", "rooms"),
                "Bills": ("SELECT * FROM bill_details", "bill_details"),  # Corrected table name
                "Appointments": ("SELECT * FROM appointments", "appointments"),
                "Staff": ("SELECT * FROM staff", "staff"),
                "Inventory": ("SELECT * FROM inventory", "inventory"),
                "Emergency Patients": ("SELECT * FROM emergency_patients", "emergency_patients"),
                "Discharged Patients": ("SELECT * FROM discharged_patients", "discharged_patients"),
                "Doctors": ("SELECT * FROM doctor", "doctor")  # Corrected table name
            }

            # Check if the selected data type is valid
            if data_type in query_mapping:
                query, table_name = query_mapping[data_type]

                # Fetch data from the database
                data = fetch_data(query, table_name)

                # Define the file path for the Excel file
                file_path = os.path.join(downloads_folder, f"{table_name}.xlsx")

                # Check if data is empty
                if data.empty:
                    st.warning(f"No data found for {data_type}. Export canceled.")
                    logging.warning(f"No data found for {data_type} during export.")
                else:
                    # Export data to Excel
                    data.to_excel(file_path, index=False)
                    st.success(f"{data_type} data exported successfully to {file_path}!")
                    logging.info(f"{data_type} data exported successfully to {file_path}.")
            else:
                st.error("Invalid data type selected.")
                logging.error(f"Invalid data type selected: {data_type}")
    except Exception as e:
        st.error(f"Error exporting data: {e}")
        logging.error(f"Error exporting data: {e}")

# ------------------ Streamlit UI ------------------
if 'startup_done' not in st.session_state:
    st.session_state["startup_done"] = False

# Show startup animation only once when the application starts
if not st.session_state["startup_done"]:
    startup_animation()
    st.session_state["startup_done"] = True

st.title("\U0001F3E5 Hospital Management System")

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Show passcode screen if not verified
if "passcode_verified" not in st.session_state:
    passcode = st.text_input("Enter Passcode", type="password", key="passcode_input")
    if st.button("Submit Passcode"):
        if check_passcode(passcode):
            st.session_state["passcode_verified"] = True
            st.rerun()
        else:
            st.error("Incorrect Passcode!")
            logging.warning("Incorrect passcode entered.")
    st.stop()


# Navigation Tabs in Sidebar
if st.session_state.get('authenticated'):
    if st.session_state['user_role'] == "Admin":
        menu = [
            "Dashboard", "Advanced Search", "Attendance Dashboard", "Doctor Section", "Manage Patients",
            "Emergency Unit", "Emergency Dashboard", "Room Info", "Billing", "Appointments", "Inventory",
            "Staff", "Patient History", "Ambulance Service", "Generate Reports", "Export Data", "Logout"
        ]
    elif st.session_state['user_role'] == "Doctor":
        menu = [
            "Dashboard", "Advanced Search", "Attendance Dashboard", "Doctor Section", "Manage Patients",
            "Emergency Unit", "Emergency Dashboard", "Room Info", "Appointments", "Patient History", "Logout"
        ]
    elif st.session_state['user_role'] == "Receptionist":
        menu = [
            "Dashboard", "Advanced Search", "Attendance Dashboard", "Doctor Section", "Emergency Unit",
            "Emergency Dashboard", "Appointments", "Billing", "Inventory", "Generate Reports", "Export Data", "Logout"
        ]
    elif st.session_state['user_role'] == "Patient":
        menu = [
            "Dashboard","Advanced Search","Doctor Section", "Emergency Unit", "Patient History",
            "Appointments", "Logout"
        ]
    elif st.session_state['user_role'] == "Nurse":
        menu = [
            "Dashboard", "Advanced Search", "Attendance Dashboard", "Doctor Section",
            "Manage Patients",
            "Emergency Unit", "Emergency Dashboard", "Room Info", "Appointments","Inventory", "Patient History","Generate Reports", "Export Data", "Logout"
        ]
else:
    menu = ["Login", "Register"]

# Initialize session state for active tab
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = menu[0]

# Sidebar layout
with st.sidebar:
    st.markdown("### Navigation")
    for tab in menu:
        if st.button(tab, key=tab):
            st.session_state["active_tab"] = tab

#------------------Main content based on the active tab-------------
choice = st.session_state["active_tab"]

if choice == "Login":
    st.subheader("\U0001F512 User Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_user(username, password):
            st.rerun()  # Rerun the app to reflect the changes
        else:
            st.error("Invalid Credentials!")
            logging.warning(f"Failed login attempt for username: {username}")


elif choice == "Dashboard":
    access_control()
    show_dashboard()


elif choice == "Register":
    st.subheader("\U0001F4DD New User Registration")
    new_username = st.text_input("Create Username")
    new_password = st.text_input("Create Password", type="password")
    full_name = st.text_input("Full Name")
    user_role = st.selectbox("Role", ["Admin", "Doctor", "Patient", "Receptionist", "Nurse"])  # Added "Nurse"
    if st.button("Register"):
        register_user(new_username, new_password, full_name, user_role)


elif choice == "Advanced Search":
    access_control()
    advanced_search()


elif choice == "Attendance Dashboard":
    access_control()
    attendance_dashboard()


elif choice == "Manage Patients":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Doctor", "Nurse"]:
        st.warning("Access Denied! This feature is only available to Admin, Doctors, and Nurses.")
        st.stop()

    patient_tabs = st.tabs(["Add Patient", "View Patients", "Discharge Patient", "View Discharged Patients"])

    with patient_tabs[0]:
        add_patient()  # Add Patient page

    with patient_tabs[1]:
        view_patients()  # View Patients page

    with patient_tabs[2]:
        discharge_patient()  # Call without arguments

    with patient_tabs[3]:
        view_discharged_patients()  # View Discharged Patients page


elif choice == "Emergency Unit":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Doctor", "Receptionist","Patient", "Nurse"]:  # Added "Nurse"
        st.warning("Access Denied! This feature is only available to Admin, Doctors, Receptionists, and Nurses.")
        st.stop()

    emergency_tabs = st.tabs([
        "Add Emergency Patient",
        "View Emergency Patients",
        "Discharge Emergency Patient",
        "View Discharged Emergency Patients"
    ])

    with emergency_tabs[0]:
        add_emergency_patient()  # Add Emergency Patient page

    with emergency_tabs[1]:
        view_emergency_patients()  # View Emergency Patients page

    with emergency_tabs[2]:
        discharge_patient()  # Corrected function call for discharging emergency patients

    with emergency_tabs[3]:
        view_discharged_patients()  # View Discharged Emergency Patients page


elif choice == "Emergency Dashboard":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Doctor", "Receptionist","Nurse"]:  # Added "Nurse"
        st.warning("Access Denied! This feature is only available to Admin, Doctors, Receptionists, and Nurses.")
        st.stop()
    emergency_dashboard()


elif choice == "Room Info":
    access_control()
    # Restrict access to Admin, Doctor, and Nurse only
    if st.session_state.get('user_role') not in ["Admin", "Doctor", "Nurse"]:
        st.warning("🚫 Access Denied! This feature is only available to Admin, Doctors, and Nurses.")
        st.stop()

    # Room Info Section with Tabs
    room_tabs = st.tabs(["🏨 Allocate Room", "📋 View Rooms", "🚪 Discharge Patient", "📜 View Discharged Patients"])

    with room_tabs[0]:
        allocate_room()  # Function to allocate room to patients

    with room_tabs[1]:
        view_rooms()  # Function to display available and booked rooms

    with room_tabs[2]:
        discharge_patient()  # Call without arguments

    with room_tabs[3]:
        view_discharged_patients()  # Function to display discharged patients


elif choice == "Billing":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Receptionist"]:
        st.warning("Access Denied! This feature is only available to Admin, Receptionists, and Patients.")
        st.stop()
    billing_tabs = st.tabs(["Add Bill", "View Bills"])
    with billing_tabs[0]:
        add_bill()
    with billing_tabs[1]:
        view_bills()


elif choice == "Appointments":
    access_control()
    # Only Admin, Doctor, Receptionist, Nurse, and Patient can access this feature
    if st.session_state['user_role'] not in ["Admin", "Doctor", "Receptionist", "Nurse", "Patient"]:
        st.warning(
            "Access Denied! This feature is only available to Admin, Doctors, Receptionists, Nurses, and Patients."
        )
        st.stop()

    # Add tabs for Appointments section
    appointment_tabs = st.tabs(["Schedule Appointment", "View Appointments"])

    with appointment_tabs[0]:
        schedule_appointment()  # Schedule Appointment page

    with appointment_tabs[1]:
        view_appointments()  # View Appointments page


elif choice == "Inventory":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Nurse", "Receptionist"]:
        st.warning("Access Denied! This feature is only available to Admin, Nurses, and Receptionists.")
        st.stop()
    inventory_tabs = st.tabs(["Add Item", "View Inventory"])
    with inventory_tabs[0]:
        manage_inventory()
    with inventory_tabs[1]:
        view_inventory()


elif choice == "Staff":
    access_control()
    if st.session_state['user_role'] != "Admin":
        st.warning("Access Denied! This feature is only available to Admin.")
        st.stop()
    staff_tabs = st.tabs(["Add Staff", "View Staff"])
    with staff_tabs[0]:
        manage_staff()
    with staff_tabs[1]:
        view_staff()


elif choice == "Patient History":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Doctor", "Patient", "Nurse"]:  # Added "Nurse"
        st.warning("Access Denied! This feature is only available to Admin, Doctors, Patients, and Nurses.")
        st.stop()
    view_patient_history()


elif choice == "Ambulance Service":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Doctor", "Receptionist"]:
        st.warning("Access Denied! This feature is only available to Admin, Doctors, and Receptionists.")
        st.stop()
    ambulance_service_section()


elif choice == "Generate Reports":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Nurse", "Receptionist"]:
        st.warning("Access Denied! This feature is only available to Admin, Nurses, and Receptionists.")
        st.stop()
    generate_reports()


elif choice == "Export Data":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Nurse", "Receptionist"]:
        st.warning("Access Denied! This feature is only available to Admin, Nurses, and Receptionists.")
        st.stop()
    export_data()


elif choice == "Doctor Section":
    access_control()
    doctor_section()

elif choice == "Logout":
    if st.session_state.get('authenticated'):
        logout()
        st.session_state["startup_done"] = False  # Reset startup animation flag
        st.rerun()
    else:
        st.info("Login Session Terminated")
#------------------- Display Message When Not Authenticated ------------------
if not st.session_state['authenticated']:
    st.info("Please login to access and use the Hospital Management System features.")
