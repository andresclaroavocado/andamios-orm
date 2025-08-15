"""
Project CRUD Example - BEFORE (Complex)

This shows the OLD complex way vs the NEW simple way.
Compare this with ultra_simple_crud.py to see the difference!
"""

import asyncio
import uvloop
from andamios_orm import create_memory_engine, sessionmaker, AsyncSession

# Import existing models
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../legacy'))
from database.models import Base, Project

async def main():
    print("🔧 OLD COMPLEX WAY (what we want to avoid)")
    print("=" * 50)
    print("❌ Too much setup - client manages everything!")
    
    # Complex setup that client shouldn't need to do
    engine = create_memory_engine()
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        print("\n📝 CREATE: Complex session management")
        project = Project(
            name="My Web App",
            description="A task management system",
            project_idea="Build a productivity tool",
            status="draft"
        )
        session.add(project)  # Client manages session
        await session.commit()  # Client manages commit
        await session.refresh(project)  # Client manages refresh
        print(f"✅ Created project ID: {project.id}")
        
        print(f"\n📖 READ: Manual session.get()")
        found_project = await session.get(Project, project.id)
        print(f"✅ Read project: {found_project.name}")
        
        print(f"\n✏️ UPDATE: Manual commit")
        found_project.name = "Updated Web App"
        await session.commit()  # Client manages commit again
        print(f"✅ Updated: {found_project.name}")
        
        print(f"\n🗑️ DELETE: Manual session.delete()")
        await session.delete(found_project)
        await session.commit()
        print("✅ Project deleted")
        
        print("\n❌ Too much boilerplate! Client manages:")
        print("   - Engine creation")
        print("   - Session maker")
        print("   - Session context")
        print("   - Manual commits")
        print("   - Table creation")
        print("\n✨ See ultra_simple_crud.py for the NEW simple way!")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())