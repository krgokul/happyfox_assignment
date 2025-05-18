from email.utils import parsedate_to_datetime
from db import crud
from db.database import SessionLocal, engine
from db.models import Base, Email, Label
from utils import get_gmail_service

USER_ID = "me"
MAX_RESULTS = 10


def fetch_label_lists(service):
    print("Fetching labels...")
    try:
        results = service.users().labels().list(userId=USER_ID).execute()
        labels = results.get("labels", [])
        print(f"Fetched {len(labels)} labels from Gmail.")
        return [{"id": label.get("id"), "name": label.get("name")} for label in labels]
    except Exception as e:
        print(f"Error fetching label lists: {e}")
        return []


def fetch_email_lists(service):
    print("Fetching emails...")

    def parse_message(msg):
        headers = msg.get("payload", {}).get("headers", [])
        data = {h["name"].lower(): h["value"] for h in headers}
        try:
            date_received = parsedate_to_datetime(data.get("date", ""))
        except Exception as e:
            print(f"Warning: Failed to parse date '{data.get('date', '')}': {e}")
            date_received = None

        return {
            "id": msg["id"],
            "thread_id": msg["threadId"],
            "subject": data.get("subject", ""),
            "sender": data.get("from", ""),
            "recepient": data.get("to", ""),
            "date_received": date_received,
        }

    try:
        results = service.users().messages().list(userId=USER_ID, maxResults=MAX_RESULTS).execute()
        messages = results.get("messages", [])
        print(f"Fetched {len(messages)} messages from Gmail.")
    except Exception as e:
        print(f"Error fetching email lists: {e}")
        return []

    records_to_insert = []
    for message in messages:
        try:
            msg = service.users().messages().get(userId=USER_ID, id=message["id"]).execute()
            data = parse_message(msg)
            records_to_insert.append(data)
        except Exception as e:
            print(f"Error fetching message {message['id']}: {e}")

    return records_to_insert


def main():
    print(f"{'='*10} Gmail fetch and DB update process started {'='*10}")

    db = SessionLocal()
    service = get_gmail_service()

    labels = fetch_label_lists(service)
    if labels:
        crud.insert_or_replace(db=db, model=Label, data=labels)
        print("Inserted/Updated labels in the database.")
    else:
        print("No labels to update.")

    # Phase 2: Fetch and insert emails
    emails = fetch_email_lists(service)
    if emails:
        crud.insert_or_replace(db=db, model=Email, data=emails)
        print("Inserted/Updated emails in the database.")
    else:
        print("No emails to update.")



if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    main()
