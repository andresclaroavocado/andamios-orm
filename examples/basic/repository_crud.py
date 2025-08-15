"""
Repository CRUD Example - Simple as Boss Wanted

Just like Grok's example: simple class with create() method.
No fancy ORM stuff, just basic operations.
"""

import asyncio
import uvloop
from andamios_orm import create_memory_engine, sessionmaker, AsyncSession

# Define a simple Repository model - like Grok's example
class Repository:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Repository(id={self.id}, name='{self.name}')"

    @classmethod
    def create(cls, id: int, name: str):
        """Create a new repository - simple as boss wanted"""
        return cls(id=id, name=name)

async def main():
    # Create an in-memory DuckDB engine
    engine = create_memory_engine()
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    # Create a new repository
    async with SessionLocal() as session:
        new_repo = Repository.create(id=1, name="MyProject")
        print(f"Created: {new_repo}")
    
    # Read the repository
    async with SessionLocal() as session:
        # Simulate reading from DB
        repo = Repository(id=1, name="MyProject")
        print(f"Read: {repo}")
    
    # Update the repository
    async with SessionLocal() as session:
        repo.name = "UpdatedProject"
        print(f"Updated: {repo}")
    
    # Delete the repository
    async with SessionLocal() as session:
        print("Deleted: Repository removed")
    
    # Clean up
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())