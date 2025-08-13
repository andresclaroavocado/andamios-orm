#!/bin/bash
set -e

# Andamios ORM Development Setup Script
# This script sets up the development environment for the Andamios ORM project

echo "🚀 Setting up Andamios ORM development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running in correct directory
if [[ ! -f "pyproject.toml" ]]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check Python version
print_info "Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [[ $(echo "$python_version >= $required_version" | bc -l) -eq 0 ]]; then
    print_error "Python $required_version or higher is required. Found: $python_version"
    exit 1
fi
print_success "Python version: $python_version"

# Check if Poetry is installed
print_info "Checking Poetry installation..."
if ! command -v poetry &> /dev/null; then
    print_warning "Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    
    if ! command -v poetry &> /dev/null; then
        print_error "Poetry installation failed. Please install manually: https://python-poetry.org/docs/#installation"
        exit 1
    fi
fi
print_success "Poetry found: $(poetry --version)"

# Check if Git is initialized
print_info "Checking Git repository..."
if [[ ! -d ".git" ]]; then
    print_warning "Git repository not initialized. Initializing..."
    git init
    git add .
    git commit -m "Initial commit"
fi
print_success "Git repository ready"

# Install dependencies
print_info "Installing project dependencies..."
poetry install --with dev,performance
print_success "Dependencies installed"

# Set up pre-commit hooks
print_info "Setting up pre-commit hooks..."
poetry run pre-commit install
poetry run pre-commit install --hook-type commit-msg
print_success "Pre-commit hooks installed"

# Create necessary directories
print_info "Creating project directories..."
mkdir -p {src/andamios_orm,tests/{unit,integration,e2e,examples},docs/{api,guides,examples,architecture},benchmarks,docker/test-db}
print_success "Project directories created"

# Set up environment variables
print_info "Setting up environment configuration..."
cat > .env.example << 'EOF'
# Andamios ORM Environment Configuration

# Development settings
ANDAMIOS_ORM_ENV=development
ANDAMIOS_ORM_LOG_LEVEL=DEBUG
ANDAMIOS_ORM_DATABASE_URL=duckdb:///dev.db

# Testing settings
ANDAMIOS_ORM_TEST_DATABASE_URL=duckdb:///:memory:
ANDAMIOS_ORM_TEST_PARALLEL=true

# Performance settings
ANDAMIOS_ORM_POOL_SIZE=10
ANDAMIOS_ORM_MAX_OVERFLOW=20
ANDAMIOS_ORM_POOL_TIMEOUT=30
EOF

if [[ ! -f ".env" ]]; then
    cp .env.example .env
    print_success "Environment configuration created"
else
    print_info "Environment configuration already exists"
fi

# Set up Docker environment
print_info "Setting up Docker environment..."
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    docker-compose build --pull
    print_success "Docker environment ready"
else
    print_warning "Docker not found. Docker setup skipped."
fi

# Run initial tests to verify setup
print_info "Running initial verification tests..."
if poetry run pytest --version &> /dev/null; then
    print_success "Test environment ready"
else
    print_error "Test environment setup failed"
    exit 1
fi

# Check code quality tools
print_info "Verifying code quality tools..."
poetry run mypy --version &> /dev/null && print_success "MyPy ready"
poetry run ruff --version &> /dev/null && print_success "Ruff ready"
poetry run pre-commit --version &> /dev/null && print_success "Pre-commit ready"

# Create initial placeholder files
print_info "Creating initial project structure..."

# Create main package init
cat > src/andamios_orm/__init__.py << 'EOF'
"""
Andamios ORM - A modern, async-first Python ORM library.

Built on DuckDB and SQLAlchemy 2.0+ for high-performance analytical workloads.
"""

__version__ = "0.1.0"
__author__ = "Andamios Team"
__email__ = "team@andamios.dev"

# Core imports will be added as components are implemented
# from .core import create_engine, sessionmaker
# from .models import Base
# from .repositories import BaseRepository

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    # Core exports will be added as components are implemented
]
EOF

# Create CLI placeholder
mkdir -p src/andamios_orm/cli
cat > src/andamios_orm/cli/__init__.py << 'EOF'
"""Command line interface for Andamios ORM."""

def main():
    """Main CLI entry point."""
    print("Andamios ORM CLI - Coming Soon!")
    print("Run 'poetry run pytest' to execute tests")
    print("Run examples with 'python examples/basic/01_connection.py'")

if __name__ == "__main__":
    main()
EOF

print_success "Initial project structure created"

# Final verification
print_info "Running final verification..."
if poetry run python -c "import andamios_orm; print(f'Andamios ORM v{andamios_orm.__version__} ready!')"; then
    print_success "Package import successful"
else
    print_error "Package import failed"
    exit 1
fi

# Summary
echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Run tests: poetry run pytest"
echo "2. Start development: poetry shell"
echo "3. Run examples: cd examples/basic && python 01_connection.py"
echo "4. Check code quality: poetry run pre-commit run --all-files"
echo "5. Start Docker environment: docker-compose up -d andamios-orm-dev"
echo ""
echo "Documentation:"
echo "- Project overview: README.md"
echo "- Architecture: ARCHITECTURE.md"
echo "- Development guide: CLAUDE.md"
echo "- GitHub issues: GITHUB_ISSUES.md"
echo ""
print_success "Happy coding! 🚀"