import os
import json
import datetime
import sys
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tabulate import tabulate

# Public-friendly scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

LAST_N_HOURS = 168


# ================= CATEGORIZATION =================
def categorize_email(email):
    subject = email.get('subject', '').lower()
    snippet = email.get('snippet', '').lower()
    sender = email.get('sender', '').lower()

    text = subject + " " + snippet

    easy_keywords = [
        'newsletter', 'promo', 'sale', 'deal', 'discount',
        'offer', 'digest', 'no-reply', 'unsubscribe'
    ]

    if any(k in text or k in sender for k in easy_keywords):
        return 'easy'

    hard_keywords = [
        'urgent', 'asap', 'important', 'deadline',
        'action required', 'verify', 'security alert',
        'password', 'login', 'account'
    ]

    if any(k in text for k in hard_keywords):
        return 'hard'

    return 'medium'


# ================= AUTH =================
def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            creds = Credentials.from_authorized_user_info(json.load(f), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


# ================= FETCH (WITH PAGINATION) =================
def fetch_emails(service):
    now = datetime.datetime.now(datetime.timezone.utc)
    start_time = now - datetime.timedelta(hours=LAST_N_HOURS)

    after_timestamp = int(start_time.timestamp())
    query = f'after:{after_timestamp} in:inbox'

    messages = []
    next_page_token = None

    while True:
        response = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=100,
            pageToken=next_page_token
        ).execute()

        messages.extend(response.get('messages', []))
        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break

    print(f"\n Found {len(messages)} emails\n")
    return messages


# ================= PROCESS =================
def process_email(service, msg_id):
    try:
        msg = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='metadata',
            metadataHeaders=['Subject', 'From', 'Date']
        ).execute()

        headers = msg.get('payload', {}).get('headers', [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        snippet = msg.get('snippet', '')

        email_data = {
            'subject': subject,
            'sender': sender,
            'snippet': snippet
        }

        category = categorize_email(email_data)

        return [sender, date, subject, category]

    except HttpError as error:
        print(f"\n Error: {error}")
        return None


# ================= MAIN =================
def main():
    print("=" * 50)
    print("Gmail Triage - Email Categorizer")
    print("=" * 50)

    if not os.path.exists(CREDENTIALS_FILE):
        print("credentials.json not found")
        return

    print("\n🔄 Connecting to Gmail...")
    service = get_gmail_service()
    print("Connected!\n")

    print(f"Fetching emails from last {LAST_N_HOURS} hours...\n")

    messages = fetch_emails(service)

    if not messages:
        print("❌ No emails found")
        return

    rows = []
    counts = {'easy': 0, 'medium': 0, 'hard': 0}

    total = len(messages)

    for i, msg in enumerate(messages):
        # ✅ SINGLE LINE PROGRESS
        sys.stdout.write(f"\r🚀 Processing Emails: {i+1}/{total}")
        sys.stdout.flush()

        data = process_email(service, msg['id'])

        if data:
            rows.append(data)
            counts[data[3]] += 1

    print()  # move to next line

    print("\n" + "=" * 50)
    print("EMAIL RESULTS")
    print("=" * 50)

    print(tabulate(rows, headers=["Sender", "Date", "Subject", "Category"]))

    print("\n SUMMARY")
    print("=" * 50)
    print(f"🟢 Easy:   {counts['easy']}")
    print(f"🟡 Medium: {counts['medium']}")
    print(f"🔴 Hard:   {counts['hard']}")
    print(f"TOTAL:     {sum(counts.values())}")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()