#!/usr/bin/env python3
"""
Example Runner for Andamios ORM - Ultra-Simple EDD

Description: Run ultra-simple Example-Driven Development examples.
4 total examples: 1 comprehensive CRUD example per model

Usage:
    python examples/run_examples.py                    # Run all 4 examples
    python examples/run_examples.py project_crud      # Run specific example
    python examples/run_examples.py --list            # List all 4 examples
"""

import asyncio
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

# Ultra-simple EDD examples - 1 comprehensive CRUD example per model = 4 examples
EXAMPLES = {
    "project_crud": {
        "module": "examples.basic.project_crud",
        "function": "main",
        "description": "Project CRUD: CREATE → READ → UPDATE → DELETE operations",
        "duration": "~15 seconds"
    },
    "conversation_crud": {
        "module": "examples.basic.conversation_crud",
        "function": "main",
        "description": "Conversation CRUD: CREATE → READ → UPDATE → DELETE operations",
        "duration": "~15 seconds"
    },
    "document_crud": {
        "module": "examples.basic.document_crud",
        "function": "main",
        "description": "Document CRUD: CREATE → READ → UPDATE → DELETE operations",
        "duration": "~15 seconds"
    },
    "repository_crud": {
        "module": "examples.basic.repository_crud",
        "function": "main",
        "description": "Repository CRUD: CREATE → READ → UPDATE → DELETE operations",
        "duration": "~15 seconds"
    }
}

class ExampleRunner:
    """Runner for executing examples with proper setup and cleanup."""
    
    def __init__(self):
        self.results: Dict[str, bool] = {}
        self.start_time = datetime.now()
    
    async def run_example(self, name: str, config: Dict) -> bool:
        """Run a single example."""
        try:
            print(f"\n🚀 Running {name}...")
            print(f"   Description: {config['description']}")
            print(f"   Duration: {config['duration']}")
            print("   " + "=" * 50)
            
            # Import and run the example
            module = importlib.import_module(config["module"])
            function = getattr(module, config["function"])
            
            await function()
            
            self.results[name] = True
            print(f"✅ {name} completed successfully")
            return True
            
        except Exception as e:
            self.results[name] = False
            print(f"❌ {name} failed: {e}")
            return False
    
    async def run_all_examples(self) -> bool:
        """Run all examples."""
        print("🎯 Running all examples...")
        
        success = True
        for name, config in EXAMPLES.items():
            result = await self.run_example(name, config)
            if not result:
                success = False
        
        return success
    
    async def run_specific_example(self, example_name: str) -> bool:
        """Run a specific example by name."""
        if example_name in EXAMPLES:
            return await self.run_example(example_name, EXAMPLES[example_name])
        
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
    
    for name, config in EXAMPLES.items():
        print(f"\n• {name}")
        print(f"  {config['description']}")
        print(f"  Duration: {config['duration']}")

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run Andamios ORM examples")
    parser.add_argument("target", nargs="?", help="Category or example name to run")
    parser.add_argument("--list", action="store_true", help="List available examples")
    
    args = parser.parse_args()
    
    if args.list:
        list_examples()
        return
    
    # Use uvloop for better performance if available
    try:
        import uvloop
        if hasattr(uvloop, 'install'):
            uvloop.install()
    except ImportError:
        pass  # Fall back to default event loop
    
    runner = ExampleRunner()
    
    print("🔧 Andamios ORM - Ultra-Simple EDD Examples Runner")
    print("=" * 60)
    print("4 examples: 1 comprehensive CRUD example per model")
    
    # Run examples based on arguments
    success = True
    
    if not args.target:
        # Run all examples
        success = await runner.run_all_examples()
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