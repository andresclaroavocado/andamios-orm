"""
Conversation CRUD Example

Complete Create, Read, Update, Delete operations for Conversation model.
Narrative: instantiate ORM object → create → persisted in DuckDB → read/update/delete
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
        print("🚀 Conversation CRUD Operations")
        print("=" * 35)
        
        # CREATE
        print("\n💬 CREATE: Instantiate → create → persisted in DuckDB")
        conversation = Conversation(
            project_id=1,
            phase="architecture",
            messages=[
                {"role": "user", "content": "Let's design the system"},
                {"role": "assistant", "content": "Great! Let's start with the architecture"}
            ]
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        print(f"✅ Created conversation ID: {conversation.id}")
        print(f"   Phase: {conversation.phase}")
        print(f"   Messages: {len(conversation.messages)}")
        
        # READ
        print(f"\n📖 READ: Retrieve conversation from DuckDB")
        found_conversation = await session.get(Conversation, conversation.id)
        print(f"✅ Read conversation: {found_conversation.id}")
        print(f"   Project ID: {found_conversation.project_id}")
        print(f"   Phase: {found_conversation.phase}")
        print(f"   First message: {found_conversation.messages[0]['content']}")
        
        # UPDATE
        print(f"\n✏️ UPDATE: Modify and persist changes")
        found_conversation.phase = "implementation"
        found_conversation.messages.append({
            "role": "user", 
            "content": "Now let's implement the features"
        })
        await session.commit()
        print(f"✅ Updated conversation phase: {found_conversation.phase}")
        print(f"   Total messages: {len(found_conversation.messages)}")
        
        # DELETE
        print(f"\n🗑️ DELETE: Remove from DuckDB")
        conversation_id = found_conversation.id
        await session.delete(found_conversation)
        await session.commit()
        
        # Verify deletion
        deleted_conversation = await session.get(Conversation, conversation_id)
        print(f"✅ Conversation deleted: {deleted_conversation is None}")
        
        print("\n✨ All Conversation CRUD operations completed!")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())