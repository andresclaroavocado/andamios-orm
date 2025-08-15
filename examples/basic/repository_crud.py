"""
Repository CRUD Example

Follows a clean factory pattern with real ORM functionality.
Simple Repository class with create() method that actually works with DuckDB.
"""

import asyncio
import uvloop
from sqlalchemy import Column, Integer, String, Text
from andamios_orm import create_memory_engine, sessionmaker, AsyncSession

# Import the base for SQLAlchemy models
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../legacy'))
from database.database import Base

# Define Repository model with clean factory pattern using SQLAlchemy
class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

    def __repr__(self):
        return f"Repository(id={self.id}, name='{self.name}')"

    @classmethod
    def create(cls, id: int, name: str):
        """Create a new repository - simple factory method"""
        return cls(id=id, name=name)

async def main():
    # Create an in-memory DuckDB engine
    engine = create_memory_engine()
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # CREATE - Create a new repository
    async with SessionLocal() as session:
        new_repo = Repository.create(id=1, name="MyProject")
        session.add(new_repo)
        await session.commit()
        await session.refresh(new_repo)
        print(f"Created: {new_repo}")
    
    # READ - Read the repository
    async with SessionLocal() as session:
        result = await session.execute("SELECT id, name FROM repositories WHERE id = 1")
        repo_data = result.fetchone()
        if repo_data:
            print(f"Read: Repository(id={repo_data[0]}, name='{repo_data[1]}')")
    
    # UPDATE - Update the repository
    async with SessionLocal() as session:
        await session.execute("UPDATE repositories SET name = 'UpdatedProject' WHERE id = 1")
        await session.commit()
        updated = await session.execute("SELECT name FROM repositories WHERE id = 1")
        updated_name = updated.fetchone()[0]
        print(f"Updated: Repository(name='{updated_name}')")
    
    # DELETE - Delete the repository
    async with SessionLocal() as session:
        await session.execute("DELETE FROM repositories WHERE id = 1")
        await session.commit()
        check = await session.execute("SELECT COUNT(*) FROM repositories WHERE id = 1")
        count = check.fetchone()[0]
        print(f"Deleted: {'Yes' if count == 0 else 'No'}")
    
    # Clean up
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())