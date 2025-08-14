"""
UPDATE Document Example

Narrative: create object → read → update → persisted in DuckDB
"""

import asyncio
import uvloop
from andamios_orm import create_memory_engine, sessionmaker, AsyncSession

# Import existing models
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../legacy'))
from database.models import Base, Document

async def main():
    engine = create_memory_engine()
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create object
        document = Document(
            project_id=1,
            name="Draft Document",
            content="Initial content",
            doc_type="draft"
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)
        
        # Read
        found_document = await session.get(Document, document.id)
        
        # Update → persisted in DuckDB
        found_document.name = "Final Document"
        found_document.content = "Updated final content"
        found_document.doc_type = "final"
        await session.commit()
        
        print(f"✅ Updated document: {found_document.name}")
        print(f"   Type: {found_document.doc_type}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())