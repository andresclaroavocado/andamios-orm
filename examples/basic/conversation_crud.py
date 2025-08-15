"""
Conversation CRUD Example

Simple Conversation class with create/read/update/delete operations.
Uses async/await but keeps it simple.
"""

import asyncio
import uvloop
from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from andamios_orm.models.base import Model, Base

# Initialize database
async def init_db():
    from andamios_orm.core import create_memory_engine
    from andamios_orm.core.session import init_db as init_core_db
    
    engine = create_memory_engine()
    init_core_db(engine)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Define Conversation model exactly like legacy database
class Conversation(Model):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    phase = Column(String(100), default="project_idea")
    messages = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"Conversation(id={self.id}, phase='{self.phase}')"

# Example usage
async def main():
    await init_db()
    
    print("🚀 Conversation CRUD Operations")
    print("=" * 35)

    # CREATE
    print("\n💬 CREATE: Instantiate → create → persisted")
    conversation = await Conversation.create(
        project_id=1,
        phase="requirements",
        messages=[
            {"role": "user", "content": "Let's start building"},
            {"role": "assistant", "content": "Great! What's your project idea?"}
        ]
    )
    print(f"✅ Created conversation ID: {conversation.id}")
    print(f"   Phase: {conversation.phase}")
    print(f"   Messages: {len(conversation.messages)} messages")

    # READ
    print("\n📖 READ: Retrieve conversation")
    found_conversation = await Conversation.read(conversation.id)
    print(f"✅ Read conversation: {found_conversation.phase}")
    print(f"   Project ID: {found_conversation.project_id}")
    print(f"   Messages: {found_conversation.messages}")

    # UPDATE
    print("\n✏️ UPDATE: Modify conversation")
    updated_conversation = await Conversation.update(
        conversation.id,
        phase="design",
        messages=[
            {"role": "user", "content": "Let's start building"},
            {"role": "assistant", "content": "Great! What's your project idea?"},
            {"role": "user", "content": "Now let's design the architecture"}
        ]
    )
    print(f"✅ Updated conversation: {updated_conversation.phase}")
    print(f"   New messages count: {len(updated_conversation.messages)}")

    # DELETE
    print("\n🗑️ DELETE: Remove conversation")
    deleted = await Conversation.delete(conversation.id)
    print(f"✅ Conversation deleted: {deleted}")

    print("\n✨ All Conversation CRUD operations completed!")

if __name__ == "__main__":
    uvloop.run(main())