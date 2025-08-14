"""
READ Repository Example

Narrative: create object → read from DuckDB
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
        # First create a repository to read
        repository = Repository(
            project_id=1,
            name="frontend-app",
            description="React frontend",
            repo_type="frontend"
        )
        session.add(repository)
        await session.commit()
        await session.refresh(repository)
        repository_id = repository.id
        
        # Read from DuckDB
        found_repository = await session.get(Repository, repository_id)
        
        print(f"✅ Read repository: {found_repository.name}")
        print(f"   ID: {found_repository.id}")
        print(f"   Type: {found_repository.repo_type}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())