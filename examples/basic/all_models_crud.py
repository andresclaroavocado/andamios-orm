"""
Complete CRUD Examples - All 4 Models

This file demonstrates CRUD operations for all 4 models:
- Project
- Repository  
- Conversation
- Document

Each model uses the same simple pattern: Model.create/read/update/delete
"""

import asyncio
import uvloop
from sqlalchemy import Column, Integer, String, Text, JSON
from andamios_orm.models.base import Model, Base

# Initialize database
async def init_db():
    from andamios_orm.core import create_memory_engine
    from andamios_orm.core.session import init_db as init_core_db
    
    engine = create_memory_engine()
    init_core_db(engine)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ============================================================================
# MODEL DEFINITIONS
# ============================================================================

class Project(Model):
    __tablename__ = "projects"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    project_idea = Column(Text, nullable=False)
    architecture = Column(JSON)
    status = Column(String(50), default="draft")

    def __repr__(self):
        return f"Project(id={self.id}, name='{self.name}')"

class Repository(Model):
    __tablename__ = "repositories"
    
    project_id = Column(Integer, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    repo_type = Column(String(100))
    github_url = Column(String(500))

    def __repr__(self):
        return f"Repository(id={self.id}, name='{self.name}')"

class Conversation(Model):
    __tablename__ = "conversations"
    
    project_id = Column(Integer, index=True)
    phase = Column(String(100), default="project_idea")
    messages = Column(JSON, default=list)

    def __repr__(self):
        return f"Conversation(id={self.id}, phase='{self.phase}')"

class Document(Model):
    __tablename__ = "documents"
    
    project_id = Column(Integer, index=True)
    name = Column(String(255), nullable=False)
    content = Column(Text)
    doc_type = Column(String(100))
    file_path = Column(String(500))

    def __repr__(self):
        return f"Document(id={self.id}, name='{self.name}')"

# ============================================================================
# CRUD EXAMPLES
# ============================================================================

async def project_crud_example():
    print("🚀 PROJECT CRUD Operations")
    print("=" * 30)

    # CREATE
    project = await Project.create(
        name="My Web App",
        description="A task management system",
        project_idea="Build a productivity tool",
        status="draft"
    )
    print(f"✅ Created project: {project.name} (ID: {project.id})")

    # READ
    found_project = await Project.read(project.id)
    print(f"✅ Read project: {found_project.name}")

    # UPDATE
    updated_project = await Project.update(
        project.id,
        name="Updated Web App",
        status="active"
    )
    print(f"✅ Updated project: {updated_project.name}")

    # DELETE
    deleted = await Project.delete(project.id)
    print(f"✅ Project deleted: {deleted}")
    
    return project.id

async def repository_crud_example(project_id):
    print("\n🚀 REPOSITORY CRUD Operations")
    print("=" * 35)

    # CREATE
    repo = await Repository.create(
        project_id=project_id,
        name="backend-api",
        description="Main backend API service",
        repo_type="backend",
        github_url="https://github.com/user/backend-api"
    )
    print(f"✅ Created repository: {repo.name} (ID: {repo.id})")

    # READ
    found_repo = await Repository.read(repo.id)
    print(f"✅ Read repository: {found_repo.name}")

    # UPDATE
    updated_repo = await Repository.update(
        repo.id,
        name="advanced-backend-api",
        repo_type="microservice"
    )
    print(f"✅ Updated repository: {updated_repo.name}")

    # DELETE
    deleted = await Repository.delete(repo.id)
    print(f"✅ Repository deleted: {deleted}")

async def conversation_crud_example(project_id):
    print("\n🚀 CONVERSATION CRUD Operations")
    print("=" * 38)

    # CREATE
    conversation = await Conversation.create(
        project_id=project_id,
        phase="requirements",
        messages=[
            {"role": "user", "content": "Let's start building"},
            {"role": "assistant", "content": "Great! What's your project idea?"}
        ]
    )
    print(f"✅ Created conversation: {conversation.phase} (ID: {conversation.id})")

    # READ
    found_conversation = await Conversation.read(conversation.id)
    print(f"✅ Read conversation: {found_conversation.phase}")

    # UPDATE
    updated_conversation = await Conversation.update(
        conversation.id,
        phase="design",
        messages=[
            {"role": "user", "content": "Let's start building"},
            {"role": "assistant", "content": "Great! What's your project idea?"},
            {"role": "user", "content": "Now let's design the architecture"}
        ]
    )
    print(f"✅ Updated conversation: {updated_conversation.phase}")

    # DELETE
    deleted = await Conversation.delete(conversation.id)
    print(f"✅ Conversation deleted: {deleted}")

async def document_crud_example(project_id):
    print("\n🚀 DOCUMENT CRUD Operations")
    print("=" * 32)

    # CREATE
    document = await Document.create(
        project_id=project_id,
        name="API Documentation",
        content="# API Specification\n\nThis document describes the REST API endpoints...",
        doc_type="api_spec",
        file_path="/docs/api-spec.md"
    )
    print(f"✅ Created document: {document.name} (ID: {document.id})")

    # READ
    found_document = await Document.read(document.id)
    print(f"✅ Read document: {found_document.name}")

    # UPDATE
    updated_document = await Document.update(
        document.id,
        name="Complete API Documentation",
        doc_type="complete_api_spec"
    )
    print(f"✅ Updated document: {updated_document.name}")

    # DELETE
    deleted = await Document.delete(document.id)
    print(f"✅ Document deleted: {deleted}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    await init_db()
    
    print("🎯 ALL MODELS CRUD DEMONSTRATION")
    print("=" * 50)
    print("Demonstrating CRUD operations for all 4 models:")
    print("Project → Repository → Conversation → Document")
    print("=" * 50)

    # Run CRUD examples for all models
    project_id = await project_crud_example()
    await repository_crud_example(project_id)
    await conversation_crud_example(project_id)  
    await document_crud_example(project_id)

    print("\n✨ ALL CRUD operations completed for all 4 models!")
    print("🎉 Project, Repository, Conversation, and Document examples finished!")

if __name__ == "__main__":
    uvloop.run(main())