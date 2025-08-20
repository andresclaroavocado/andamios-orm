"""
Repository model for Andamios ORM
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from .base import Model


class Repository(Model):
    """Repository model with async CRUD operations."""
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    repo_type = Column(String(100))  # backend, frontend, docs, infrastructure
    github_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())