"""
Document CRUD Example (client-only)

Rules:
- No engine/session setup here.
- No SQLAlchemy/columns/models defined here.
- Import the Document model from the library public API.
"""

import asyncio
from andamios_orm import Document  # library-provided model, not defined here

async def main():
    print("🚀 Document CRUD Operations")

    # CREATE
    doc = await Document.create(
        project_id=1,
        name="API Documentation",
        content="# API Specification\n\nThis document describes the REST API endpoints...",
        doc_type="api_spec",
        file_path="/docs/api-spec.md",
    )
    print("✅ created:", doc.id, doc.name)          # expected: id != None, "API Documentation"

    # READ
    found = await Document.read(doc.id)
    print("📖 read:", found.name)                   # expected: "API Documentation"
    print("   type:", found.doc_type)               # expected: "api_spec"
    print("   content length:", len(found.content)) # expected: > 0

    # UPDATE
    updated = await Document.update(
        doc.id,
        name="Complete API Documentation",
        doc_type="complete_api_spec",
        content="# Complete API Specification\n\nThis comprehensive document...",
    )
    print("✏️ updated:", updated.name, updated.doc_type)  # expected: "Complete API Documentation", "complete_api_spec"

    # DELETE
    await Document.delete(doc.id)
    gone = await Document.read(doc.id)
    print("🗑️ after delete:", gone)                 # expected: None

if __name__ == "__main__":
    asyncio.run(main())