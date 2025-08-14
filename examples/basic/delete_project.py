"""
DELETE Project Example

Narrative: create object → read → delete → removed from DuckDB
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
        project = Project(name="To Delete", project_idea="Will be deleted")
        session.add(project)
        await session.commit()
        await session.refresh(project)
        project_id = project.id
        
        # Read
        found_project = await session.get(Project, project_id)
        
        # Delete → removed from DuckDB
        await session.delete(found_project)
        await session.commit()
        
        # Verify deletion
        deleted_project = await session.get(Project, project_id)
        
        print(f"✅ Project deleted: {deleted_project is None}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())