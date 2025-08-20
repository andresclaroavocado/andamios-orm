"""
Project model for Andamios ORM
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Sequence
from sqlalchemy.sql import func

from .base import Model


class Project(Model):
    """Project model with async CRUD operations."""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    project_idea = Column(Text, nullable=False)
    architecture = Column(JSON)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())