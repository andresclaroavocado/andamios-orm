#!/usr/bin/env python3
"""
Example Runner for Andamios ORM

Description: Utility script to run all examples in sequence or individually.
Includes setup validation, database preparation, and cleanup.

Usage:
    python examples/run_examples.py                    # Run all examples
    python examples/run_examples.py basic              # Run basic examples only
    python examples/run_examples.py user_crud         # Run specific example
    python examples/run_examples.py --list            # List available examples
    python examples/run_examples.py --setup           # Setup test database only
"""

import asyncio
import uvloop
import sys
import os
import importlib
import argparse
from pathlib import Path
from typing import Dict, List, Callable, Optional
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Example configurations
EXAMPLES = {
    "basic": {
        "user_crud": {
            "module": "examples.basic.user_crud",
            "function": "main",
            "description": "Basic CRUD operations with User model",
            "duration": "~2 minutes"
        }
    },
    "advanced": {
        "relationships": {
            "module": "examples.advanced.relationships",
            "function": "main", 
            "description": "Complex model relationships and queries",
            "duration": "~3 minutes"
        }
    },
    "integration": {
        "fastapi_integration": {
            "module": "examples.integration.fastapi_integration",
            "function": "demo_api_usage",
            "description": "FastAPI integration demonstration",
            "duration": "~2 minutes",
            "requires": ["fastapi_server"]
        }
    }
}

DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_andamios_orm"

class ExampleRunner:
    """Runner for executing examples with proper setup and cleanup."""
    
    def __init__(self):
        self.results: Dict[str, bool] = {}
        self.start_time = datetime.now()
    
    async def check_database_connection(self) -> bool:
        """Check if database is available."""
        try:
            from andamios_orm.core.engine import create_async_engine
            
            engine = create_async_engine(DATABASE_URL, echo=False)
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            await engine.dispose()
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print(f"   Make sure PostgreSQL is running with test database setup")
            print(f"   URL: {DATABASE_URL}")
            return False
    
    async def setup_test_database(self) -> bool:
        """Setup test database schema."""
        try:
            print("🔧 Setting up test database...")
            
            # This would typically run migrations
            # For now, we'll create basic tables
            from andamios_orm.core.engine import create_async_engine
            
            engine = create_async_engine(DATABASE_URL, echo=False)
            
            # Create basic tables (simplified for example)
            async with engine.begin() as conn:
                # Drop existing tables
                await conn.execute("DROP TABLE IF EXISTS comments CASCADE")
                await conn.execute("DROP TABLE IF EXISTS post_tags CASCADE")
                await conn.execute("DROP TABLE IF EXISTS user_tags CASCADE")
                await conn.execute("DROP TABLE IF EXISTS posts CASCADE")
                await conn.execute("DROP TABLE IF EXISTS user_profiles CASCADE")
                await conn.execute("DROP TABLE IF EXISTS users CASCADE")
                await conn.execute("DROP TABLE IF EXISTS tags CASCADE")
                
                # Create users table
                await conn.execute("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        first_name VARCHAR(255) NOT NULL,
                        last_name VARCHAR(255) NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        is_verified BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create user_profiles table
                await conn.execute("""
                    CREATE TABLE user_profiles (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        bio TEXT,
                        avatar_url VARCHAR(255),
                        birth_date DATE,
                        location VARCHAR(255),
                        website VARCHAR(255),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create tags table
                await conn.execute("""
                    CREATE TABLE tags (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        slug VARCHAR(255) UNIQUE NOT NULL,
                        description TEXT,
                        color VARCHAR(7) DEFAULT '#6B7280'
                    )
                """)
                
                # Create posts table
                await conn.execute("""
                    CREATE TABLE posts (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        slug VARCHAR(255),
                        content TEXT NOT NULL,
                        excerpt TEXT,
                        status VARCHAR(50) DEFAULT 'draft',
                        is_published BOOLEAN DEFAULT FALSE,
                        published_at TIMESTAMP WITH TIME ZONE,
                        view_count INTEGER DEFAULT 0,
                        author_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create comments table
                await conn.execute("""
                    CREATE TABLE comments (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        status VARCHAR(50) DEFAULT 'pending',
                        post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                        author_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create junction tables
                await conn.execute("""
                    CREATE TABLE post_tags (
                        post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                        tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
                        PRIMARY KEY (post_id, tag_id)
                    )
                """)
                
                await conn.execute("""
                    CREATE TABLE user_tags (
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        PRIMARY KEY (user_id, tag_id)
                    )
                """)
            
            await engine.dispose()
            print("✅ Test database setup completed")
            return True
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False
    
    async def run_example(self, category: str, name: str, config: Dict) -> bool:
        """Run a single example."""
        try:
            print(f"\n🚀 Running {category}/{name}...")
            print(f"   Description: {config['description']}")
            print(f"   Duration: {config['duration']}")
            print("   " + "=" * 50)
            
            # Import and run the example
            module = importlib.import_module(config["module"])
            function = getattr(module, config["function"])
            
            await function()
            
            self.results[f"{category}/{name}"] = True
            print(f"✅ {category}/{name} completed successfully")
            return True
            
        except Exception as e:
            self.results[f"{category}/{name}"] = False
            print(f"❌ {category}/{name} failed: {e}")
            return False
    
    async def run_category(self, category: str) -> bool:
        """Run all examples in a category."""
        if category not in EXAMPLES:
            print(f"❌ Unknown category: {category}")
            return False
        
        print(f"\n📁 Running {category} examples...")
        
        success = True
        for name, config in EXAMPLES[category].items():
            result = await self.run_example(category, name, config)
            if not result:
                success = False
        
        return success
    
    async def run_all_examples(self) -> bool:
        """Run all examples."""
        print("🎯 Running all examples...")
        
        success = True
        for category in EXAMPLES:
            result = await self.run_category(category)
            if not result:
                success = False
        
        return success
    
    async def run_specific_example(self, example_name: str) -> bool:
        """Run a specific example by name."""
        for category, examples in EXAMPLES.items():
            if example_name in examples:
                return await self.run_example(category, example_name, examples[example_name])
        
        print(f"❌ Example '{example_name}' not found")
        return False
    
    def print_summary(self):
        """Print execution summary."""
        total = len(self.results)
        passed = sum(1 for result in self.results.values() if result)
        failed = total - passed
        
        duration = datetime.now() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Total examples: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Duration: {duration}")
        
        if self.results:
            print("\nDetailed results:")
            for example, success in self.results.items():
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"  {example}: {status}")
        
        return failed == 0

def list_examples():
    """List all available examples."""
    print("📋 Available Examples")
    print("=" * 40)
    
    for category, examples in EXAMPLES.items():
        print(f"\n📁 {category}:")
        for name, config in examples.items():
            print(f"  • {name}")
            print(f"    {config['description']}")
            print(f"    Duration: {config['duration']}")
            if "requires" in config:
                print(f"    Requires: {', '.join(config['requires'])}")

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run Andamios ORM examples")
    parser.add_argument("target", nargs="?", help="Category or example name to run")
    parser.add_argument("--list", action="store_true", help="List available examples")
    parser.add_argument("--setup", action="store_true", help="Setup test database only")
    parser.add_argument("--skip-db-check", action="store_true", help="Skip database connection check")
    
    args = parser.parse_args()
    
    if args.list:
        list_examples()
        return
    
    # Use uvloop for better performance
    if hasattr(uvloop, 'install'):
        uvloop.install()
    
    runner = ExampleRunner()
    
    print("🔧 Andamios ORM Examples Runner")
    print("=" * 50)
    
    # Check database connection
    if not args.skip_db_check:
        print("🔍 Checking database connection...")
        if not await runner.check_database_connection():
            print("\n💡 To fix database issues:")
            print("1. Make sure PostgreSQL is running")
            print("2. Create test database and user:")
            print("   CREATE USER test_user WITH PASSWORD 'test_password';")
            print("   CREATE DATABASE test_andamios_orm OWNER test_user;")
            print("3. Or run: docker-compose -f docker/test-databases.yml up -d")
            return
        print("✅ Database connection successful")
    
    # Setup database schema
    if not await runner.setup_test_database():
        return
    
    if args.setup:
        print("✅ Database setup completed")
        return
    
    # Run examples based on arguments
    success = True
    
    if not args.target:
        # Run all examples
        success = await runner.run_all_examples()
    elif args.target in EXAMPLES:
        # Run category
        success = await runner.run_category(args.target)
    else:
        # Run specific example
        success = await runner.run_specific_example(args.target)
    
    # Print summary
    overall_success = runner.print_summary()
    
    if overall_success:
        print("\n🎉 All examples completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some examples failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())