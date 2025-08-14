"""
Simple CRUD Examples - Repository Model

Basic Create, Read, Update, Delete operations using the Repository model.
Each example shows how an ORM object created in memory gets saved to DuckDB.
"""

import asyncio
import uvloop
from andamios_orm import create_engine, sessionmaker, AsyncSession
from database.models import Base, Repository


async def create_repository_example():
    """Create a new repository in DuckDB."""
    print("📦 Creating a new repository...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create repository object in memory
        repository = Repository(
            project_id=1,
            name="my-backend-api",
            description="Main backend API for the project",
            repo_type="backend",
            github_url="https://github.com/user/my-backend-api"
        )
        
        # Save to DuckDB
        session.add(repository)
        await session.commit()
        await session.refresh(repository)
        
        print(f"✅ Repository created with ID: {repository.id}")
        print(f"📦 Name: {repository.name}")
        print(f"🔧 Type: {repository.repo_type}")
    
    await engine.dispose()


async def read_repository_example():
    """Read a repository from DuckDB."""
    print("📖 Reading repository...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create repository
        repository = Repository(
            project_id=1,
            name="frontend-app",
            description="React frontend application",
            repo_type="frontend"
        )
        session.add(repository)
        await session.commit()
        await session.refresh(repository)
        
        # Read repository back
        found_repository = await session.get(Repository, repository.id)
        print(f"📦 Found repository: {found_repository.name}")
        print(f"🔧 Type: {found_repository.repo_type}")
        print(f"📝 Description: {found_repository.description}")
    
    await engine.dispose()


async def update_repository_example():
    """Update a repository in DuckDB."""
    print("✏️ Updating repository...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create repository
        repository = Repository(
            project_id=1,
            name="old-repo-name",
            description="Old description",
            repo_type="backend"
        )
        session.add(repository)
        await session.commit()
        await session.refresh(repository)
        
        # Update repository
        repository.name = "new-repo-name"
        repository.description = "Updated description with more details"
        repository.github_url = "https://github.com/user/new-repo-name"
        await session.commit()
        
        print(f"✅ Repository updated: {repository.name}")
        print(f"📝 Description: {repository.description}")
        print(f"🔗 GitHub URL: {repository.github_url}")
    
    await engine.dispose()


async def delete_repository_example():
    """Delete a repository from DuckDB."""
    print("🗑️ Deleting repository...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create repository
        repository = Repository(
            project_id=1,
            name="temp-repo",
            description="Temporary repository to delete",
            repo_type="test"
        )
        session.add(repository)
        await session.commit()
        repository_id = repository.id
        
        # Delete repository
        await session.delete(repository)
        await session.commit()
        
        # Verify deletion
        deleted_repository = await session.get(Repository, repository_id)
        print(f"✅ Repository deleted: {deleted_repository is None}")
    
    await engine.dispose()


async def main():
    """Run all CRUD examples."""
    print("🚀 Simple Repository CRUD Examples")
    print("=" * 40)
    
    await create_repository_example()
    await read_repository_example()
    await update_repository_example()
    await delete_repository_example()
    
    print("\n✨ All CRUD examples completed!")


if __name__ == "__main__":
    uvloop.run(main())