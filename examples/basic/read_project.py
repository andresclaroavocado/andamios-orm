"""
READ Project Example

Narrative: create object → read from DuckDB
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
        # First create a project to read
        project = Project(name="Test Project", project_idea="Read example")
        session.add(project)
        await session.commit()
        await session.refresh(project)
        project_id = project.id
        
        # Read from DuckDB
        found_project = await session.get(Project, project_id)
        
        print(f"✅ Read project: {found_project.name}")
        print(f"   ID: {found_project.id}")
        print(f"   Idea: {found_project.project_idea}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())