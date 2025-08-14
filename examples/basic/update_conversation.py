"""
UPDATE Conversation Example

Narrative: create object → read → update → persisted in DuckDB
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
        # Create object
        conversation = Conversation(
            project_id=1,
            phase="initial",
            messages=[{"role": "user", "content": "Start"}]
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        
        # Read
        found_conversation = await session.get(Conversation, conversation.id)
        
        # Update → persisted in DuckDB
        found_conversation.phase = "architecture"
        found_conversation.messages.append({"role": "assistant", "content": "Let's design"})
        await session.commit()
        
        print(f"✅ Updated conversation phase: {found_conversation.phase}")
        print(f"   Messages: {len(found_conversation.messages)}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())