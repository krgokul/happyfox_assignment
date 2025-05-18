import json
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, not_, or_
from pydantic import ValidationError

from db import crud
from db.database import SessionLocal
from db.models import Email
from schema import RuleConfig
from utils import get_gmail_service

USER_ID = "me"


def modify_gmail_messages(
    gmail_service, message_ids, labels_to_add=None, labels_to_remove=None
):
    request_body = {
        "ids": message_ids,
        "addLabelIds": labels_to_add or [],
        "removeLabelIds": labels_to_remove or [],
    }

    try:
        gmail_service.users().messages().batchModify(
            userId=USER_ID, body=request_body
        ).execute()
        print(f"Modified {len(message_ids)} messages")
    except Exception as e:
        print(f"Failed to modify Gmail messages: {e}")


def build_rule_expression(rule):
    field = rule.get("field")
    predicate = rule.get("predicate")
    value = rule.get("value")
    unit = rule.get("unit")

    if not field or not predicate:
        print("Missing 'field' or 'predicate' in rule")
        return None

    column_attr = getattr(Email, field, None)
    if not column_attr:
        print(f"Invalid field: {field}")
        return None

    if field == "date_received":
        try:
            numeric_value = int(value)
        except (ValueError, TypeError):
            print(f"Invalid numeric value for date_received: {value}")
            return None

        current_time = datetime.now(timezone.utc)

        if unit == "days":
            target_time = current_time - relativedelta(days=numeric_value)
        elif unit == "months":
            target_time = current_time - relativedelta(months=numeric_value)
        else:
            print(f"Unsupported unit for date_received: {unit}")
            return None

        return (
            column_attr < target_time
            if predicate == "greater_than"
            else column_attr > target_time
        )

    if predicate == "equals":
        return column_attr == value
    elif predicate == "not_equals":
        return column_attr != value
    elif predicate == "contains":
        return column_attr.ilike(f"%{value}%")
    elif predicate == "does_not_contain":
        return not_(column_attr.ilike(f"%{value}%"))

    print(f"Unsupported predicate: {predicate}")
    return None


def combine_rule_expressions(rules, match):
    expressions = [build_rule_expression(rule) for rule in rules]
    print(f"Combining {len(expressions)} rule expressions with match='{match}'")
    return and_(*expressions) if match == "all" else or_(*expressions)


def parse_label_actions(db_session, action_definitions):
    labels = crud.fetch_labels(db_session)
    label_lookup = {label.name.strip().lower(): label.id for label in labels}

    labels_to_add = []
    labels_to_remove = []

    for action in action_definitions:
        action_type = action.get("type")

        if action_type == "move_message":
            destination = action.get("target", "").strip().lower()
            label_id = label_lookup.get(destination)
            if label_id:
                labels_to_add.append(label_id)
                print(f"Action: Move message to label '{destination}'")
            else:
                print(f"Label '{destination}' not found.")
        elif action_type == "mark_as_read":
            labels_to_remove.append("UNREAD")
            print("Action: Mark as read")
        elif action_type == "mark_as_unread":
            labels_to_add.append("UNREAD")
            print("Action: Mark as unread")

    return labels_to_add, labels_to_remove


def main():
    print(f"{'='*10} Validation {'='*10}")
    gmail_service = get_gmail_service()
    db_session = SessionLocal()

    try:
        with open("rules_config.json", "r") as rule_file:
            data = json.load(rule_file)
            rules_config_obj = RuleConfig(**data)
            rules_config = rules_config_obj.model_dump()
            print("Loaded and validated rules_config.json")
    except ValidationError as e:
        print("Invalid RuleConfig format.")
        for err in e.errors():
            print(f"Field: {err['loc']}, Error: {err['msg']}")
        return
    except FileNotFoundError:
        print("rules_config.json file not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing rules_config.json: {e}")
        return

    print(f"{'='*10} Rule Evaluation {'='*10}")

    rules = rules_config.get("rules", [])
    match = rules_config.get("match", "all")

    rule_expressions = combine_rule_expressions(rules, match)
    matched_emails = crud.select_email_records(db_session, rule_expressions)
    message_ids = [email.id for email in matched_emails]

    if not message_ids:
        print("No matching emails found")
        return

    print(f"Found {len(message_ids)} matching emails")

    print(f"{'='*10} Gmail Action {'='*10}")
    labels_to_add, labels_to_remove = parse_label_actions(
        db_session, rules_config.get("actions", [])
    )
    modify_gmail_messages(gmail_service, message_ids, labels_to_add, labels_to_remove)


if __name__ == "__main__":
    main()
