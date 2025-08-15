"""
Simple Model Examples - Ultra Easy ORM Usage

Shows how simple it is to define and use models with the new Active Record pattern.
No session management, no engine setup - just define models and use them!
"""

from sqlalchemy import Column, String, Text
from andamios_orm import Model


class Project(Model):
    """Simple Project model - inherits all ORM functionality"""
    __tablename__ = "projects"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    project_idea = Column(Text, nullable=False)
    status = Column(String(50), default="draft")


class Repository(Model):
    """Simple Repository model"""
    __tablename__ = "repositories"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    repo_type = Column(String(100))
    github_url = Column(String(500))


class Document(Model):
    """Simple Document model"""
    __tablename__ = "documents"
    
    name = Column(String(255), nullable=False)
    content = Column(Text)
    doc_type = Column(String(100))
    file_path = Column(String(500))


class Conversation(Model):
    """Simple Conversation model"""
    __tablename__ = "conversations"
    
    phase = Column(String(100), default="project_idea")
    messages = Column(Text)  # JSON stored as text for simplicity