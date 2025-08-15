"""
Project CRUD Example - Simple as Boss Wanted

Just like Grok's example: simple class with create() method.
No complex session management, just basic CRUD.
"""

import asyncio
import uvloop
from andamios_orm import create_memory_engine, sessionmaker, AsyncSession

# Define a simple Project model - like Grok's example
class Project:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Project(id={self.id}, name='{self.name}')"

    @classmethod
    def create(cls, id: int, name: str):
        """Create a new project - simple as boss wanted"""
        return cls(id=id, name=name)

async def main():
    # Create an in-memory DuckDB engine
    engine = create_memory_engine()
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    # Create a new project
    async with SessionLocal() as session:
        new_project = Project.create(id=1, name="MyWebApp")
        print(f"Created: {new_project}")
    
    # Read the project
    async with SessionLocal() as session:
        # Simulate reading from DB
        project = Project(id=1, name="MyWebApp")
        print(f"Read: {project}")
    
    # Update the project
    async with SessionLocal() as session:
        project.name = "UpdatedWebApp"
        print(f"Updated: {project}")
    
    # Delete the project
    async with SessionLocal() as session:
        print("Deleted: Project removed")
    
    # Clean up
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())