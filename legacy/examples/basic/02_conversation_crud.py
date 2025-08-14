"""
Simple CRUD Examples - Conversation Model

Basic Create, Read, Update, Delete operations using the Conversation model.
Each example shows how an ORM object created in memory gets saved to DuckDB.
"""

import asyncio
import uvloop
from andamios_orm import create_engine, sessionmaker, AsyncSession
from database.models import Base, Conversation


async def create_conversation_example():
    """Create a new conversation in DuckDB."""
    print("💬 Creating a new conversation...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create conversation object in memory
        conversation = Conversation(
            project_id=1,
            phase="planning",
            messages=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! How can I help?"}
            ]
        )
        
        # Save to DuckDB
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        
        print(f"✅ Conversation created with ID: {conversation.id}")
        print(f"📝 Phase: {conversation.phase}")
    
    await engine.dispose()


async def read_conversation_example():
    """Read a conversation from DuckDB."""
    print("📖 Reading conversation...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create conversation
        conversation = Conversation(
            project_id=1,
            phase="development",
            messages=[{"role": "user", "content": "Test message"}]
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        
        # Read conversation back
        found_conversation = await session.get(Conversation, conversation.id)
        print(f"💬 Found conversation for project: {found_conversation.project_id}")
        print(f"📋 Phase: {found_conversation.phase}")
        print(f"📩 Messages count: {len(found_conversation.messages)}")
    
    await engine.dispose()


async def update_conversation_example():
    """Update a conversation in DuckDB."""
    print("✏️ Updating conversation...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create conversation
        conversation = Conversation(
            project_id=1,
            phase="initial",
            messages=[{"role": "user", "content": "Start"}]
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        
        # Update conversation
        conversation.phase = "completed"
        conversation.messages.append({"role": "assistant", "content": "Done!"})
        await session.commit()
        
        print(f"✅ Conversation updated - Phase: {conversation.phase}")
        print(f"📩 Messages count: {len(conversation.messages)}")
    
    await engine.dispose()


async def delete_conversation_example():
    """Delete a conversation from DuckDB."""
    print("🗑️ Deleting conversation...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create conversation
        conversation = Conversation(
            project_id=1,
            phase="to_delete",
            messages=[{"role": "user", "content": "Delete me"}]
        )
        session.add(conversation)
        await session.commit()
        conversation_id = conversation.id
        
        # Delete conversation
        await session.delete(conversation)
        await session.commit()
        
        # Verify deletion
        deleted_conversation = await session.get(Conversation, conversation_id)
        print(f"✅ Conversation deleted: {deleted_conversation is None}")
    
    await engine.dispose()


async def main():
    """Run all CRUD examples."""
    print("🚀 Simple Conversation CRUD Examples")
    print("=" * 40)
    
    await create_conversation_example()
    await read_conversation_example()
    await update_conversation_example()
    await delete_conversation_example()
    
    print("\n✨ All CRUD examples completed!")


if __name__ == "__main__":
    uvloop.run(main())