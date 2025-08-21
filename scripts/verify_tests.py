#!/usr/bin/env python3
"""
Test verification script for Andamios ORM

This script verifies that all tests run correctly and achieve 100% coverage.
"""

import subprocess
import sys
import json
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def verify_test_structure():
    """Verify test directory structure."""
    print("🔍 Verifying test structure...")
    
    project_root = Path(__file__).parent.parent
    required_files = [
        "tests/conftest.py",
        "tests/unit/test_engine.py",
        "tests/unit/test_session.py", 
        "tests/unit/test_database.py",
        "tests/unit/test_models.py",
        "tests/unit/test_exceptions.py",
        "tests/unit/test_logging.py",
        "pytest.ini",
        ".coveragerc"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing test files: {missing_files}")
        return False
    
    print("✅ Test structure verified")
    return True


def verify_test_discovery():
    """Verify that pytest can discover all tests."""
    print("🔍 Verifying test discovery...")
    
    success, stdout, stderr = run_command(
        "python -m pytest --collect-only -q"
    )
    
    if not success:
        print(f"❌ Test discovery failed: {stderr}")
        return False
    
    # Count discovered tests
    lines = stdout.strip().split('\n')
    test_count = 0
    for line in lines:
        if 'test session starts' in line or 'collected' in line:
            continue
        if line.strip() and not line.startswith('='):
            test_count += 1
    
    print(f"✅ Discovered {test_count} tests")
    return test_count > 0


def run_unit_tests():
    """Run unit tests and verify 100% coverage."""
    print("🧪 Running unit tests with coverage...")
    
    success, stdout, stderr = run_command(
        "python -m pytest tests/unit/ --cov=src/andamios_orm --cov-report=json --cov-report=term --cov-fail-under=100 -v"
    )
    
    if not success:
        print(f"❌ Unit tests failed:")
        print(stderr)
        return False
    
    # Check coverage report
    coverage_file = Path("coverage.json")
    if coverage_file.exists():
        try:
            with open(coverage_file) as f:
                coverage_data = json.load(f)
            
            total_coverage = coverage_data['totals']['percent_covered']
            print(f"✅ Unit tests passed with {total_coverage:.1f}% coverage")
            
            if total_coverage < 100:
                print(f"❌ Coverage below 100%: {total_coverage:.1f}%")
                return False
            
            return True
        except Exception as e:
            print(f"⚠️  Could not parse coverage report: {e}")
            return success
    
    print("✅ Unit tests passed")
    return True


def verify_imports():
    """Verify that the package can be imported correctly."""
    print("🔍 Verifying package imports...")
    
    import_tests = [
        "import src.andamios_orm",
        "from src.andamios_orm import Model, get_logger, create_engine",
        "from src.andamios_orm.core import engine, session, database",
        "from src.andamios_orm.models import Project, Conversation, Document, Repository",
        "from src.andamios_orm.exceptions import AndamiosORMException, ValidationError",
        "from src.andamios_orm.logging import setup_logging, LoggingConfig"
    ]
    
    for import_test in import_tests:
        success, stdout, stderr = run_command(f"python -c \"{import_test}\"")
        if not success:
            print(f"❌ Import failed: {import_test}")
            print(f"Error: {stderr}")
            return False
    
    print("✅ All imports successful")
    return True


def verify_coverage_config():
    """Verify coverage configuration."""
    print("🔍 Verifying coverage configuration...")
    
    success, stdout, stderr = run_command("coverage --help")
    if not success:
        print("❌ Coverage tool not available")
        return False
    
    # Check if .coveragerc exists and has required settings
    coveragerc = Path(".coveragerc")
    if not coveragerc.exists():
        print("❌ .coveragerc file not found")
        return False
    
    content = coveragerc.read_text()
    required_settings = ["source = src/andamios_orm", "fail_under = 100", "branch = True"]
    
    for setting in required_settings:
        if setting not in content:
            print(f"❌ Missing coverage setting: {setting}")
            return False
    
    print("✅ Coverage configuration verified")
    return True


def main():
    """Main verification function."""
    print("🎯 Andamios ORM Test Verification")
    print("=" * 40)
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    original_cwd = Path.cwd()
    
    try:
        import os
        os.chdir(project_root)
        
        # Run all verification steps
        steps = [
            ("Test Structure", verify_test_structure),
            ("Coverage Config", verify_coverage_config),
            ("Package Imports", verify_imports),
            ("Test Discovery", verify_test_discovery),
            ("Unit Tests & Coverage", run_unit_tests),
        ]
        
        results = []
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}")
            print("-" * 20)
            
            try:
                success = step_func()
                results.append((step_name, success))
                
                if success:
                    print(f"✅ {step_name} - PASSED")
                else:
                    print(f"❌ {step_name} - FAILED")
                    
            except Exception as e:
                print(f"💥 {step_name} - ERROR: {e}")
                results.append((step_name, False))
        
        # Summary
        print("\n" + "=" * 40)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 40)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for step_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{step_name:.<30} {status}")
        
        print("-" * 40)
        print(f"Total: {passed}/{total} steps passed")
        
        if passed == total:
            print("\n🎉 ALL VERIFICATIONS PASSED!")
            print("The test suite is working correctly with 100% coverage.")
            return 0
        else:
            print(f"\n💥 {total - passed} VERIFICATION(S) FAILED!")
            print("Please fix the issues before proceeding.")
            return 1
            
    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    sys.exit(main())