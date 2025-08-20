"""
Conversation model for Andamios ORM
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func

from .base import Model


class Conversation(Model):
    """Conversation model with async CRUD operations."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, index=True)
    phase = Column(String(100), default="project_idea")
    messages = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())