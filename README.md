# Setup and Usage Guide

A complete guide to authenticate with Google using OAuth 2.0 and interact with Gmail emails programmatically in Python.

---

## 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on **Select a project** at the top, then click **New Project**.
3. Enter a project name (e.g., `My Gmail API Project`) and click **Create**.

## 2. Enable Gmail API

1. In the Cloud Console, navigate to **APIs & Services > Library**.
2. Search for **Gmail API**.
3. Click on **Gmail API**, then click **Enable**.

## 3. Configure OAuth Consent Screen

1. Navigate to **APIs & Services > OAuth consent screen**.
2. Select **External** (or **Internal** if applicable) and click **Create**.
3. Fill out the required fields (App name, User support email, Developer contact info).
4. Save and continue.

## 4. Create OAuth 2.0 Credentials

1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials > OAuth Client ID**.
3. Select **Application type**: **Desktop app**.
4. Enter a name for your OAuth client (e.g., `Gmail API Client`).
5. Click **Create**.

## 5. Add Test Users to OAuth Consent Screen

When the app is in testing mode, only test users can authorize it.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Navigate to **APIs & Services > OAuth consent screen**.
3. Scroll down to the **Test users** section.
4. Click **+ Add users**.
5. Enter the email addresses (Google accounts) of users you want to allow access.
6. Click **Save and Continue**.

## 6. Download `client_secret.json`

1. After creation, you will see your client credentials.
2. Click **Download JSON** to download the `client_secret.json` file.
3. Save this file in project root directory.

## 7. Set Up Python Virtual Environment

```bash
python3 -m venv venv
```

## 8. Activate the virtual environment:

- On Linux/macOS:

```bash
source venv/bin/activate
```

- On Windows:

```bash
venv\Scripts\activate
```

## 9. Install the dependencies:

```bash
pip install -r requirements.txt
```

## 10. Running the Scripts

You have two Python scripts to interact with Gmail and your database:

- **`fetch_emails.py`**  
  This script requires OAuth authentication the first time you run it. It fetches emails from Gmail and updates them into your database.

- **`process_emails.py`**  
  This script reads fetched emails from the database, applies rules defined in `rule_config.json`, and performs actions via the Gmail REST API accordingly.

Run the fetch script (to authenticate and fetch emails):

```bash
python3 fetch_emails.py
```

Run the processing script (to process emails based on your rules):

```bash
python3 process_emails.py
```

## 11. Run Test Cases

```bash
python3 tests/test_fetch_emails.py
```

```bash
python3 tests/test_process_emails.py
```
