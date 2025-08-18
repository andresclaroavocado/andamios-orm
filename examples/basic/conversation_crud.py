"""
Conversation CRUD Example (client-only)

Rules:
- No engine/session setup here.
- No SQLAlchemy/columns/models defined here.
- Import the Conversation model from the library public API.
"""

import asyncio
from andamios_orm import Conversation  # library-provided model, not defined here

async def main():
    print("🚀 Conversation CRUD Operations")

    # CREATE
    convo = await Conversation.create(
        project_id=1,
        phase="requirements",
        messages=[
            {"role": "user", "content": "Let's start building"},
            {"role": "assistant", "content": "Great! What's your project idea?"},
        ],
    )
    print("✅ created:", convo.id, convo.phase)     # expected: id != None, "requirements"

    # READ
    found = await Conversation.read(convo.id)
    print("📖 read:", found.phase)                  # expected: "requirements"
    print("   messages:", len(found.messages))      # expected: 2

    # UPDATE
    updated = await Conversation.update(
        convo.id,
        phase="design",
        messages=found.messages + [{"role": "user", "content": "Design the architecture"}],
    )
    print("✏️ updated phase:", updated.phase)       # expected: "design"
    print("   messages:", len(updated.messages))    # expected: 3

    # DELETE
    await Conversation.delete(convo.id)
    gone = await Conversation.read(convo.id)
    print("🗑️ after delete:", gone)                 # expected: None

if __name__ == "__main__":
    asyncio.run(main())