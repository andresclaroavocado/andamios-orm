"""
Project CRUD Example (client-only)

Rules:
- No engine/session setup here.
- No SQLAlchemy/columns/models defined here.
- Import the Project model from the library public API.
"""

import asyncio
from andamios_orm import Project  # library-provided model, not defined here

async def main():
    print("🚀 Project CRUD Operations")

    # CREATE
    project = await Project.create(
        name="My Web App",
        description="A task management system",
        project_idea="Build a productivity tool",
        status="draft",
    )
    print("✅ created:", project.id, project.name)  # expected: id != None, "My Web App"

    # READ
    found = await Project.read(project.id)
    print("📖 read:", found.name)                   # expected: "My Web App"
    print("   status:", found.status)               # expected: "draft"

    # UPDATE
    updated = await Project.update(
        project.id,
        name="Updated Web App",
        status="active",
    )
    print("✏️ updated:", updated.name, updated.status)  # expected: "Updated Web App", "active"

    # DELETE
    await Project.delete(project.id)
    gone = await Project.read(project.id)
    print("🗑️ after delete:", gone)                 # expected: None

if __name__ == "__main__":
    asyncio.run(main())