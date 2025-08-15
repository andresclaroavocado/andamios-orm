"""
Repository Simple Example

Shows the boss's ideal: super easy to use, zero configuration.
"""

import asyncio
import uvloop
from simple_models import Repository


async def main():
    print("🚀 Repository - Ultra Simple Usage")
    print("=" * 35)
    
    # CREATE - Just instantiate and save
    print("\n📝 CREATE: Repository")
    repo = Repository(
        name="My Awesome Repo",
        description="A simple example repository",
        repo_type="backend",
        github_url="https://github.com/user/repo"
    )
    await repo.save()
    print(f"✅ Created repo ID: {repo.id}")
    print(f"   Name: {repo.name}")
    print(f"   Type: {repo.repo_type}")
    
    # READ - Get by ID
    print(f"\n📖 READ: Get repository")
    found = await Repository.get(repo.id)
    print(f"✅ Found: {found.name}")
    print(f"   GitHub: {found.github_url}")
    
    # UPDATE - Change and save
    print(f"\n✏️ UPDATE: Change repo details")
    found.name = "Updated Awesome Repo"
    found.repo_type = "frontend"
    found.description = "Now it's a frontend repo"
    await found.save()
    print(f"✅ Updated: {found.name}")
    print(f"   New type: {found.repo_type}")
    
    # CREATE with class method
    print(f"\n📝 CREATE: Using class method")
    repo2 = await Repository.create(
        name="Another Repo",
        description="Created with class method",
        repo_type="docs"
    )
    print(f"✅ Created via create(): {repo2.name}")
    
    # GET ALL
    print(f"\n📋 LIST: All repositories")
    all_repos = await Repository.get_all()
    print(f"✅ Found {len(all_repos)} repositories:")
    for r in all_repos:
        print(f"   - {r.name} ({r.repo_type})")
    
    # DELETE
    print(f"\n🗑️ DELETE: Clean up")
    await found.delete()
    await repo2.delete()
    print("✅ Repositories deleted")
    
    print("\n✨ Super easy! No sessions, no engines, no setup!")


if __name__ == "__main__":
    uvloop.run(main())