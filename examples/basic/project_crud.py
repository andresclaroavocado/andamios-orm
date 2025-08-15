"""
Project CRUD Example

Simple Project class with create/read/update/delete operations.
Uses async/await but keeps it simple.
"""

import asyncio
import uvloop
from sqlalchemy import Column, Integer, String, Text, JSON
from andamios_orm.models.base import Model, Base
from andamios_orm.core import get_session

# Initialize database
async def init_db():
    from andamios_orm.core import create_memory_engine
    from andamios_orm.core.session import init_db as init_core_db
    
    engine = create_memory_engine()
    init_core_db(engine)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Define Project model exactly like we have
class Project(Model):
    __tablename__ = "projects"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    project_idea = Column(Text, nullable=False)
    architecture = Column(JSON)
    status = Column(String(50), default="draft")

    def __repr__(self):
        return f"Project(id={self.id}, name='{self.name}')"

# Example usage
async def main():
    await init_db()
    
    print("🚀 Project CRUD Operations")
    print("=" * 30)

    # CREATE
    print("\n🏗️ CREATE: Instantiate → create → persisted")
    project = await Project.create(
        name="My Web App",
        description="A task management system",
        project_idea="Build a productivity tool",
        status="draft"
    )
    print(f"✅ Created project ID: {project.id}")
    print(f"   Name: {project.name}")
    print(f"   Status: {project.status}")

    # READ
    print("\n📖 READ: Retrieve project")
    found_project = await Project.read(project.id)
    print(f"✅ Read project: {found_project.name}")
    print(f"   Description: {found_project.description}")
    print(f"   Idea: {found_project.project_idea}")

    # UPDATE
    print("\n✏️ UPDATE: Modify project")
    updated_project = await Project.update(
        project.id,
        name="Updated Web App",
        status="active",
        description="An advanced task management system"
    )
    print(f"✅ Updated project: {updated_project.name}")
    print(f"   New status: {updated_project.status}")

    # DELETE
    print("\n🗑️ DELETE: Remove project")
    deleted = await Project.delete(project.id)
    print(f"✅ Project deleted: {deleted}")

    print("\n✨ All Project CRUD operations completed!")

if __name__ == "__main__":
    uvloop.run(main())