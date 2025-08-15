"""
Project CRUD Example

Following Grok's simple pattern but with real ORM functionality.
Simple Project class with create() method that actually works with DuckDB.
"""

import asyncio
import uvloop
from sqlalchemy import Column, Integer, String, Text
from andamios_orm import create_memory_engine, sessionmaker, AsyncSession

# Import the base for SQLAlchemy models
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../legacy'))
from database.database import Base

# Define Project model - like Grok's pattern but with real SQLAlchemy
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

    def __repr__(self):
        return f"Project(id={self.id}, name='{self.name}')"

    @classmethod
    def create(cls, id: int, name: str):
        """Create a new project - simple factory method like Grok's example"""
        return cls(id=id, name=name)

async def main():
    # Create an in-memory DuckDB engine
    engine = create_memory_engine()
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # CREATE - Create a new project
    async with SessionLocal() as session:
        new_project = Project.create(id=1, name="MyWebApp")
        session.add(new_project)
        await session.commit()
        await session.refresh(new_project)
        print(f"Created: {new_project}")
    
    # READ - Read the project
    async with SessionLocal() as session:
        result = await session.execute("SELECT id, name FROM projects WHERE id = 1")
        project_data = result.fetchone()
        if project_data:
            print(f"Read: Project(id={project_data[0]}, name='{project_data[1]}')")
    
    # UPDATE - Update the project
    async with SessionLocal() as session:
        await session.execute("UPDATE projects SET name = 'UpdatedWebApp' WHERE id = 1")
        await session.commit()
        updated = await session.execute("SELECT name FROM projects WHERE id = 1")
        updated_name = updated.fetchone()[0]
        print(f"Updated: Project(name='{updated_name}')")
    
    # DELETE - Delete the project
    async with SessionLocal() as session:
        await session.execute("DELETE FROM projects WHERE id = 1")
        await session.commit()
        check = await session.execute("SELECT COUNT(*) FROM projects WHERE id = 1")
        count = check.fetchone()[0]
        print(f"Deleted: {'Yes' if count == 0 else 'No'}")
    
    # Clean up
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())