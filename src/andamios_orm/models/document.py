"""
Document model for Andamios ORM
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from .base import Model


class Document(Model):
    """Document model with async CRUD operations."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, index=True)
    name = Column(String(255), nullable=False)
    content = Column(Text)
    doc_type = Column(String(100))  # architecture, api_spec, deployment, etc.
    file_path = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())