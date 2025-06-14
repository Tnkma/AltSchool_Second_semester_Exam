""" Database models for the application.
This module defines the database models used in the application."""
from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Contact(Base):
    """Contact model to store user contact information."""
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100))
    message = Column(Text)

class Newsletter(Base):
    """Newsletter model to store email subscriptions."""
    __tablename__ = "newsletters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)

class Feedback(Base):
    """Feedback model to store user feedback."""
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100))
    feedback = Column(Text)