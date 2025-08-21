#!/usr/bin/env python3
"""
Continuous test runner for Andamios ORM development

This script watches for file changes and automatically runs relevant tests
when source files are modified. Useful for TDD workflows.
"""

import os
import sys
import time
import subprocess
import argparse
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class TestRunner:
    """Handles test execution with different strategies."""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.last_run_time = 0
        self.min_interval = 2  # Minimum seconds between test runs
    
    def run_tests(self, test_path: str = None, fast: bool = True):
        """Run tests with optional specific test path."""
        current_time = time.time()
        if current_time - self.last_run_time < self.min_interval:
            return
        
        self.last_run_time = current_time
        
        # Build pytest command
        cmd = ["python", "-m", "pytest"]
        
        if fast:
            cmd.extend(["-x", "--tb=short"])  # Fail fast, short traceback
        
        if self.verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        # Add coverage for full test runs
        if test_path is None:
            cmd.extend([
                "--cov=src/andamios_orm",
                "--cov-report=term-missing",
                "--cov-fail-under=100"
            ])
        
        # Add specific test path if provided
        if test_path:
            cmd.append(test_path)
        else:
            cmd.extend(["-m", "unit"])  # Only unit tests for watch mode
        
        print(f"\n🧪 Running tests: {' '.join(cmd)}")
        print("=" * 50)
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Tests passed!")
            else:
                print("❌ Tests failed!")
                
        except Exception as e:
            print(f"Error running tests: {e}")
    
    def run_specific_test(self, source_file: Path):
        """Run tests related to a specific source file."""
        # Try to find corresponding test file
        relative_path = source_file.relative_to(self.project_root / "src" / "andamios_orm")
        
        # Convert source path to test path
        test_patterns = [
            f"tests/unit/test_{relative_path.stem}.py",
            f"tests/unit/test_{relative_path.parent.name}.py",
            f"tests/unit/test_{relative_path.parent.name}_{relative_path.stem}.py"
        ]
        
        for pattern in test_patterns:
            test_file = self.project_root / pattern
            if test_file.exists():
                print(f"📍 Running specific tests for {source_file.name}")
                self.run_tests(str(test_file), fast=True)
                return
        
        # Fallback to all tests if no specific test found
        print(f"🔄 No specific test found for {source_file.name}, running all tests")
        self.run_tests(fast=True)


class SourceChangeHandler(FileSystemEventHandler):
    """Handles file system events for source code changes."""
    
    def __init__(self, test_runner: TestRunner):
        self.test_runner = test_runner
        self.ignored_patterns = {
            '.git', '__pycache__', '.pytest_cache', 'htmlcov',
            '.coverage', '.pyc', '.pyo', '.DS_Store'
        }
    
    def should_ignore(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        # Ignore hidden files and directories
        if any(part.startswith('.') for part in file_path.parts):
            return True
        
        # Ignore specific patterns
        if any(pattern in str(file_path) for pattern in self.ignored_patterns):
            return True
        
        # Only watch Python files
        if file_path.suffix not in {'.py'}:
            return True
        
        return False
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        if self.should_ignore(file_path):
            return
        
        print(f"\n📝 File changed: {file_path.name}")
        
        # Determine if it's a source file or test file
        if "tests/" in str(file_path):
            # Test file changed, run that specific test
            self.test_runner.run_tests(str(file_path), fast=True)
        elif "src/andamios_orm/" in str(file_path):
            # Source file changed, run related tests
            self.test_runner.run_specific_test(file_path)


def main():
    """Main entry point for the test watcher."""
    parser = argparse.ArgumentParser(
        description="Watch for file changes and run tests automatically"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose test output"
    )
    parser.add_argument(
        "--initial",
        action="store_true",
        help="Run tests immediately on startup"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tests (including integration) on changes"
    )
    
    args = parser.parse_args()
    
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    if not (project_root / "src" / "andamios_orm").exists():
        print("❌ Could not find andamios_orm source directory")
        sys.exit(1)
    
    print("🎯 Andamios ORM Test Watcher")
    print("=" * 30)
    print(f"📁 Project root: {project_root}")
    print(f"👁️  Watching: {project_root / 'src'} and {project_root / 'tests'}")
    print("⌨️  Press Ctrl+C to stop")
    print()
    
    # Create test runner
    test_runner = TestRunner(project_root, verbose=args.verbose)
    
    # Run initial tests if requested
    if args.initial:
        print("🚀 Running initial test suite...")
        test_runner.run_tests()
    
    # Set up file watcher
    event_handler = SourceChangeHandler(test_runner)
    observer = Observer()
    
    # Watch source directory
    observer.schedule(
        event_handler,
        str(project_root / "src"),
        recursive=True
    )
    
    # Watch tests directory
    observer.schedule(
        event_handler,
        str(project_root / "tests"),
        recursive=True
    )
    
    # Start watching
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping test watcher...")
        observer.stop()
    
    observer.join()
    print("✅ Test watcher stopped")


if __name__ == "__main__":
    main()