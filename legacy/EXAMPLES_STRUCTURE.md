# Example-Driven Development Structure

## Overview

This document outlines the comprehensive example structure for Project Architect DB, following example-driven development principles where clear, executable examples are created before implementation and tests.

## Example-Driven Development Philosophy

### Core Principles
1. **Examples First**: Write clear, practical examples before any implementation
2. **Executable Examples**: All examples must be runnable and self-contained
3. **Real-World Scenarios**: Examples demonstrate actual use cases, not toy problems
4. **Progressive Complexity**: Start simple, build to advanced scenarios
5. **Documentation Integration**: Examples serve as living documentation

### Development Flow
```
Examples → Tests → Implementation → Validation
```

## Directory Structure

```
examples/
├── README.md                    # Examples overview and quick start
├── requirements.txt             # Example-specific dependencies
├── conftest.py                 # Shared example fixtures
├── utils.py                    # Common example utilities
├── basic/                      # Basic usage patterns
│   ├── README.md
│   ├── __init__.py
│   ├── 01_project_crud.py      # Basic CRUD operations
│   ├── 02_conversation_flow.py # Managing conversations
│   ├── 03_document_handling.py # Document operations
│   ├── 04_repository_tracking.py # Repository management
│   └── 05_simple_queries.py    # Basic filtering and queries
├── advanced/                   # Advanced patterns and techniques
│   ├── README.md
│   ├── __init__.py
│   ├── 01_complex_queries.py   # Advanced querying techniques
│   ├── 02_analytics.py         # Analytics and reporting
│   ├── 03_bulk_operations.py   # High-performance bulk ops
│   ├── 04_json_queries.py      # JSON field manipulation
│   ├── 05_concurrent_access.py # Concurrent operation patterns
│   ├── 06_transaction_patterns.py # Advanced transaction handling
│   └── 07_custom_repositories.py # Custom repository patterns
├── integration/                # Framework and service integration
│   ├── README.md
│   ├── __init__.py
│   ├── 01_fastapi_integration.py # FastAPI integration
│   ├── 02_websocket_updates.py   # Real-time updates
│   ├── 03_background_tasks.py    # Background processing
│   ├── 04_api_endpoints.py       # REST API patterns
│   ├── 05_dependency_injection.py # DI patterns
│   └── 06_middleware_integration.py # Middleware usage
├── performance/                # Performance optimization examples
│   ├── README.md
│   ├── __init__.py
│   ├── 01_bulk_insert.py       # Optimized bulk operations
│   ├── 02_query_optimization.py # Query performance tuning
│   ├── 03_connection_pooling.py # Connection pool optimization
│   ├── 04_memory_efficiency.py  # Memory usage optimization
│   └── 05_monitoring.py        # Performance monitoring
├── workflows/                  # Complete business workflows
│   ├── README.md
│   ├── __init__.py
│   ├── 01_project_lifecycle.py # Complete project workflow
│   ├── 02_collaboration_flow.py # Multi-user collaboration
│   ├── 03_reporting_workflow.py # Analytics and reporting
│   └── 04_migration_workflow.py # Data migration patterns
└── troubleshooting/           # Common issues and solutions
    ├── README.md
    ├── __init__.py
    ├── 01_debugging_queries.py # Query debugging techniques
    ├── 02_performance_issues.py # Performance troubleshooting
    ├── 03_connection_issues.py  # Connection problem resolution
    └── 04_data_consistency.py   # Data consistency issues
```

## Basic Examples

### 01_project_crud.py - Basic CRUD Operations

```python
#!/usr/bin/env python3
"""
Basic CRUD Operations Example

This example demonstrates fundamental Create, Read, Update, Delete operations
for projects using Project Architect DB.

Run this example:
    python examples/basic/01_project_crud.py
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional

# Add src to path for examples
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from project_architect_db.core.engine import DatabaseEngine
from project_architect_db.repositories.project import ProjectRepository
from project_architect_db.schemas.project import ProjectCreate, ProjectUpdate, Project


async def create_project_example() -> Project:
    """Example: Creating a new project with validation"""
    print("🔄 Creating a new project...")
    
    # Create project data
    project_data = ProjectCreate(
        name="E-commerce Platform",
        description="A modern e-commerce platform with microservices architecture",
        project_idea="Build a scalable e-commerce platform using FastAPI and React",
        architecture={
            "framework": "FastAPI",
            "frontend": "React",
            "database": "DuckDB",
            "deployment": "Docker + Kubernetes",
            "complexity_score": 8,
            "estimated_duration": 16,  # weeks
            "team_size": 5
        },
        status="draft"
    )
    
    # Initialize database connection
    engine = DatabaseEngine("duckdb:///example_projects.db")
    
    async with engine.session() as session:
        async with ProjectRepository(session) as repo:
            project = await repo.create(project_data)
            print(f"✅ Created project: {project.name} (ID: {project.id})")
            return project


async def read_project_example(project_id: int) -> Optional[Project]:
    """Example: Reading a project by ID"""
    print(f"🔍 Reading project with ID: {project_id}")
    
    engine = DatabaseEngine("duckdb:///example_projects.db")
    
    async with engine.session() as session:
        async with ProjectRepository(session) as repo:
            project = await repo.get_by_id(project_id)
            
            if project:
                print(f"✅ Found project: {project.name}")
                print(f"   Status: {project.status}")
                print(f"   Framework: {project.architecture.get('framework', 'N/A')}")
                return project
            else:
                print(f"❌ Project with ID {project_id} not found")
                return None


async def update_project_example(project_id: int) -> Optional[Project]:
    """Example: Updating a project"""
    print(f"🔄 Updating project with ID: {project_id}")
    
    # Update data
    update_data = ProjectUpdate(
        status="active",
        architecture={
            "framework": "FastAPI",
            "frontend": "React",
            "database": "DuckDB", 
            "deployment": "Docker + Kubernetes",
            "complexity_score": 7,  # Reduced complexity
            "estimated_duration": 14,  # Reduced timeline
            "team_size": 5,
            "last_updated": "2024-01-15"
        }
    )
    
    engine = DatabaseEngine("duckdb:///example_projects.db")
    
    async with engine.session() as session:
        async with ProjectRepository(session) as repo:
            project = await repo.update(project_id, update_data)
            
            if project:
                print(f"✅ Updated project: {project.name}")
                print(f"   New status: {project.status}")
                print(f"   Updated complexity: {project.architecture.get('complexity_score')}")
                return project
            else:
                print(f"❌ Failed to update project with ID {project_id}")
                return None


async def list_projects_example() -> List[Project]:
    """Example: Listing projects with filtering"""
    print("📋 Listing all active projects...")
    
    engine = DatabaseEngine("duckdb:///example_projects.db")
    
    async with engine.session() as session:
        async with ProjectRepository(session) as repo:
            # Get active projects
            active_projects = await repo.get_by_status("active")
            
            print(f"✅ Found {len(active_projects)} active projects:")
            for project in active_projects:
                framework = project.architecture.get('framework', 'Unknown')
                print(f"   • {project.name} ({framework})")
            
            return active_projects


async def delete_project_example(project_id: int) -> bool:
    """Example: Soft deleting a project"""
    print(f"🗑️  Deleting project with ID: {project_id}")
    
    engine = DatabaseEngine("duckdb:///example_projects.db")
    
    async with engine.session() as session:
        async with ProjectRepository(session) as repo:
            success = await repo.delete(project_id)
            
            if success:
                print(f"✅ Successfully deleted project with ID {project_id}")
            else:
                print(f"❌ Failed to delete project with ID {project_id}")
            
            return success


async def search_projects_example(query: str) -> List[Project]:
    """Example: Searching projects by name"""
    print(f"🔍 Searching for projects matching: '{query}'")
    
    engine = DatabaseEngine("duckdb:///example_projects.db")
    
    async with engine.session() as session:
        async with ProjectRepository(session) as repo:
            projects = await repo.search_by_name(query)
            
            print(f"✅ Found {len(projects)} projects matching '{query}':")
            for project in projects:
                print(f"   • {project.name} - {project.status}")
            
            return projects


async def main():
    """Run all CRUD examples"""
    print("🚀 Project Architect DB - Basic CRUD Examples")
    print("=" * 50)
    
    try:
        # Create
        project = await create_project_example()
        project_id = project.id
        
        print()
        
        # Read
        await read_project_example(project_id)
        
        print()
        
        # Update
        await update_project_example(project_id)
        
        print()
        
        # List
        await list_projects_example()
        
        print()
        
        # Search
        await search_projects_example("E-commerce")
        
        print()
        
        # Note: Uncomment to test delete
        # await delete_project_example(project_id)
        
        print("✅ All CRUD examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Example failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
```

### 02_conversation_flow.py - Managing Conversations

```python
#!/usr/bin/env python3
"""
Conversation Flow Management Example

This example demonstrates how to manage conversations and their phases
in Project Architect DB.

Run this example:
    python examples/basic/02_conversation_flow.py
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# Add src to path for examples
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from project_architect_db.core.engine import DatabaseEngine
from project_architect_db.repositories.project import ProjectRepository
from project_architect_db.repositories.conversation import ConversationRepository
from project_architect_db.schemas.project import ProjectCreate
from project_architect_db.schemas.conversation import ConversationCreate, ConversationUpdate


async def create_project_for_conversations():
    """Create a project to associate conversations with"""
    engine = DatabaseEngine("duckdb:///example_conversations.db")
    
    project_data = ProjectCreate(
        name="Mobile Banking App",
        description="Secure mobile banking application",
        project_idea="Create a mobile banking app with biometric authentication",
        status="active"
    )
    
    async with engine.session() as session:
        async with ProjectRepository(session) as repo:
            return await repo.create(project_data)


async def create_conversation_example(project_id: int):
    """Example: Creating a new conversation"""
    print("💬 Creating a new conversation...")
    
    conversation_data = ConversationCreate(
        project_id=project_id,
        phase="project_idea",
        messages=[
            {
                "role": "user",
                "content": "I want to create a mobile banking app with biometric authentication",
                "timestamp": datetime.now().isoformat()
            },
            {
                "role": "assistant",
                "content": "Great idea! Let's start by discussing the core features and security requirements for your mobile banking app.",
                "timestamp": datetime.now().isoformat()
            }
        ]
    )
    
    engine = DatabaseEngine("duckdb:///example_conversations.db")
    
    async with engine.session() as session:
        async with ConversationRepository(session) as repo:
            conversation = await repo.create(conversation_data)
            print(f"✅ Created conversation in {conversation.phase} phase")
            return conversation


async def add_message_example(conversation_id: int):
    """Example: Adding a message to existing conversation"""
    print(f"📝 Adding message to conversation {conversation_id}...")
    
    new_message = {
        "role": "user",
        "content": "What security features should I prioritize?",
        "timestamp": datetime.now().isoformat()
    }
    
    engine = DatabaseEngine("duckdb:///example_conversations.db")
    
    async with engine.session() as session:
        async with ConversationRepository(session) as repo:
            conversation = await repo.add_message(conversation_id, new_message)
            
            if conversation:
                print(f"✅ Added message. Total messages: {len(conversation.messages)}")
                return conversation
            else:
                print(f"❌ Failed to add message to conversation {conversation_id}")
                return None


async def update_conversation_phase_example(conversation_id: int):
    """Example: Moving conversation to next phase"""
    print(f"🔄 Moving conversation {conversation_id} to architecture phase...")
    
    update_data = ConversationUpdate(
        phase="architecture"
    )
    
    engine = DatabaseEngine("duckdb:///example_conversations.db")
    
    async with engine.session() as session:
        async with ConversationRepository(session) as repo:
            conversation = await repo.update(conversation_id, update_data)
            
            if conversation:
                print(f"✅ Conversation moved to {conversation.phase} phase")
                return conversation
            else:
                print(f"❌ Failed to update conversation {conversation_id}")
                return None


async def get_conversations_by_project_example(project_id: int):
    """Example: Getting all conversations for a project"""
    print(f"📋 Getting conversations for project {project_id}...")
    
    engine = DatabaseEngine("duckdb:///example_conversations.db")
    
    async with engine.session() as session:
        async with ConversationRepository(session) as repo:
            conversations = await repo.get_by_project(project_id)
            
            print(f"✅ Found {len(conversations)} conversations:")
            for conv in conversations:
                print(f"   • Phase: {conv.phase}, Messages: {len(conv.messages)}")
            
            return conversations


async def get_conversations_by_phase_example(phase: str):
    """Example: Getting conversations in specific phase"""
    print(f"🔍 Getting conversations in {phase} phase...")
    
    engine = DatabaseEngine("duckdb:///example_conversations.db")
    
    async with engine.session() as session:
        async with ConversationRepository(session) as repo:
            conversations = await repo.get_by_phase(phase)
            
            print(f"✅ Found {len(conversations)} conversations in {phase} phase")
            return conversations


async def conversation_analytics_example():
    """Example: Getting conversation analytics"""
    print("📊 Getting conversation analytics...")
    
    engine = DatabaseEngine("duckdb:///example_conversations.db")
    
    async with engine.session() as session:
        async with ConversationRepository(session) as repo:
            analytics = await repo.conversation_analytics()
            
            print("✅ Conversation Analytics:")
            print(f"   • Total conversations: {analytics.total_conversations}")
            print(f"   • Average messages per conversation: {analytics.avg_messages_per_conversation:.1f}")
            print(f"   • Most common phase: {analytics.most_common_phase}")
            print(f"   • Phase distribution: {analytics.phase_distribution}")
            
            return analytics


async def simulate_conversation_workflow(project_id: int):
    """Example: Simulate a complete conversation workflow"""
    print("🔄 Simulating complete conversation workflow...")
    
    engine = DatabaseEngine("duckdb:///example_conversations.db")
    
    # Phase 1: Project Idea
    conversation_data = ConversationCreate(
        project_id=project_id,
        phase="project_idea",
        messages=[
            {
                "role": "user",
                "content": "I need help designing a mobile banking app",
                "timestamp": datetime.now().isoformat()
            }
        ]
    )
    
    async with engine.session() as session:
        async with ConversationRepository(session) as repo:
            conv = await repo.create(conversation_data)
            conv_id = conv.id
            
            # Add more messages to project_idea phase
            await repo.add_message(conv_id, {
                "role": "assistant",
                "content": "Let's discuss the key features and target audience",
                "timestamp": datetime.now().isoformat()
            })
            
            # Move to architecture phase
            conv = await repo.update(conv_id, ConversationUpdate(phase="architecture"))
            
            # Add architecture discussions
            await repo.add_message(conv_id, {
                "role": "user", 
                "content": "I'm thinking microservices architecture",
                "timestamp": datetime.now().isoformat()
            })
            
            await repo.add_message(conv_id, {
                "role": "assistant",
                "content": "Great choice! Let's design the service boundaries",
                "timestamp": datetime.now().isoformat()
            })
            
            # Move to implementation phase
            conv = await repo.update(conv_id, ConversationUpdate(phase="implementation"))
            
            print(f"✅ Simulated workflow: {conv.phase} phase with {len(conv.messages)} messages")
            return conv


async def main():
    """Run all conversation flow examples"""
    print("🚀 Project Architect DB - Conversation Flow Examples")
    print("=" * 55)
    
    try:
        # Create project for conversations
        project = await create_project_for_conversations()
        project_id = project.id
        print(f"📁 Created project: {project.name} (ID: {project_id})")
        print()
        
        # Basic conversation operations
        conversation = await create_conversation_example(project_id)
        conversation_id = conversation.id
        
        print()
        await add_message_example(conversation_id)
        
        print()
        await update_conversation_phase_example(conversation_id)
        
        print()
        await get_conversations_by_project_example(project_id)
        
        print()
        await get_conversations_by_phase_example("architecture")
        
        print()
        # Simulate complete workflow
        await simulate_conversation_workflow(project_id)
        
        print()
        await conversation_analytics_example()
        
        print()
        print("✅ All conversation flow examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Example failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Examples

### 01_complex_queries.py - Advanced Querying

```python
#!/usr/bin/env python3
"""
Complex Queries Example

This example demonstrates advanced querying capabilities including
JSON field queries, aggregations, and complex filtering.

Run this example:
    python examples/advanced/01_complex_queries.py
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for examples
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from project_architect_db.core.engine import DatabaseEngine
from project_architect_db.repositories.project import ProjectRepository
from project_architect_db.queries.builder import QueryBuilder
from project_architect_db.schemas.project import ProjectCreate


async def setup_sample_data():
    """Create sample projects with diverse architectures"""
    print("🔧 Setting up sample data...")
    
    sample_projects = [
        ProjectCreate(
            name="E-commerce Platform",
            description="Scalable e-commerce solution",
            project_idea="Build microservices-based e-commerce platform",
            architecture={
                "framework": "FastAPI",
                "frontend": "React",
                "database": "PostgreSQL",
                "complexity_score": 8,
                "team_size": 6,
                "technologies": ["Python", "JavaScript", "Docker", "Kubernetes"]
            },
            status="active"
        ),
        ProjectCreate(
            name="Analytics Dashboard",
            description="Real-time analytics dashboard",
            project_idea="Create dashboard for business intelligence",
            architecture={
                "framework": "Django",
                "frontend": "Vue.js",
                "database": "DuckDB",
                "complexity_score": 6,
                "team_size": 4,
                "technologies": ["Python", "JavaScript", "Redis", "Celery"]
            },
            status="completed"
        ),
        ProjectCreate(
            name="Mobile Banking App",
            description="Secure mobile banking solution",
            project_idea="Build mobile app with biometric authentication",
            architecture={
                "framework": "FastAPI",
                "frontend": "React Native",
                "database": "PostgreSQL",
                "complexity_score": 9,
                "team_size": 8,
                "technologies": ["Python", "React Native", "Docker", "GraphQL"]
            },
            status="active"
        ),
        ProjectCreate(
            name="Content Management System",
            description="Flexible CMS for multiple sites",
            project_idea="Build headless CMS with API-first approach",
            architecture={
                "framework": "Flask",
                "frontend": "Next.js",
                "database": "SQLite",
                "complexity_score": 5,
                "team_size": 3,
                "technologies": ["Python", "TypeScript", "REST"]
            },
            status="draft"
        )
    ]
    
    engine = DatabaseEngine("duckdb:///complex_queries.db")
    
    async with engine.session() as session:
        async with ProjectRepository(session) as repo:
            projects = []
            for project_data in sample_projects:
                project = await repo.create(project_data)
                projects.append(project)
            
            print(f"✅ Created {len(projects)} sample projects")
            return projects


async def json_field_queries_example():
    """Example: Querying JSON fields with DuckDB functions"""
    print("🔍 JSON Field Queries Example")
    print("-" * 30)
    
    engine = DatabaseEngine("duckdb:///complex_queries.db")
    
    async with engine.session() as session:
        # Query projects using FastAPI framework
        fastapi_projects = await (QueryBuilder(Project, session)
            .filter_json("architecture", "$.framework", "FastAPI")
            .all())
        
        print(f"✅ Found {len(fastapi_projects)} FastAPI projects:")
        for project in fastapi_projects:
            framework = project.architecture.get('framework')
            print(f"   • {project.name} - {framework}")
        
        print()
        
        # Query projects with complexity score > 7
        complex_projects = await (QueryBuilder(Project, session)
            .filter_json_numeric("architecture", "$.complexity_score", ">", 7)
            .all())
        
        print(f"✅ Found {len(complex_projects)} high-complexity projects:")
        for project in complex_projects:
            score = project.architecture.get('complexity_score')
            print(f"   • {project.name} - Complexity: {score}")
        
        print()
        
        # Query projects with specific technology
        docker_projects = await (QueryBuilder(Project, session)
            .filter_json_array_contains("architecture", "$.technologies", "Docker")
            .all())
        
        print(f"✅ Found {len(docker_projects)} projects using Docker:")
        for project in docker_projects:
            techs = project.architecture.get('technologies', [])
            print(f"   • {project.name} - Technologies: {', '.join(techs)}")


async def aggregation_queries_example():
    """Example: Complex aggregation queries"""
    print("📊 Aggregation Queries Example")
    print("-" * 30)
    
    engine = DatabaseEngine("duckdb:///complex_queries.db")
    
    async with engine.session() as session:
        # Framework popularity analysis
        framework_stats = await (QueryBuilder(Project, session)
            .group_by_json("architecture", "$.framework")
            .aggregate([
                func.count().label("project_count"),
                func.avg(func.json_extract("architecture", "$.complexity_score")).label("avg_complexity"),
                func.sum(func.json_extract("architecture", "$.team_size")).label("total_team_size")
            ])
            .all())
        
        print("✅ Framework Statistics:")
        for stat in framework_stats:
            print(f"   • {stat.framework}: {stat.project_count} projects, "
                  f"Avg Complexity: {stat.avg_complexity:.1f}, "
                  f"Total Team Size: {stat.total_team_size}")
        
        print()
        
        # Status distribution with complexity analysis
        status_complexity = await (QueryBuilder(Project, session)
            .group_by("status")
            .aggregate([
                func.count().label("count"),
                func.min(func.json_extract("architecture", "$.complexity_score")).label("min_complexity"),
                func.max(func.json_extract("architecture", "$.complexity_score")).label("max_complexity"),
                func.avg(func.json_extract("architecture", "$.complexity_score")).label("avg_complexity")
            ])
            .all())
        
        print("✅ Status vs Complexity Analysis:")
        for stat in status_complexity:
            print(f"   • {stat.status}: {stat.count} projects, "
                  f"Complexity Range: {stat.min_complexity}-{stat.max_complexity}, "
                  f"Average: {stat.avg_complexity:.1f}")


async def time_based_queries_example():
    """Example: Time-based filtering and analysis"""
    print("⏰ Time-Based Queries Example")
    print("-" * 30)
    
    engine = DatabaseEngine("duckdb:///complex_queries.db")
    
    # Get date ranges
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    async with engine.session() as session:
        # Recent projects
        recent_projects = await (QueryBuilder(Project, session)
            .filter_by_date_range("created_at", start_date, end_date)
            .order_by(Project.created_at.desc())
            .all())
        
        print(f"✅ Found {len(recent_projects)} projects created in last 30 days:")
        for project in recent_projects:
            print(f"   • {project.name} - Created: {project.created_at.strftime('%Y-%m-%d')}")
        
        print()
        
        # Time series analysis
        daily_stats = await (QueryBuilder(Project, session)
            .time_series_analysis("created_at", "day")
            .aggregate([
                func.count().label("projects_created"),
                func.avg(func.json_extract("architecture", "$.complexity_score")).label("avg_complexity")
            ])
            .all())
        
        print("✅ Daily Creation Statistics:")
        for stat in daily_stats:
            print(f"   • {stat.date}: {stat.projects_created} projects, "
                  f"Avg Complexity: {stat.avg_complexity:.1f}")


async def combined_complex_query_example():
    """Example: Complex multi-condition query"""
    print("🔬 Combined Complex Query Example") 
    print("-" * 35)
    
    engine = DatabaseEngine("duckdb:///complex_queries.db")
    
    async with engine.session() as session:
        # Find active FastAPI projects with high complexity and large teams
        complex_query_result = await (QueryBuilder(Project, session)
            .filter(status="active")
            .filter_json("architecture", "$.framework", "FastAPI")
            .filter_json_numeric("architecture", "$.complexity_score", ">=", 8)
            .filter_json_numeric("architecture", "$.team_size", ">=", 5)
            .filter_json_array_contains("architecture", "$.technologies", "Docker")
            .order_by(
                func.json_extract("architecture", "$.complexity_score").desc(),
                Project.created_at.desc()
            )
            .limit(10)
            .all())
        
        print("✅ Active FastAPI projects (Complex, Large Team, Docker):")
        for project in complex_query_result:
            arch = project.architecture
            print(f"   • {project.name}")
            print(f"     Framework: {arch.get('framework')}")
            print(f"     Complexity: {arch.get('complexity_score')}")
            print(f"     Team Size: {arch.get('team_size')}")
            print(f"     Technologies: {', '.join(arch.get('technologies', []))}")
            print()


async def subquery_example():
    """Example: Using subqueries for complex analysis"""
    print("🔍 Subquery Example")
    print("-" * 20)
    
    engine = DatabaseEngine("duckdb:///complex_queries.db")
    
    async with engine.session() as session:
        # Find projects with above-average complexity
        avg_complexity_subquery = (
            select(func.avg(func.json_extract(Project.architecture, "$.complexity_score")))
            .scalar_subquery()
        )
        
        above_avg_projects = await (QueryBuilder(Project, session)
            .filter(
                func.json_extract(Project.architecture, "$.complexity_score") > avg_complexity_subquery
            )
            .order_by(func.json_extract(Project.architecture, "$.complexity_score").desc())
            .all())
        
        print(f"✅ Found {len(above_avg_projects)} projects with above-average complexity:")
        for project in above_avg_projects:
            complexity = project.architecture.get('complexity_score')
            print(f"   • {project.name} - Complexity: {complexity}")


async def window_function_example():
    """Example: Using window functions for advanced analytics"""
    print("📈 Window Function Example")
    print("-" * 25)
    
    engine = DatabaseEngine("duckdb:///complex_queries.db")
    
    async with engine.session() as session:
        # Rank projects by complexity within each status
        ranked_projects = await session.execute(
            select(
                Project.name,
                Project.status,
                func.json_extract(Project.architecture, "$.complexity_score").label("complexity"),
                func.rank().over(
                    partition_by=Project.status,
                    order_by=func.json_extract(Project.architecture, "$.complexity_score").desc()
                ).label("complexity_rank"),
                func.row_number().over(
                    order_by=Project.created_at.desc()
                ).label("creation_order")
            )
        )
        
        print("✅ Project Rankings by Complexity within Status:")
        for row in ranked_projects:
            print(f"   • {row.name} ({row.status})")
            print(f"     Complexity: {row.complexity}, Rank: {row.complexity_rank}")
            print(f"     Creation Order: {row.creation_order}")
            print()


async def main():
    """Run all complex query examples"""
    print("🚀 Project Architect DB - Complex Queries Examples")
    print("=" * 55)
    
    try:
        # Setup sample data
        await setup_sample_data()
        print()
        
        # JSON field queries
        await json_field_queries_example()
        print()
        
        # Aggregation queries
        await aggregation_queries_example()
        print()
        
        # Time-based queries
        await time_based_queries_example()
        print()
        
        # Combined complex query
        await combined_complex_query_example()
        print()
        
        # Subquery example
        await subquery_example()
        print()
        
        # Window functions
        await window_function_example()
        
        print("✅ All complex query examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Example failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
```

## Integration Examples

### 01_fastapi_integration.py - FastAPI Integration

```python
#!/usr/bin/env python3
"""
FastAPI Integration Example

This example demonstrates how to integrate Project Architect DB
with FastAPI for building REST APIs.

Run this example:
    uvicorn examples.integration.01_fastapi_integration:app --reload
    
Then visit: http://localhost:8000/docs
"""

import asyncio
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

# Import our database components
from project_architect_db.core.engine import DatabaseEngine
from project_architect_db.repositories.project import ProjectRepository
from project_architect_db.repositories.conversation import ConversationRepository
from project_architect_db.repositories.analytics import AnalyticsRepository
from project_architect_db.schemas.project import Project, ProjectCreate, ProjectUpdate
from project_architect_db.schemas.conversation import Conversation, ConversationCreate
from project_architect_db.schemas.analytics import ProjectMetrics


# Global database engine
db_engine: Optional[DatabaseEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    global db_engine
    
    # Startup
    print("🚀 Starting Project Architect API...")
    db_engine = DatabaseEngine("duckdb:///fastapi_example.db")
    await db_engine.initialize()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Project Architect API...")
    if db_engine:
        await db_engine.close()
    print("✅ Database connections closed")


# Create FastAPI app with lifespan management
app = FastAPI(
    title="Project Architect API",
    description="API for managing software project architecture and conversations",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection
async def get_db_session() -> AsyncSession:
    """Get database session for dependency injection"""
    if not db_engine:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    async with db_engine.session() as session:
        yield session


async def get_project_repository(
    session: AsyncSession = Depends(get_db_session)
) -> ProjectRepository:
    """Get project repository"""
    return ProjectRepository(session)


async def get_conversation_repository(
    session: AsyncSession = Depends(get_db_session)
) -> ConversationRepository:
    """Get conversation repository"""
    return ConversationRepository(session)


async def get_analytics_repository(
    session: AsyncSession = Depends(get_db_session)
) -> AnalyticsRepository:
    """Get analytics repository"""
    return AnalyticsRepository(session)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Project Architect API"
    }


# Project endpoints
@app.post("/projects/", response_model=Project, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    repo: ProjectRepository = Depends(get_project_repository)
):
    """Create a new project"""
    try:
        async with repo:
            project = await repo.create(project_data)
            return project
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/projects/", response_model=List[Project])
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by project status"),
    framework: Optional[str] = Query(None, description="Filter by framework"),
    limit: int = Query(100, ge=1, le=1000, description="Number of projects to return"),
    offset: int = Query(0, ge=0, description="Number of projects to skip"),
    repo: ProjectRepository = Depends(get_project_repository)
):
    """List projects with optional filtering"""
    try:
        async with repo:
            if status:
                projects = await repo.get_by_status(status)
            elif framework:
                projects = await repo.get_by_framework(framework)
            else:
                projects = await repo.list(limit=limit, offset=offset)
            
            return projects
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    include_relations: bool = Query(False, description="Include conversations, docs, repos"),
    repo: ProjectRepository = Depends(get_project_repository)
):
    """Get a specific project by ID"""
    try:
        async with repo:
            if include_relations:
                project = await repo.get_with_conversations(project_id)
            else:
                project = await repo.get_by_id(project_id)
            
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: int,
    update_data: ProjectUpdate,
    repo: ProjectRepository = Depends(get_project_repository)
):
    """Update a project"""
    try:
        async with repo:
            project = await repo.update(project_id, update_data)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    repo: ProjectRepository = Depends(get_project_repository)
):
    """Delete a project (soft delete)"""
    try:
        async with repo:
            success = await repo.delete(project_id)
            if not success:
                raise HTTPException(status_code=404, detail="Project not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/projects/{project_id}/conversations/", response_model=List[Conversation])
async def get_project_conversations(
    project_id: int,
    phase: Optional[str] = Query(None, description="Filter by conversation phase"),
    repo: ConversationRepository = Depends(get_conversation_repository)
):
    """Get conversations for a project"""
    try:
        async with repo:
            if phase:
                conversations = await repo.get_by_project_and_phase(project_id, phase)
            else:
                conversations = await repo.get_by_project(project_id)
            return conversations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/projects/{project_id}/conversations/", response_model=Conversation, status_code=201)
async def create_conversation(
    project_id: int,
    conversation_data: ConversationCreate,
    repo: ConversationRepository = Depends(get_conversation_repository)
):
    """Create a new conversation for a project"""
    try:
        # Ensure project_id matches
        conversation_data.project_id = project_id
        
        async with repo:
            conversation = await repo.create(conversation_data)
            return conversation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Analytics endpoints
@app.get("/analytics/projects", response_model=ProjectMetrics)
async def get_project_analytics(
    date_from: Optional[datetime] = Query(None, description="Start date for analytics"),
    date_to: Optional[datetime] = Query(None, description="End date for analytics"),
    repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Get project analytics and metrics"""
    try:
        async with repo:
            date_range = (date_from, date_to) if date_from and date_to else None
            metrics = await repo.project_metrics(date_range)
            return metrics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/analytics/frameworks")
async def get_framework_analytics(
    repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Get framework usage analytics"""
    try:
        async with repo:
            framework_stats = await repo.framework_popularity()
            return {
                "framework_distribution": framework_stats,
                "generated_at": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Search endpoints
@app.get("/search/projects", response_model=List[Project])
async def search_projects(
    q: str = Query(..., min_length=1, description="Search query"),
    repo: ProjectRepository = Depends(get_project_repository)
):
    """Search projects by name and description"""
    try:
        async with repo:
            projects = await repo.search_by_name(q)
            return projects
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Background task example
async def generate_project_report(project_id: int):
    """Background task to generate project report"""
    # Simulate report generation
    await asyncio.sleep(5)
    print(f"✅ Generated report for project {project_id}")


@app.post("/projects/{project_id}/reports", status_code=202)
async def generate_report(
    project_id: int,
    background_tasks: BackgroundTasks,
    repo: ProjectRepository = Depends(get_project_repository)
):
    """Generate project report (background task)"""
    try:
        async with repo:
            project = await repo.get_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Add background task
            background_tasks.add_task(generate_project_report, project_id)
            
            return {
                "message": "Report generation started",
                "project_id": project_id,
                "status": "processing"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# WebSocket endpoint for real-time updates
@app.websocket("/ws/projects/{project_id}")
async def project_websocket(websocket: WebSocket, project_id: int):
    """WebSocket endpoint for real-time project updates"""
    await websocket.accept()
    
    try:
        while True:
            # In a real implementation, you would:
            # 1. Listen for database changes
            # 2. Send updates to connected clients
            # 3. Handle client messages
            
            data = await websocket.receive_text()
            
            # Echo for demo purposes
            await websocket.send_text(f"Project {project_id} update: {data}")
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Project Architect FastAPI Example")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Interactive API: http://localhost:8000/redoc")
    
    uvicorn.run(
        "examples.integration.01_fastapi_integration:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

## Example Execution and Validation

### Example Runner Script

```python
#!/usr/bin/env python3
"""
Example Runner and Validator

This script runs all examples to ensure they work correctly
and validates their outputs.

Run this script:
    python examples/run_examples.py
"""

import asyncio
import importlib
import sys
from pathlib import Path
from typing import List, Dict, Any
import traceback


class ExampleRunner:
    """Runs and validates examples"""
    
    def __init__(self):
        self.examples_root = Path(__file__).parent
        self.results: Dict[str, Any] = {}
    
    async def run_basic_examples(self) -> Dict[str, bool]:
        """Run all basic examples"""
        print("🔄 Running Basic Examples...")
        print("-" * 30)
        
        basic_examples = [
            "basic.01_project_crud",
            "basic.02_conversation_flow",
            "basic.03_document_handling",
            "basic.04_repository_tracking",
            "basic.05_simple_queries"
        ]
        
        results = {}
        for example in basic_examples:
            try:
                print(f"Running {example}...")
                module = importlib.import_module(f"examples.{example}")
                
                if hasattr(module, 'main'):
                    await module.main()
                    results[example] = True
                    print(f"✅ {example} completed successfully")
                else:
                    results[example] = False
                    print(f"❌ {example} missing main() function")
                    
            except Exception as e:
                results[example] = False
                print(f"❌ {example} failed: {e}")
                traceback.print_exc()
            
            print()
        
        return results
    
    async def run_advanced_examples(self) -> Dict[str, bool]:
        """Run all advanced examples"""
        print("🔄 Running Advanced Examples...")
        print("-" * 30)
        
        advanced_examples = [
            "advanced.01_complex_queries",
            "advanced.02_analytics", 
            "advanced.03_bulk_operations",
            "advanced.04_json_queries",
            "advanced.05_concurrent_access",
            "advanced.06_transaction_patterns",
            "advanced.07_custom_repositories"
        ]
        
        results = {}
        for example in advanced_examples:
            try:
                print(f"Running {example}...")
                module = importlib.import_module(f"examples.{example}")
                
                if hasattr(module, 'main'):
                    await module.main()
                    results[example] = True
                    print(f"✅ {example} completed successfully")
                else:
                    results[example] = False
                    print(f"❌ {example} missing main() function")
                    
            except Exception as e:
                results[example] = False
                print(f"❌ {example} failed: {e}")
                traceback.print_exc()
            
            print()
        
        return results
    
    async def validate_example_outputs(self) -> Dict[str, bool]:
        """Validate that examples produce expected outputs"""
        print("🔍 Validating Example Outputs...")
        print("-" * 30)
        
        validations = {}
        
        # Check if database files were created
        db_files = [
            "example_projects.db",
            "example_conversations.db", 
            "complex_queries.db",
            "fastapi_example.db"
        ]
        
        for db_file in db_files:
            db_path = Path(db_file)
            if db_path.exists():
                validations[f"{db_file}_exists"] = True
                print(f"✅ {db_file} created successfully")
                
                # Check file size (should have content)
                if db_path.stat().st_size > 0:
                    validations[f"{db_file}_has_content"] = True
                    print(f"✅ {db_file} has content ({db_path.stat().st_size} bytes)")
                else:
                    validations[f"{db_file}_has_content"] = False
                    print(f"❌ {db_file} is empty")
            else:
                validations[f"{db_file}_exists"] = False
                print(f"❌ {db_file} not found")
        
        return validations
    
    async def cleanup_example_databases(self):
        """Clean up example database files"""
        print("🧹 Cleaning up example databases...")
        
        db_files = [
            "example_projects.db",
            "example_conversations.db",
            "complex_queries.db", 
            "fastapi_example.db"
        ]
        
        for db_file in db_files:
            db_path = Path(db_file)
            if db_path.exists():
                try:
                    db_path.unlink()
                    print(f"✅ Removed {db_file}")
                except Exception as e:
                    print(f"❌ Failed to remove {db_file}: {e}")
    
    def generate_report(self) -> str:
        """Generate example execution report"""
        report = ["", "📊 Example Execution Report", "=" * 50]
        
        total_examples = 0
        successful_examples = 0
        
        for category, results in self.results.items():
            report.append(f"\n{category.title()} Examples:")
            report.append("-" * (len(category) + 10))
            
            for example, success in results.items():
                status = "✅ PASS" if success else "❌ FAIL"
                report.append(f"  {example}: {status}")
                total_examples += 1
                if success:
                    successful_examples += 1
        
        success_rate = (successful_examples / total_examples) * 100 if total_examples > 0 else 0
        
        report.extend([
            f"\nSummary:",
            f"Total Examples: {total_examples}",
            f"Successful: {successful_examples}",
            f"Failed: {total_examples - successful_examples}",
            f"Success Rate: {success_rate:.1f}%"
        ])
        
        if success_rate == 100:
            report.append("\n🎉 All examples executed successfully!")
        else:
            report.append(f"\n⚠️  {total_examples - successful_examples} examples failed")
        
        return "\n".join(report)
    
    async def run_all_examples(self):
        """Run all examples and generate report"""
        print("🚀 Project Architect DB - Example Runner")
        print("=" * 50)
        
        try:
            # Run basic examples
            self.results["basic"] = await self.run_basic_examples()
            
            # Run advanced examples
            self.results["advanced"] = await self.run_advanced_examples()
            
            # Validate outputs
            self.results["validation"] = await self.validate_example_outputs()
            
            # Generate and print report
            report = self.generate_report()
            print(report)
            
            # Cleanup
            await self.cleanup_example_databases()
            
        except Exception as e:
            print(f"❌ Example runner failed: {e}")
            traceback.print_exc()


async def main():
    """Main example runner entry point"""
    runner = ExampleRunner()
    await runner.run_all_examples()


if __name__ == "__main__":
    asyncio.run(main())
```

This comprehensive example structure provides:

1. **Clear Learning Path**: Basic → Advanced → Integration → Performance
2. **Executable Examples**: All examples can be run independently
3. **Real-World Scenarios**: Examples demonstrate practical use cases
4. **Progressive Complexity**: Building from simple CRUD to complex analytics
5. **Framework Integration**: Shows how to integrate with FastAPI and other frameworks
6. **Validation System**: Automated testing of all examples
7. **Documentation Integration**: Examples serve as living documentation

The examples follow the example-driven development philosophy where they are created first, then used to drive test creation and implementation.