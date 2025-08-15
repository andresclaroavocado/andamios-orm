"""
Repository CRUD Example

Simple Repository class with create/read/update/delete operations.
Uses async/await but keeps it simple.
"""

import asyncio
import uvloop
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from andamios_orm.models.base import Model, Base
from andamios_orm.core import get_session

# Initialize database
async def init_db():
    from andamios_orm.core import create_memory_engine
    from andamios_orm.core.session import init_db as init_core_db
    
    engine = create_memory_engine()
    init_core_db(engine)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Define Repository model exactly like legacy database
class Repository(Model):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    repo_type = Column(String(100))  # backend, frontend, docs, infrastructure
    github_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"Repository(id={self.id}, name='{self.name}')"

# Example usage
async def main():
    await init_db()
    
    print("🚀 Repository CRUD Operations")
    print("=" * 32)

    # CREATE
    print("\n🏗️ CREATE: Instantiate → create → persisted")
    repo = await Repository.create(
        project_id=1,
        name="backend-api",
        description="Main backend API service",
        repo_type="backend",
        github_url="https://github.com/user/backend-api"
    )
    print(f"✅ Created repository ID: {repo.id}")
    print(f"   Name: {repo.name}")
    print(f"   Type: {repo.repo_type}")

    # READ
    print("\n📖 READ: Retrieve repository")
    found_repo = await Repository.read(repo.id)
    print(f"✅ Read repository: {found_repo.name}")
    print(f"   Description: {found_repo.description}")
    print(f"   GitHub URL: {found_repo.github_url}")

    # UPDATE
    print("\n✏️ UPDATE: Modify repository")
    updated_repo = await Repository.update(
        repo.id, 
        name="advanced-backend-api",
        description="Advanced microservices backend API",
        repo_type="microservice"
    )
    print(f"✅ Updated repository: {updated_repo.name}")
    print(f"   New type: {updated_repo.repo_type}")

    # DELETE
    print("\n🗑️ DELETE: Remove repository")
    deleted = await Repository.delete(repo.id)
    print(f"✅ Repository deleted: {deleted}")

    print("\n✨ All Repository CRUD operations completed!")

if __name__ == "__main__":
    uvloop.run(main())