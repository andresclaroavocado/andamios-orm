"""
Simple CRUD Examples - Project Model

Basic Create, Read, Update, Delete operations using the Project model.
Each example shows how an ORM object created in memory gets saved to DuckDB.
"""

import asyncio
import uvloop
from andamios_orm import create_engine, sessionmaker, AsyncSession
from database.models import Base, Project


async def create_project_example():
    """Create a new project in DuckDB."""
    print("📝 Creating a new project...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create project object in memory
        project = Project(
            name="My Web App",
            description="A simple web application",
            project_idea="Build a task management system",
            status="active"
        )
        
        # Save to DuckDB
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        print(f"✅ Project created with ID: {project.id}")
        return project.id
    
    await engine.dispose()


async def read_project_example():
    """Read a project from DuckDB."""
    print("📖 Reading project...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # First create a project
        project = Project(name="Test Project", project_idea="Test idea")
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        # Read the project back
        found_project = await session.get(Project, project.id)
        print(f"📋 Found project: {found_project.name}")
        print(f"💡 Idea: {found_project.project_idea}")
    
    await engine.dispose()


async def update_project_example():
    """Update a project in DuckDB."""
    print("✏️ Updating project...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create project
        project = Project(name="Old Name", project_idea="Old idea", status="draft")
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        # Update project
        project.name = "New Name"
        project.status = "active"
        await session.commit()
        
        print(f"✅ Project updated: {project.name}, Status: {project.status}")
    
    await engine.dispose()


async def delete_project_example():
    """Delete a project from DuckDB."""
    print("🗑️ Deleting project...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create project
        project = Project(name="To Delete", project_idea="Will be deleted")
        session.add(project)
        await session.commit()
        project_id = project.id
        
        # Delete project
        await session.delete(project)
        await session.commit()
        
        # Verify deletion
        deleted_project = await session.get(Project, project_id)
        print(f"✅ Project deleted: {deleted_project is None}")
    
    await engine.dispose()


async def main():
    """Run all CRUD examples."""
    print("🚀 Simple Project CRUD Examples")
    print("=" * 40)
    
    await create_project_example()
    await read_project_example()
    await update_project_example() 
    await delete_project_example()
    
    print("\n✨ All CRUD examples completed!")


if __name__ == "__main__":
    uvloop.run(main())