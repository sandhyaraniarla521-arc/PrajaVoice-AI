import os
import sqlite3
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="PrajaVoice AI",
    page_icon="🏛️",
    layout="wide",
)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "prajavoice.db")

DEPARTMENTS = {
    "Emergency Services": [
        "fire", "accident", "emergency", "ambulance",
        "ప్రమాదం", "అత్యవసరం", "మంటలు", "అంబులెన్స్",
    ],
    "Water Supply Department": [
        "water", "నీరు", "నీళ్లు", "drinking water",
        "water supply", "తాగునీరు", "మంచినీరు",
    ],
    "Roads & Infrastructure": [
        "road", "pothole", "street", "bridge",
        "రహదారి", "గుంతలు", "రోడ్డు", "వంతెన",
    ],
    "Sanitation Department": [
        "garbage", "waste", "drainage", "cleanliness",
        "చెత్త", "మురుగు", "పారిశుధ్యం", "కాలువ",
    ],
    "Electricity Department": [
        "electricity", "power", "current", " बिजली",
        "విద్యుత్", "కరెంట్", "విద్యుత్ సరఫరా",
    ],
}

STATUSES = ["Pending", "In Progress", "Resolved", "Rejected"]


# -------------------- DATABASE --------------------
def get_connection():
    return sqlite3.connect(DB_PATH, timeout=15)


def initialize_database():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                complaint_id TEXT UNIQUE NOT NULL,
                language TEXT NOT NULL,
                complaint TEXT NOT NULL,
                department TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                admin_note TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        # Add columns safely when opening a database created by the earlier version.
        columns = {
            row[1] for row in conn.execute("PRAGMA table_info(complaints)").fetchall()
        }
        if "admin_note" not in columns:
            conn.execute("ALTER TABLE complaints ADD COLUMN admin_note TEXT DEFAULT ''")
        if "updated_at" not in columns:
            conn.execute("ALTER TABLE complaints ADD COLUMN updated_at TEXT DEFAULT ''")
            conn.execute("UPDATE complaints SET updated_at = created_at WHERE updated_at = ''")


def classify_department(complaint):
    normalized = complaint.casefold()
    for department, keywords in DEPARTMENTS.items():
        if any(keyword.casefold() in normalized for keyword in keywords):
            return department
    return "General Administration"


def create_complaint(language, complaint):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    complaint_id = f"MVA-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"
    department = classify_department(complaint)
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO complaints
            (complaint_id, language, complaint, department, status,
             admin_note, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'Pending', '', ?, ?)
            """,
            (complaint_id, language, complaint, department, now, now),
        )
    return complaint_id, department


def fetch_complaint(complaint_id):
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM complaints WHERE complaint_id = ?",
            conn,
            params=(complaint_id,),
        )


def fetch_all_complaints():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM complaints ORDER BY id DESC", conn
        )


def change_complaint_status(complaint_id, status, admin_note):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE complaints
            SET status = ?, admin_note = ?, updated_at = ?
            WHERE complaint_id = ?
            """,
            (status, admin_note, now, complaint_id),
        )


def admin_password():
    # Set ADMIN_PASSWORD in Streamlit secrets or an environment variable.
    try:
        configured = st.secrets.get("ADMIN_PASSWORD", "")
    except Exception:
        configured = ""
    return configured or os.environ.get("ADMIN_PASSWORD", "")


initialize_database()


# -------------------- HEADER / NAVIGATION --------------------
st.title("🏛️ PrajaVoice AI")
st.subheader("Telangana Smart Grievance Assistant")
st.write(
    "A demonstration platform for submitting, categorizing and tracking "
    "public grievances in Telugu and English."
)

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📝 Submit Complaint", "🔍 Track Complaint", "🔐 Admin Login"],
)


# -------------------- HOME --------------------
if page == "🏠 Home":
    st.header("Welcome to PrajaVoice AI")
    df = fetch_all_complaints()
    total = len(df)
    pending = int((df["status"] == "Pending").sum()) if total else 0
    progress = int((df["status"] == "In Progress").sum()) if total else 0
    resolved = int((df["status"] == "Resolved").sum()) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Complaints", total)
    c2.metric("Pending", pending)
    c3.metric("In Progress", progress)
    c4.metric("Resolved", resolved)

    st.subheader("Our Services")
    st.markdown(
        """
        - 📝 Submit a public grievance in English or Telugu
        - 🏢 Automatically suggest a department using keywords
        - 🆔 Generate a unique complaint reference
        - 🔍 Track a complaint using its reference ID
        - 🔐 Admin dashboard to review and update complaint status
        - 📊 View department-wise complaint reports
        """
    )
    st.info(
        "Demonstration only: this application is not connected to Telangana "
        "government systems and does not send complaints to government offices."
    )


# -------------------- SUBMIT COMPLAINT --------------------
elif page == "📝 Submit Complaint":
    st.header("📝 Submit Your Complaint")
    language = st.selectbox("Select Language", ["English", "తెలుగు"])
    prompt = (
        "Describe your public grievance..."
        if language == "English"
        else "మీ సమస్యను ఇక్కడ వివరించండి..."
    )
    complaint = st.text_area("Enter your complaint", placeholder=prompt, height=160)

    if st.button("Submit Complaint", type="primary"):
        if not complaint.strip():
            st.warning("Please enter your complaint.")
        elif len(complaint.strip()) < 8:
            st.warning("Please provide a little more detail about the problem.")
        else:
            complaint_id, department = create_complaint(language, complaint.strip())
            st.success("Complaint saved successfully in this demonstration app.")
            st.markdown(f"**Complaint ID:** `{complaint_id}`")
            st.write("**Suggested Department:**", department)
            st.write("**Language:**", language)
            st.write("**Initial Status:** Pending")
            st.warning("Save your Complaint ID. You will need it to track this record.")
            st.caption(
                "This confirmation means the record was saved locally; it does not "
                "mean a government department received it."
            )


# -------------------- TRACK COMPLAINT --------------------
elif page == "🔍 Track Complaint":
    st.header("🔍 Track Your Complaint")
    complaint_id = st.text_input(
        "Enter your Complaint ID",
        placeholder="Example: MVA-20261103-ABC123",
    )
    if st.button("Track Complaint"):
        if not complaint_id.strip():
            st.warning("Please enter a Complaint ID.")
        else:
            result = fetch_complaint(complaint_id.strip().upper())
            if result.empty:
                st.error("Complaint ID not found. Check the ID and try again.")
            else:
                row = result.iloc[0]
                st.success("Complaint found!")
                st.write("**Complaint ID:**", row["complaint_id"])
                st.write("**Department:**", row["department"])
                st.write("**Language:**", row["language"])
                st.write("**Complaint:**", row["complaint"])
                st.write("**Submitted:**", row["created_at"])
                st.write("**Last Updated:**", row["updated_at"])
                st.subheader("Current Status")
                status = row["status"]
                if status == "Resolved":
                    st.success("✅ Resolved")
                elif status == "In Progress":
                    st.info("🔄 In Progress")
                elif status == "Rejected":
                    st.error("❌ Rejected")
                else:
                    st.warning("⏳ Pending")
                if row.get("admin_note"):
                    st.write("**Department/Admin Note:**", row["admin_note"])


# -------------------- ADMIN --------------------
elif page == "🔐 Admin Login":
    st.header("🔐 Admin Portal")
    if not st.session_state.get("admin_logged_in", False):
        configured_password = admin_password()
        if not configured_password:
            st.error(
                "Admin password is not configured. Set ADMIN_PASSWORD in "
                ".streamlit/secrets.toml or your environment before using this page."
            )
        password = st.text_input("Admin Password", type="password")
        if st.button("Login", type="primary"):
            if configured_password and password == configured_password:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Incorrect password or admin password not configured.")
    else:
        st.success("Admin login successful.")
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()

        df = fetch_all_complaints()
        st.header("📊 Admin Dashboard")
        if df.empty:
            st.info("No complaints have been submitted yet.")
        else:
            total = len(df)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total", total)
            c2.metric("Pending", int((df["status"] == "Pending").sum()))
            c3.metric("In Progress", int((df["status"] == "In Progress").sum()))
            c4.metric("Resolved", int((df["status"] == "Resolved").sum()))

            st.subheader("Department-wise Reports")
            department_report = (
                df.groupby("department").size().reset_index(name="Complaints")
            )
            st.bar_chart(department_report.set_index("department"))

            st.subheader("All Complaints")
            visible_columns = [
                "complaint_id", "department", "language", "status",
                "created_at", "updated_at",
            ]
            st.dataframe(df[visible_columns], use_container_width=True, hide_index=True)

            st.subheader("Update Complaint Status")
            selected_id = st.selectbox("Select Complaint ID", df["complaint_id"].tolist())
            current = df.loc[df["complaint_id"] == selected_id, "status"].iloc[0]
            status_index = STATUSES.index(current) if current in STATUSES else 0
            new_status = st.selectbox(
                "Choose New Status", STATUSES, index=status_index
            )
            admin_note = st.text_area(
                "Optional update note",
                placeholder="Example: Inspection scheduled / Work completed.",
            )
            if st.button("Update Status", type="primary"):
                change_complaint_status(selected_id, new_status, admin_note.strip())
                st.success("Complaint status updated.")
                st.rerun()

            st.subheader("Download Reports")
            csv_data = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 Download Complaints CSV",
                data=csv_data,
                file_name="prajavoice_complaints.csv",
                mime="text/csv",
            )


# -------------------- FOOTER --------------------
st.divider()
st.caption("© 2026 PrajaVoice AI | Telangana Smart Grievance Assistant")
st.caption("Developed using Python, Streamlit and SQLite.")
