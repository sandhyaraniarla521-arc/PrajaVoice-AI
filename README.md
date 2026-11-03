# PrajaVoice AI — Telangana Smart Grievance Assistant

A Streamlit demonstration app for submitting, categorizing and tracking public grievances in English and Telugu.

## Features
- English and Telugu complaint input
- Keyword-based department categorization
- Unique complaint ID generation
- SQLite storage
- Complaint tracking
- Admin login and status updates
- Department-wise dashboard and CSV export

## Departments
- Emergency Services
- Water Supply Department
- Roads & Infrastructure
- Sanitation Department
- Electricity Department
- General Administration (fallback)

## Requirements
- Python 3.10 or later
- pip

## Run locally

1. Extract the project ZIP.
2. Open a terminal in the project folder.
3. Create and activate a virtual environment (recommended):

   Windows:
   ```bash
   py -m venv .venv
   .venv\\Scripts\\activate
   ```

   macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install packages:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure the admin password:
   - Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
   - Replace the example value with a strong password.
   - Do not upload `secrets.toml` to GitHub.

6. Start the application:
   ```bash
   streamlit run app.py
   ```

The SQLite database `prajavoice.db` is created automatically on first run.

## Deploy to Streamlit Community Cloud

1. Push the project files to a GitHub repository.
2. Open https://share.streamlit.io/ and sign in.
3. Choose the repository, branch and `app.py`.
4. In the app's settings, add a secret named `ADMIN_PASSWORD` with a strong value:
   ```toml
   ADMIN_PASSWORD = "replace-with-a-strong-password"
   ```
5. Deploy the app.

## Important deployment note
This is a demonstration project, not an official Telangana government service. It does not forward complaints to government departments. SQLite storage on cloud hosting may not be durable across restarts, redeployments or multiple instances. For a real public deployment, use a managed persistent database, secure authentication, backups, HTTPS, audit logs, privacy notices and an authorized government integration.

## Admin workflow
1. Open **Admin Login**.
2. Enter the password configured in Streamlit secrets or the `ADMIN_PASSWORD` environment variable.
3. Select a complaint ID.
4. Choose Pending, In Progress, Resolved or Rejected.
5. Optionally enter an update note and click **Update Status**.

## Department categorization
The app uses simple keyword matching, not an AI language model. Add or adjust words in `DEPARTMENTS` inside `app.py` to improve categorization. A complaint that matches no keyword is sent to General Administration.

## Project files
- `app.py` — main Streamlit application
- `requirements.txt` — Python dependencies
- `.streamlit/secrets.toml.example` — example admin password configuration
- `.gitignore` — excludes local secrets, database and Python cache
