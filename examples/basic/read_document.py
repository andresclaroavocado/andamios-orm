"""
READ Document Example

Narrative: create object → read from DuckDB
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
        # First create a document to read
        document = Document(
            project_id=1,
            name="Architecture Doc",
            content="System design...",
            doc_type="architecture"
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)
        document_id = document.id
        
        # Read from DuckDB
        found_document = await session.get(Document, document_id)
        
        print(f"✅ Read document: {found_document.name}")
        print(f"   ID: {found_document.id}")
        print(f"   Type: {found_document.doc_type}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())