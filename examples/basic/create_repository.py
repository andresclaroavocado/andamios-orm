"""
CREATE Repository Example

Narrative: instantiate Repository ORM object → create → persisted in DuckDB
"""

import asyncio
import uvloop
from andamios_orm import create_memory_engine, sessionmaker, AsyncSession

# Import existing models
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../legacy'))
from database.models import Base, Repository

async def main():
    engine = create_memory_engine()
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Instantiate ORM object
        repository = Repository(
            project_id=1,
            name="backend-api",
            description="Main API backend",
            repo_type="backend"
        )
        
        # Create → persisted in DuckDB
        session.add(repository)
        await session.commit()
        await session.refresh(repository)
        
        print(f"✅ Repository created with ID: {repository.id}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())