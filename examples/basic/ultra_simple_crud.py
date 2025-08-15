"""
Ultra Simple CRUD Example

The simplest possible ORM usage - no sessions, no engines, no setup!
Just import, define model, and use. Library handles everything internally.
"""

import asyncio
import uvloop
from simple_models import Project


async def main():
    print("🚀 Ultra Simple ORM Usage")
    print("=" * 30)
    
    # CREATE - Just create and save
    print("\n📝 CREATE: Super simple!")
    project = Project(
        name="My Simple App", 
        description="A productivity tool",
        project_idea="Build something awesome"
    )
    await project.save()
    print(f"✅ Created project ID: {project.id}")
    
    # READ - Get by ID
    print(f"\n📖 READ: Get by ID")
    found = await Project.get(project.id)
    print(f"✅ Found: {found.name}")
    
    # UPDATE - Modify and save
    print(f"\n✏️ UPDATE: Modify and save")
    found.name = "Updated App"
    found.status = "active"
    await found.save()
    print(f"✅ Updated: {found.name}")
    
    # CREATE with class method
    print(f"\n📝 CREATE with class method")
    repo = await Project.create(
        name="Another Project",
        project_idea="Build another thing"
    )
    print(f"✅ Created via class method: {repo.id}")
    
    # GET ALL
    print(f"\n📋 GET ALL projects")
    all_projects = await Project.get_all()
    print(f"✅ Found {len(all_projects)} projects:")
    for p in all_projects:
        print(f"   - {p.name} (ID: {p.id})")
    
    # DELETE
    print(f"\n🗑️ DELETE")
    await found.delete()
    await repo.delete()
    print("✅ Projects deleted")
    
    print("\n✨ All operations completed - Zero configuration needed!")


if __name__ == "__main__":
    uvloop.run(main())