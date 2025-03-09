🚑 Hospital Management System (HMS)

🏥 A Comprehensive, Secure & Smart Healthcare Solution

Project By: YUVRAJ KUMAR GOND

📌 About The Project
The Hospital Management System (HMS) is a full-fledged healthcare management solution that automates and optimizes hospital operations, including:
✅ Patient Management 🏥
✅ Doctor & Staff Management 👨‍⚕️
✅ Appointments & Scheduling 📅
✅ Billing & Invoicing 💰
✅ Emergency & ICU Handling 🚨
✅ Data Security & Role-Based Access 🔐
✅ Medical Inventory Management 📦

This system is designed with efficiency, security, and scalability in mind, ensuring smooth hospital operations and seamless healthcare service delivery.

🚀 Key Features
🔹 General Features
✔ User Authentication & Role-Based Access Control (RBAC) 🔑
✔ Easy-to-Use Web Interface (Built with Streamlit) 🌐
✔ Secure MySQL Database for Storing Hospital Records 💾
✔ Automated ICU Bed Allocation & Emergency Patient Handling 🏥
✔ Billing System with Auto-Generated Invoices 🧾
✔ Real-Time Dashboard & Data Analytics 📊

🔹 Security Measures
✔ SHA-256 Encrypted Passwords 🔒
✔ User Activity Logging & Audit Trails 📝
✔ SQL Injection & XSS Prevention 🛡️
✔ Restricted Access to Critical Modules 🚫

🔹 Data Visualization & Reports
✔ Appointment & Patient Statistics 📈
✔ Revenue & Billing Trends 💹
✔ Real-Time ICU Utilization & Emergency Handling Metrics 🚨

🛠️ Technology Stack
Technology	Purpose
Python 🐍	Backend Logic
Streamlit 🌐	Web Application UI
MySQL 🛢️	Database Management
Plotly & Pandas 📊	Data Visualization & Analysis
MySQL-Connector 🔌	Database Connection
FPDF 📜	Report Generation
Python-Dotenv 🔐	Environment Variable Security

📂 Project Structure
bash
Copy
Edit
HospitalManagementSystem/
│-- HMS.py           # Main application code
│-- HMST.text        # Database schema (SQL)
│-- HDT.py           # Debugging & Testing clone of HMS.py
│-- requirements.txt # Dependencies list
│-- README.md        # Project Documentation (You are here!)
│-- /assets          # Icons, Images, and UI Resources

⚡ Installation & Setup
1️⃣ System Requirements
✔ Python 3.x
✔ MySQL Server (Installed & Running)
✔ Git Installed (For Version Control)

2️⃣ Clone the Repository
sh
Copy
Edit
git clone https://github.com/YuvrajKG/HospitalManagementSystem.git
cd HospitalManagementSystem

3️⃣ Install Required Dependencies
sh
Copy
Edit
pip install -r requirements.txt

4️⃣ Setup MySQL Database
Open MySQL Workbench or Command Line.
Execute the SQL script in HMST.text to create the database and tables.

5️⃣ Run the Application
sh
Copy
Edit
streamlit run HMS.py
✅ The Hospital Management System will launch in your web browser.

🧪 Debugging & Testing
Use the HDT.py file to test new features before deploying changes in HMS.py.

sh
Copy
Edit
python HDT.py

⚠️ Common Issues & Solutions
Issue	Possible Cause	Solution
Database Connection Error ❌	Incorrect credentials	Check .env file for database details
Module Not Found 📦	Missing dependencies	Run pip install -r requirements.txt
App Not Opening 🛑	Port already in use	Use streamlit run HMS.py --server.port=8502

🔮 Future Enhancements
✔ AI-Powered Patient Health Prediction 🤖
✔ Blockchain-Based Secure Medical Records 🔗
✔ Mobile App for Remote Access 📱
✔ Telemedicine & Video Consultation Integration 🎥

🎯 Contributing
Contributions are welcome! 🎉 If you’d like to improve this project:

Fork the repository
Create a new branch (feature-xyz)
Commit your changes
Push to GitHub
Create a Pull Request 🚀


📞 Contact
💡 Project By: YUVRAJ KUMAR GOND
🔗 GitHub Profile: https://github.com/YuvrajKG

If you find this project useful, consider giving it a ⭐ Star on GitHub! 🚀
