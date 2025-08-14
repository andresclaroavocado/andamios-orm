"""
Simple CRUD Examples - Document Model

Basic Create, Read, Update, Delete operations using the Document model.
Each example shows how an ORM object created in memory gets saved to DuckDB.
"""

import asyncio
import uvloop
from andamios_orm import create_engine, sessionmaker, AsyncSession
from database.models import Base, Document


async def create_document_example():
    """Create a new document in DuckDB."""
    print("📄 Creating a new document...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create document object in memory
        document = Document(
            project_id=1,
            name="API Documentation",
            content="# API Documentation\n\nThis is the API spec...",
            doc_type="api_spec",
            file_path="/docs/api.md"
        )
        
        # Save to DuckDB
        session.add(document)
        await session.commit()
        await session.refresh(document)
        
        print(f"✅ Document created with ID: {document.id}")
        print(f"📝 Name: {document.name}")
        print(f"📁 Type: {document.doc_type}")
    
    await engine.dispose()


async def read_document_example():
    """Read a document from DuckDB."""
    print("📖 Reading document...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create document
        document = Document(
            project_id=1,
            name="Architecture Doc",
            content="System architecture details...",
            doc_type="architecture"
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)
        
        # Read document back
        found_document = await session.get(Document, document.id)
        print(f"📄 Found document: {found_document.name}")
        print(f"🏗️ Type: {found_document.doc_type}")
        print(f"📁 Project ID: {found_document.project_id}")
    
    await engine.dispose()


async def update_document_example():
    """Update a document in DuckDB."""
    print("✏️ Updating document...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create document
        document = Document(
            project_id=1,
            name="Draft Doc",
            content="Initial content",
            doc_type="draft"
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)
        
        # Update document
        document.name = "Final Documentation"
        document.content = "Updated content with more details"
        document.doc_type = "documentation"
        await session.commit()
        
        print(f"✅ Document updated: {document.name}")
        print(f"📝 Type: {document.doc_type}")
    
    await engine.dispose()


async def delete_document_example():
    """Delete a document from DuckDB."""
    print("🗑️ Deleting document...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create document
        document = Document(
            project_id=1,
            name="Temporary Doc",
            content="This will be deleted",
            doc_type="temp"
        )
        session.add(document)
        await session.commit()
        document_id = document.id
        
        # Delete document
        await session.delete(document)
        await session.commit()
        
        # Verify deletion
        deleted_document = await session.get(Document, document_id)
        print(f"✅ Document deleted: {deleted_document is None}")
    
    await engine.dispose()


async def main():
    """Run all CRUD examples."""
    print("🚀 Simple Document CRUD Examples")
    print("=" * 40)
    
    await create_document_example()
    await read_document_example()
    await update_document_example()
    await delete_document_example()
    
    print("\n✨ All CRUD examples completed!")


if __name__ == "__main__":
    uvloop.run(main())