"""
Document CRUD Example

Simple Document class with create/read/update/delete operations.
Uses async/await but keeps it simple.
"""

import asyncio
import uvloop
from sqlalchemy import Column, Integer, String, Text, DateTime
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

# Define Document model exactly like legacy database
class Document(Model):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    name = Column(String(255), nullable=False)
    content = Column(Text)
    doc_type = Column(String(100))  # architecture, api_spec, deployment, etc.
    file_path = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"Document(id={self.id}, name='{self.name}')"

# Example usage
async def main():
    await init_db()
    
    print("🚀 Document CRUD Operations")
    print("=" * 30)

    # CREATE
    print("\n📄 CREATE: Instantiate → create → persisted")
    document = await Document.create(
        project_id=1,
        name="API Documentation",
        content="# API Specification\n\nThis document describes the REST API endpoints...",
        doc_type="api_spec",
        file_path="/docs/api-spec.md"
    )
    print(f"✅ Created document ID: {document.id}")
    print(f"   Name: {document.name}")
    print(f"   Type: {document.doc_type}")

    # READ
    print("\n📖 READ: Retrieve document")
    found_document = await Document.read(document.id)
    print(f"✅ Read document: {found_document.name}")
    print(f"   Project ID: {found_document.project_id}")
    print(f"   Content length: {len(found_document.content) if found_document.content else 0} chars")
    print(f"   File path: {found_document.file_path}")

    # UPDATE
    print("\n✏️ UPDATE: Modify document")
    updated_document = await Document.update(
        document.id,
        name="Complete API Documentation",
        content="# Complete API Specification\n\nThis comprehensive document...",
        doc_type="complete_api_spec"
    )
    print(f"✅ Updated document: {updated_document.name}")
    print(f"   New type: {updated_document.doc_type}")

    # DELETE
    print("\n🗑️ DELETE: Remove document")
    deleted = await Document.delete(document.id)
    print(f"✅ Document deleted: {deleted}")

    print("\n✨ All Document CRUD operations completed!")

if __name__ == "__main__":
    uvloop.run(main())