"""
Repository CRUD Example (client-only)

Rules:
- No engine/session setup here.
- No SQLAlchemy/columns/models defined here.
- Import the Repository model from the library public API.
"""

import asyncio
from andamios_orm import Repository  # library-provided model, not defined here

async def main():
    print("🚀 Repository CRUD Operations")

    # CREATE
    repo = await Repository.create(
        project_id=1,
        name="backend-api",
        description="Main backend API service",
        repo_type="backend",
        github_url="https://github.com/user/backend-api",
    )
    print("✅ created:", repo.id, repo.name)        # expected: id != None, "backend-api"

    # READ
    found = await Repository.read(repo.id)
    print("📖 read:", found.name)                   # expected: "backend-api"
    print("   type:", found.repo_type)              # expected: "backend"

    # UPDATE
    updated = await Repository.update(
        repo.id,
        name="backend-api-v2",
        repo_type="microservice",
    )
    print("✏️ updated:", updated.name, updated.repo_type)  # expected: "backend-api-v2", "microservice"

    # DELETE
    await Repository.delete(repo.id)
    gone = await Repository.read(repo.id)
    print("🗑️ after delete:", gone)                 # expected: None

if __name__ == "__main__":
    asyncio.run(main())