"""
UPDATE Repository Example

Narrative: create object → read → update → persisted in DuckDB
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
        # Create object
        repository = Repository(
            project_id=1,
            name="old-service",
            description="Legacy service",
            repo_type="backend"
        )
        session.add(repository)
        await session.commit()
        await session.refresh(repository)
        
        # Read
        found_repository = await session.get(Repository, repository.id)
        
        # Update → persisted in DuckDB
        found_repository.name = "new-microservice"
        found_repository.description = "Modern microservice"
        found_repository.repo_type = "microservice"
        await session.commit()
        
        print(f"✅ Updated repository: {found_repository.name}")
        print(f"   Type: {found_repository.repo_type}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())