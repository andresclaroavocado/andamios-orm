# Andamios ORM - Claude Context & Development Guide

## Project Overview

Andamios ORM is a modern, async-first Python ORM library built on DuckDB and SQLAlchemy 2.0+. This project emphasizes Example-Driven Development (EDD) followed by Test-Driven Development (TDD), with real database testing and 100% coverage requirements.

## Core Development Philosophy

### 1. Example-Driven Development (EDD) → Test-Driven Development (TDD)
- **Phase 1 - Examples First**: Create practical, executable examples in `/examples/`
- **Phase 2 - Tests Second**: Write comprehensive tests based on examples  
- **Phase 3 - Implementation**: Implement functionality to satisfy tests
- **Phase 4 - Optimization**: Refactor and optimize with maintained test coverage

### 2. Real Database Testing
- Use actual DuckDB instances for all database operations
- **NO MOCKING** of database operations
- Parallel test execution with isolated database instances
- Docker containers for consistent test environments

### 3. 100% Test Coverage
- Mandatory 100% code coverage
- Tests must be meaningful, not just coverage-driven
- Integration tests with real databases
- Performance benchmarks as part of test suite

## Technical Requirements

### Technology Stack
- **Python**: 3.13+ (latest stable Python version)
- **Database**: DuckDB 1.1.0+ (primary columnar database), SQLAlchemy 2.0.35+ (modern async ORM foundation)
- **Async**: uvloop 0.20.0+ (high-performance async event loop)
- **Validation**: Pydantic 2.10.0+ (data validation and serialization)
- **Migration**: Alembic 1.13.0+ (database schema migration management)

### Development Dependencies
- **Testing**: pytest 8.3.0+ (modern testing framework), pytest-asyncio 0.24.0+ (async test support), pytest-xdist 3.6.0+ (parallel execution)
- **Coverage**: pytest-cov 6.0.0+ (coverage reporting)
- **Quality**: mypy 1.13.0+ (static type checking), ruff 0.8.0+ (fast linting), black 24.10.0+ (code formatting), pre-commit 4.0.0+ (git hooks)
- **Factories**: factory-boy 3.3.0+ (test data generation)

### Performance Requirements
- Simple queries: < 1ms
- Complex queries: < 10ms  
- Bulk operations: < 100ms for 10,000 records
- Connection acquisition: < 5ms
- Memory usage: < 100MB base footprint

## Project Structure

```
andamios-orm/
├── src/andamios_orm/               # Main package
│   ├── __init__.py                 # Public API exports
│   ├── core/                       # Core ORM functionality
│   │   ├── __init__.py
│   │   ├── engine.py              # DuckDB engine management
│   │   ├── session.py             # Async session management
│   │   └── connection.py          # Connection handling & pooling
│   ├── models/                     # Model definitions
│   │   ├── __init__.py
│   │   ├── base.py                # Base model class
│   │   └── mixins.py              # Common model mixins
│   ├── repositories/               # Repository pattern
│   │   ├── __init__.py
│   │   ├── base.py                # Base repository
│   │   ├── generic.py             # Generic typed repository
│   │   └── specialized.py         # Domain-specific repositories
│   ├── queries/                    # Query builders
│   │   ├── __init__.py
│   │   ├── builder.py             # Fluent query builder
│   │   └── filters.py             # Reusable filters
│   ├── migration/                  # Migration system
│   │   ├── __init__.py
│   │   └── manager.py             # Migration management
│   ├── testing/                    # Testing utilities
│   │   ├── __init__.py
│   │   ├── fixtures.py            # Test fixtures
│   │   ├── database.py            # Test database management
│   │   └── factories.py           # Test data factories
│   └── cli/                        # Command line interface
│       ├── __init__.py
│       └── commands.py            # CLI commands
├── examples/                       # Example-Driven Development
│   ├── basic/                      # Basic usage patterns
│   │   ├── 01_connection.py       # Database connection
│   │   ├── 02_models.py           # Model definition
│   │   ├── 03_crud.py             # Basic CRUD operations
│   │   ├── 04_queries.py          # Query examples
│   │   └── 05_transactions.py     # Transaction management
│   ├── intermediate/               # Intermediate patterns
│   │   ├── 01_repositories.py     # Repository patterns
│   │   ├── 02_complex_queries.py  # Advanced querying
│   │   ├── 03_relationships.py    # Model relationships
│   │   ├── 04_migrations.py       # Migration examples
│   │   └── 05_testing.py          # Testing patterns
│   └── advanced/                   # Advanced patterns
│       ├── 01_performance.py      # Performance optimization
│       ├── 02_custom_types.py     # Custom field types
│       ├── 03_events.py           # Event handling
│       ├── 04_middleware.py       # Middleware patterns
│       └── 05_extensions.py       # Custom extensions
├── tests/                          # Comprehensive test suite
│   ├── conftest.py                # Test configuration
│   ├── unit/                      # Unit tests (isolated)
│   │   ├── test_models.py
│   │   ├── test_repositories.py
│   │   ├── test_queries.py
│   │   └── test_core.py
│   ├── integration/               # Integration tests (with DB)
│   │   ├── test_crud_operations.py
│   │   ├── test_transactions.py
│   │   ├── test_migrations.py
│   │   └── test_performance.py
│   └── e2e/                       # End-to-end tests
│       ├── test_workflows.py
│       └── test_real_scenarios.py
├── docs/                          # Documentation
│   ├── api/                       # API documentation
│   ├── guides/                    # Usage guides
│   ├── examples/                  # Example documentation
│   └── architecture/             # Architecture docs
├── benchmarks/                    # Performance benchmarks
│   ├── query_performance.py
│   ├── connection_benchmarks.py
│   └── bulk_operations.py
├── docker/                        # Docker configurations
│   ├── test-db/                   # Test database containers
│   └── development/               # Development environment
├── scripts/                       # Utility scripts
│   ├── setup_dev.py              # Development setup
│   ├── run_tests.py              # Test runner
│   └── benchmark.py              # Benchmark runner
├── pyproject.toml                 # Project configuration
├── poetry.lock                    # Dependency lock file
├── README.md                      # Project readme
├── ARCHITECTURE.md                # Architecture documentation
├── CONTRIBUTING.md                # Contribution guidelines
└── .github/                       # GitHub configuration
    ├── workflows/                 # CI/CD workflows
    └── ISSUE_TEMPLATE/           # Issue templates
```

## Development Workflow

### 1. Example-Driven Development Phase
- Create practical examples in `/examples/`
- Examples must be executable and demonstrate real-world usage
- Document expected behavior and edge cases
- Examples should cover the full API surface

### 2. Test-Driven Development Phase
- Write tests immediately after examples
- Tests should be based on example behavior
- Use real DuckDB instances for all database tests
- Achieve 100% code coverage with meaningful tests

### 3. Implementation Phase
- Implement functionality to satisfy tests
- Follow async-first patterns throughout
- Maintain type safety with full type hints
- Optimize for DuckDB's columnar architecture

### 4. Quality Assurance Phase
- Run full test suite with parallel execution
- Verify 100% test coverage
- Performance benchmarks within targets
- Code quality checks (mypy, ruff, pre-commit)

## Testing Strategy

### Test Database Management
- Docker containers for consistent DuckDB environments
- Separate database instance per test worker
- Automatic setup/teardown of test schemas
- No shared state between tests

### Test Categories
1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test database operations with real DuckDB
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Benchmark critical operations

### Parallel Testing Requirements
- pytest-xdist for parallel execution
- Database isolation per worker process
- Proper resource cleanup between tests
- No race conditions or shared state

## Code Quality Standards

### Type Safety
- Full type hints throughout codebase
- mypy strict mode compliance
- Generic types for repository patterns
- Proper async type annotations

### Code Style
- ruff for linting and formatting
- Black-compatible formatting
- isort for import organization
- Pre-commit hooks for quality gates

### Documentation
- Docstrings for all public APIs
- Type annotations serve as inline documentation
- Examples for all major features
- Architecture decision records

## Performance Guidelines

### DuckDB Optimization
- Leverage columnar storage advantages
- Batch operations when possible
- Use appropriate indexing strategies
- Monitor query performance

### Async Best Practices
- Use uvloop for maximum performance
- Proper connection pooling
- Avoid blocking operations in async context
- Resource cleanup and connection management

### Memory Management
- Efficient use of memory for large datasets
- Proper cleanup of database connections
- Monitor memory usage in tests
- Optimize for DuckDB's memory model

## CLI Commands

```bash
# Development setup
poetry run andamios-orm setup-dev     # Setup development environment
poetry run andamios-orm db-start      # Start test databases

# Testing
poetry run andamios-orm test          # Run all tests
poetry run andamios-orm test-parallel # Run tests in parallel
poetry run andamios-orm coverage      # Generate coverage report

# Quality
poetry run andamios-orm lint          # Run linting
poetry run andamios-orm typecheck     # Run type checking
poetry run andamios-orm format        # Format code

# Database
poetry run andamios-orm migrate       # Run migrations
poetry run andamios-orm db-reset      # Reset test database

# Benchmarks
poetry run andamios-orm benchmark     # Run performance benchmarks
```

## GitHub Issues Workflow

### Issue Types
1. **Examples**: Create new usage examples
2. **Tests**: Write tests for specific functionality
3. **Implementation**: Implement core functionality
4. **Performance**: Optimize performance bottlenecks
5. **Documentation**: Update documentation

### Development Process
1. Start with example issues
2. Follow with corresponding test issues  
3. Implement functionality to pass tests
4. Optimize and document

## Success Criteria

### Functional Requirements
- 100% test coverage maintained
- All tests pass in parallel execution
- Performance benchmarks within targets
- Full type safety (mypy strict mode)

### Quality Requirements
- Zero critical security vulnerabilities
- No performance regressions
- Comprehensive documentation
- Clear examples for all features

### Integration Requirements
- Seamless DuckDB integration
- Async-first API design
- Compatible with modern Python ecosystem
- Easy testing and development workflow

## Important Development Notes

### Example-First Approach
- **ALWAYS** create examples before writing any code
- Examples should be practical and executable
- Document expected behavior clearly
- Use examples to drive API design

### Real Database Testing
- **NEVER** mock database operations
- Use actual DuckDB instances for all database tests
- Test with realistic data volumes
- Verify performance under load

### Type Safety
- Full type hints are mandatory
- Use generic types for reusable components
- Maintain mypy strict mode compliance
- Type safety helps with API design

### Async Patterns
- All database operations must be async
- Use uvloop for optimal performance
- Proper resource management and cleanup
- Handle concurrent operations gracefully

This project follows a strict Example → Test → Implementation → Optimization cycle. Always start with examples, ensure they're well-documented and executable, then write comprehensive tests, and finally implement the functionality.