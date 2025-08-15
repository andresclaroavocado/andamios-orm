"""
Document CRUD Example

Complete Create, Read, Update, Delete operations for Document model.
Narrative: instantiate ORM object → create → persisted in DuckDB → read/update/delete
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
        print("🚀 Document CRUD Operations")
        print("=" * 30)
        
        # CREATE
        print("\n📄 CREATE: Instantiate → create → persisted in DuckDB")
        document = Document(
            project_id=1,
            name="API Documentation",
            content="# API Documentation\n\n## Overview\nThis API provides...",
            doc_type="api_spec",
            file_path="/docs/api.md"
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)
        print(f"✅ Created document ID: {document.id}")
        print(f"   Name: {document.name}")
        print(f"   Type: {document.doc_type}")
        
        # READ
        print(f"\n📖 READ: Retrieve document from DuckDB")
        found_document = await session.get(Document, document.id)
        print(f"✅ Read document: {found_document.name}")
        print(f"   Project ID: {found_document.project_id}")
        print(f"   Type: {found_document.doc_type}")
        print(f"   Content preview: {found_document.content[:50]}...")
        
        # UPDATE
        print(f"\n✏️ UPDATE: Modify and persist changes")
        found_document.name = "Complete API Documentation"
        found_document.content += "\n\n## Authentication\nAPI uses JWT tokens..."
        found_document.doc_type = "complete_api_spec"
        found_document.file_path = "/docs/complete-api.md"
        await session.commit()
        print(f"✅ Updated document: {found_document.name}")
        print(f"   New type: {found_document.doc_type}")
        print(f"   New path: {found_document.file_path}")
        
        # DELETE
        print(f"\n🗑️ DELETE: Remove from DuckDB")
        document_id = found_document.id
        await session.delete(found_document)
        await session.commit()
        
        # Verify deletion
        deleted_document = await session.get(Document, document_id)
        print(f"✅ Document deleted: {deleted_document is None}")
        
        print("\n✨ All Document CRUD operations completed!")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())