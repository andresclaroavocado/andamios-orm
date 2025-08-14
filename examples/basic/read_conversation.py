"""
READ Conversation Example

Narrative: create object → read from DuckDB
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
        # First create a conversation to read
        conversation = Conversation(
            project_id=1, 
            phase="design",
            messages=[{"role": "user", "content": "Hello"}]
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        conversation_id = conversation.id
        
        # Read from DuckDB
        found_conversation = await session.get(Conversation, conversation_id)
        
        print(f"✅ Read conversation: {found_conversation.id}")
        print(f"   Phase: {found_conversation.phase}")
        print(f"   Messages: {len(found_conversation.messages)}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())