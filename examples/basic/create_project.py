"""
CREATE Project Example

Narrative: instantiate Project ORM object → create → persisted in DuckDB
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
        # Instantiate ORM object
        project = Project(
            name="My Web App",
            project_idea="Build a task management system"
        )
        
        # Create → persisted in DuckDB
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        print(f"✅ Project created with ID: {project.id}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())