#!/bin/bash

# Development environment setup script for Andamios ORM
# This script sets up everything needed for development and testing

set -e  # Exit on any error

echo "🚀 Andamios ORM Development Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}Project root: $PROJECT_ROOT${NC}"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  Not in a virtual environment${NC}"
    echo -e "${YELLOW}It's recommended to use a virtual environment${NC}"
    echo ""
    echo "To create one:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate  # On Linux/Mac"
    echo "  # or"
    echo "  venv\\Scripts\\activate     # On Windows"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✅ Virtual environment detected: $VIRTUAL_ENV${NC}"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo -e "${BLUE}Python version: $PYTHON_VERSION${NC}"

# Upgrade pip
echo -e "${YELLOW}📦 Upgrading pip...${NC}"
python3 -m pip install --upgrade pip

# Install Poetry if not available
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Poetry...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
else
    echo -e "${GREEN}✅ Poetry already installed${NC}"
fi

# Install dependencies with Poetry
echo -e "${YELLOW}📦 Installing dependencies with Poetry...${NC}"
poetry install --with dev,test

# Alternative: Install with pip if Poetry fails
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Poetry install failed, trying with pip...${NC}"
    
    # Install package in development mode
    pip install -e .
    
    # Install test dependencies
    pip install pytest pytest-asyncio pytest-cov pytest-xdist pytest-mock
    pip install coverage
    
    # Install development dependencies
    pip install black isort ruff mypy pre-commit
    
    # Install additional testing tools
    pip install factory-boy faker watchdog
fi

# Install pre-commit hooks
echo -e "${YELLOW}🪝 Installing pre-commit hooks...${NC}"
if command -v pre-commit &> /dev/null; then
    pre-commit install
else
    echo -e "${YELLOW}⚠️  pre-commit not available, skipping hooks setup${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p logs
mkdir -p htmlcov
mkdir -p .pytest_cache

# Run a quick test to verify everything works
echo -e "${YELLOW}🧪 Running verification tests...${NC}"

# Test imports
echo -e "${BLUE}Testing basic imports...${NC}"
python3 -c "
try:
    import pytest
    import coverage
    print('✅ Test dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Test project imports
echo -e "${BLUE}Testing project imports...${NC}"
python3 -c "
try:
    import sys
    sys.path.insert(0, 'src')
    from andamios_orm.exceptions import AndamiosORMException
    from andamios_orm.logging import get_logger
    print('✅ Project imports successful')
except ImportError as e:
    print(f'❌ Project import error: {e}')
    exit(1)
"

# Run a single test
echo -e "${BLUE}Running a sample test...${NC}"
if python3 -m pytest tests/unit/test_exceptions.py::TestAndamiosORMException::test_basic_exception -v --tb=short; then
    echo -e "${GREEN}✅ Sample test passed${NC}"
else
    echo -e "${YELLOW}⚠️  Sample test failed, but setup may still be OK${NC}"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating .env file...${NC}"
    cat > .env << EOF
# Development environment variables for Andamios ORM
DATABASE_URL=duckdb:///:memory:
LOG_LEVEL=DEBUG
TESTING=true
EOF
fi

# Display setup summary
echo ""
echo "=================================="
echo -e "${GREEN}🎉 Development setup completed!${NC}"
echo "=================================="
echo ""
echo "Available commands:"
echo "  make test           - Run all tests with coverage"
echo "  make test-unit      - Run only unit tests"
echo "  make test-watch     - Run tests continuously"
echo "  make lint           - Run code linting"
echo "  make format         - Format code"
echo "  make clean          - Clean temporary files"
echo ""
echo "Test files:"
echo "  pytest.ini          - Pytest configuration"
echo "  .coveragerc         - Coverage configuration"
echo "  tests/conftest.py   - Test fixtures and setup"
echo "  tests/unit/         - Unit test modules"
echo ""
echo "To run tests manually:"
echo "  python -m pytest tests/unit/ -v --cov=src/andamios_orm --cov-report=term-missing"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"