"""
DELETE Repository Example

Narrative: create object → read → delete → removed from DuckDB
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
            name="temp-repo",
            description="Temporary repository",
            repo_type="test"
        )
        session.add(repository)
        await session.commit()
        await session.refresh(repository)
        repository_id = repository.id
        
        # Read
        found_repository = await session.get(Repository, repository_id)
        
        # Delete → removed from DuckDB
        await session.delete(found_repository)
        await session.commit()
        
        # Verify deletion
        deleted_repository = await session.get(Repository, repository_id)
        
        print(f"✅ Repository deleted: {deleted_repository is None}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())