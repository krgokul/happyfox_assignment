from sqlalchemy import TIMESTAMP, Column, String, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Email(Base):
    __tablename__ = "emails"

    id = Column(String, primary_key=True)
    thread_id = Column(String)
    subject = Column(String)
    sender = Column(String)
    recepient = Column(String)
    date_received = Column(TIMESTAMP)


class Label(Base):
    __tablename__ = "labels"

    id = Column(String, primary_key=True)
    name = Column(String)
