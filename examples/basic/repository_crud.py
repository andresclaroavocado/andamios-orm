"""
Repository CRUD Example

Complete Create, Read, Update, Delete operations for Repository model.
Narrative: instantiate ORM object → create → persisted in DuckDB → read/update/delete
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
        print("🚀 Repository CRUD Operations")
        print("=" * 32)
        
        # CREATE
        print("\n🏗️ CREATE: Instantiate → create → persisted in DuckDB")
        repository = Repository(
            project_id=1,
            name="backend-api",
            description="Main backend API service",
            repo_type="backend",
            github_url="https://github.com/user/backend-api"
        )
        session.add(repository)
        await session.commit()
        await session.refresh(repository)
        print(f"✅ Created repository ID: {repository.id}")
        print(f"   Name: {repository.name}")
        print(f"   Type: {repository.repo_type}")
        
        # READ
        print(f"\n📖 READ: Retrieve repository from DuckDB")
        found_repository = await session.get(Repository, repository.id)
        print(f"✅ Read repository: {found_repository.name}")
        print(f"   Project ID: {found_repository.project_id}")
        print(f"   Description: {found_repository.description}")
        print(f"   GitHub URL: {found_repository.github_url}")
        
        # UPDATE
        print(f"\n✏️ UPDATE: Modify and persist changes")
        found_repository.name = "advanced-backend-api"
        found_repository.description = "Advanced microservices backend API"
        found_repository.repo_type = "microservice"
        found_repository.github_url = "https://github.com/user/advanced-backend-api"
        await session.commit()
        print(f"✅ Updated repository: {found_repository.name}")
        print(f"   New type: {found_repository.repo_type}")
        print(f"   New URL: {found_repository.github_url}")
        
        # DELETE
        print(f"\n🗑️ DELETE: Remove from DuckDB")
        repository_id = found_repository.id
        await session.delete(found_repository)
        await session.commit()
        
        # Verify deletion
        deleted_repository = await session.get(Repository, repository_id)
        print(f"✅ Repository deleted: {deleted_repository is None}")
        
        print("\n✨ All Repository CRUD operations completed!")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())