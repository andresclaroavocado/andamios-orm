"""
UPDATE Project Example

Narrative: create object → read → update → persisted in DuckDB
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
        # Create object
        project = Project(name="Old Name", project_idea="Original idea", status="draft")
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        # Read
        found_project = await session.get(Project, project.id)
        
        # Update → persisted in DuckDB
        found_project.name = "Updated Name"
        found_project.status = "active"
        await session.commit()
        
        print(f"✅ Updated project: {found_project.name}")
        print(f"   Status: {found_project.status}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())