"""
Project CRUD Example

Complete Create, Read, Update, Delete operations for Project model.
Narrative: instantiate ORM object → create → persisted in DuckDB → read/update/delete
"""

import asyncio
import uvloop
from andamios_orm import create_memory_engine, sessionmaker, AsyncSession

# Import existing models
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../legacy'))
from database.models import Base, Project

async def main():
    engine = create_memory_engine()
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        print("🚀 Project CRUD Operations")
        print("=" * 30)
        
        # CREATE
        print("\n📝 CREATE: Instantiate → create → persisted in DuckDB")
        project = Project(
            name="My Web App",
            description="A task management system",
            project_idea="Build a productivity tool",
            status="draft"
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        print(f"✅ Created project ID: {project.id}, Name: {project.name}")
        
        # READ
        print(f"\n📖 READ: Retrieve project from DuckDB")
        found_project = await session.get(Project, project.id)
        print(f"✅ Read project: {found_project.name}")
        print(f"   Description: {found_project.description}")
        print(f"   Status: {found_project.status}")
        
        # UPDATE
        print(f"\n✏️ UPDATE: Modify and persist changes")
        found_project.name = "Updated Web App"
        found_project.status = "active"
        found_project.description = "An advanced task management system"
        await session.commit()
        print(f"✅ Updated project: {found_project.name}")
        print(f"   New status: {found_project.status}")
        
        # DELETE
        print(f"\n🗑️ DELETE: Remove from DuckDB")
        project_id = found_project.id
        await session.delete(found_project)
        await session.commit()
        
        # Verify deletion
        deleted_project = await session.get(Project, project_id)
        print(f"✅ Project deleted: {deleted_project is None}")
        
        print("\n✨ All Project CRUD operations completed!")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())