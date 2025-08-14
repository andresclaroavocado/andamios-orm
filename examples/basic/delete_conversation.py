"""
DELETE Conversation Example

Narrative: create object → read → delete → removed from DuckDB
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
            phase="to_delete",
            messages=[{"role": "user", "content": "Delete me"}]
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        conversation_id = conversation.id
        
        # Read
        found_conversation = await session.get(Conversation, conversation_id)
        
        # Delete → removed from DuckDB
        await session.delete(found_conversation)
        await session.commit()
        
        # Verify deletion
        deleted_conversation = await session.get(Conversation, conversation_id)
        
        print(f"✅ Conversation deleted: {deleted_conversation is None}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())