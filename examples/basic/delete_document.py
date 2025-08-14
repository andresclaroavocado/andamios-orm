"""
DELETE Document Example

Narrative: create object → read → delete → removed from DuckDB
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
            name="Temporary Document",
            content="Will be deleted",
            doc_type="temp"
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)
        document_id = document.id
        
        # Read
        found_document = await session.get(Document, document_id)
        
        # Delete → removed from DuckDB
        await session.delete(found_document)
        await session.commit()
        
        # Verify deletion
        deleted_document = await session.get(Document, document_id)
        
        print(f"✅ Document deleted: {deleted_document is None}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())