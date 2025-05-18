from requests import Session
from sqlalchemy import insert
from db.models import Label, Email


def insert_or_replace(db: Session, model, data):
    if isinstance(data, dict):
        data = [data]

    for record in data:
        stmt = insert(model.__table__).prefix_with("OR REPLACE").values(**record)
        db.execute(stmt)
    db.commit()


def select_email_records(db: Session, filter_clauses):
    return db.query(Email).filter(filter_clauses).all()


def fetch_labels(db: Session):
    return db.query(Label).all()
