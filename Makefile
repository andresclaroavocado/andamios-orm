# Makefile for Andamios ORM
# Provides convenient commands for development, testing, and maintenance

.PHONY: help install install-dev test test-unit test-integration test-watch test-coverage clean lint format type-check docs build publish

# Default target
help:
	@echo "Andamios ORM Development Commands"
	@echo "================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  install      Install package dependencies"
	@echo "  install-dev  Install package with development dependencies"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test         Run all tests with coverage (requires 100%)"
	@echo "  test-unit    Run only unit tests"
	@echo "  test-integration  Run integration tests"
	@echo "  test-watch   Run tests continuously on file changes"
	@echo "  test-coverage     Generate and open coverage report"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  lint         Run all linting checks"
	@echo "  format       Format code with black and isort"
	@echo "  type-check   Run mypy type checking"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  clean        Clean temporary files and caches"
	@echo "  docs         Generate documentation"
	@echo "  build        Build package distributions"
	@echo "  publish      Publish package to PyPI"

# Installation commands
install:
	@echo "📦 Installing Andamios ORM..."
	pip install -e .

install-dev:
	@echo "🛠️  Installing development dependencies..."
	pip install -e ".[dev]"
	pre-commit install

# Testing commands
test:
	@echo "🧪 Running full test suite with 100% coverage requirement..."
	./scripts/run_tests.sh

test-unit:
	@echo "🧪 Running unit tests only..."
	pytest tests/unit/ -v --cov=src/andamios_orm --cov-report=term-missing --cov-fail-under=100

test-integration:
	@echo "🧪 Running integration tests..."
	pytest tests/integration/ -v --cov=src/andamios_orm --cov-report=term-missing

test-watch:
	@echo "👁️  Starting test watcher..."
	python scripts/test_watch.py --initial

test-coverage:
	@echo "📊 Generating coverage report..."
	pytest --cov=src/andamios_orm --cov-report=html --cov-report=term-missing
	@echo "Opening coverage report..."
	@if command -v open >/dev/null 2>&1; then \
		open htmlcov/index.html; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open htmlcov/index.html; \
	else \
		echo "Coverage report generated at htmlcov/index.html"; \
	fi

# Code quality commands
lint:
	@echo "🔍 Running linting checks..."
	@echo "Running ruff..."
	ruff check src/ tests/
	@echo "Running black check..."
	black --check src/ tests/
	@echo "Running isort check..."
	isort --check-only src/ tests/
	@echo "Running mypy..."
	mypy src/

format:
	@echo "🎨 Formatting code..."
	black src/ tests/
	isort src/ tests/
	ruff check --fix src/ tests/

type-check:
	@echo "🔍 Running type checking..."
	mypy src/ --strict

# Maintenance commands
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf coverage.json
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

docs:
	@echo "📚 Generating documentation..."
	@if [ -d "docs/" ]; then \
		cd docs && make html; \
	else \
		echo "Documentation directory not found"; \
	fi

build: clean
	@echo "🏗️  Building package..."
	python -m build

publish: build
	@echo "🚀 Publishing to PyPI..."
	python -m twine upload dist/*

# Development workflow commands
dev-setup: install-dev
	@echo "🔧 Setting up development environment..."
	@echo "✅ Development environment ready!"

dev-test: format lint test
	@echo "🔄 Running full development workflow..."
	@echo "✅ All checks passed!"

ci-test:
	@echo "🤖 Running CI test suite..."
	pytest --cov=src/andamios_orm --cov-report=xml --cov-report=term --cov-fail-under=100 --junitxml=junit.xml

# Performance testing
test-performance:
	@echo "⚡ Running performance tests..."
	pytest tests/ -m performance -v

# Security testing
test-security:
	@echo "🔒 Running security checks..."
	bandit -r src/

# Database commands
db-test-setup:
	@echo "🗄️  Setting up test databases..."
	docker-compose -f docker/docker-compose.test.yml up -d

db-test-teardown:
	@echo "🗄️  Tearing down test databases..."
	docker-compose -f docker/docker-compose.test.yml down -v

# Git hooks and pre-commit
pre-commit-install:
	@echo "🪝 Installing pre-commit hooks..."
	pre-commit install

pre-commit-run:
	@echo "🪝 Running pre-commit hooks on all files..."
	pre-commit run --all-files

# Version management
version-bump-patch:
	@echo "📈 Bumping patch version..."
	bump2version patch

version-bump-minor:
	@echo "📈 Bumping minor version..."
	bump2version minor

version-bump-major:
	@echo "📈 Bumping major version..."
	bump2version major

# Release workflow
release-patch: version-bump-patch build publish
	@echo "🎉 Patch release completed!"

release-minor: version-bump-minor build publish
	@echo "🎉 Minor release completed!"

release-major: version-bump-major build publish
	@echo "🎉 Major release completed!"