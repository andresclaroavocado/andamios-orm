"""
CREATE Conversation Example

Narrative: instantiate Conversation ORM object → create → persisted in DuckDB
"""

import asyncio
import uvloop
from andamios_orm import create_memory_engine, sessionmaker, AsyncSession

# Import existing models
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../legacy'))
from database.models import Base, Conversation

async def main():
    engine = create_memory_engine()
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Instantiate ORM object
        conversation = Conversation(
            project_id=1,
            phase="architecture",
            messages=[{"role": "user", "content": "Design the system"}]
        )
        
        # Create → persisted in DuckDB
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        
        print(f"✅ Conversation created with ID: {conversation.id}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())