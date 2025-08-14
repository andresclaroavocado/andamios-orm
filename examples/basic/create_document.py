"""
CREATE Document Example

Narrative: instantiate Document ORM object → create → persisted in DuckDB
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
        # Instantiate ORM object
        document = Document(
            project_id=1,
            name="API Specification",
            content="# API Docs\n\n## Endpoints",
            doc_type="api_spec"
        )
        
        # Create → persisted in DuckDB
        session.add(document)
        await session.commit()
        await session.refresh(document)
        
        print(f"✅ Document created with ID: {document.id}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())