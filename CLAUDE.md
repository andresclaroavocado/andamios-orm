# Andamios ORM - Claude Context & Project Guide

## Project Overview

Andamios ORM is a modern, async-first Python ORM library designed to be part of the broader Andamios ecosystem. This project follows LRRS principles (Little, Responsible, Reusable, Separate) and emphasizes example-driven development followed by comprehensive test-driven development.

## Core Requirements

### Technical Stack
- **Python**: Latest versions (3.11+, optimized for 3.12)
- **Async Framework**: Built on `uvloop` for high-performance async operations
- **Database Layer**: SQLAlchemy 2.0+ as the foundation
- **Type Safety**: Full type hints with mypy strict mode
- **Dependencies**: Latest stable versions of all packages

### Development Philosophy
1. **Example-Driven Development (EDD)**: Start with clear, practical examples
2. **Test-Driven Development (TDD)**: Follow examples with comprehensive tests
3. **Real Database Testing**: Use actual database instances, avoid mocks
4. **100% Test Coverage**: Mandatory coverage with meaningful tests
5. **Parallel Testing**: Support for concurrent test execution

## Architecture Principles

### Async-First Design
- All operations must be async by default
- Use `uvloop` as the default event loop
- Proper connection pooling and resource management
- Graceful handling of concurrent database operations

### Repository Pattern
- Clean separation between models and data access
- Repository interfaces for testability
- Support for complex queries and aggregations
- Transaction management at repository level

### Type Safety
- Comprehensive type hints throughout
- Generic repository types
- Proper async type annotations
- mypy strict mode compliance

## Project Structure

```
andamios-orm/
├── src/andamios_orm/
│   ├── __init__.py              # Main exports
│   ├── core/                    # Core ORM functionality
│   │   ├── __init__.py
│   │   ├── engine.py           # Database engine management
│   │   ├── session.py          # Session management
│   │   └── connection.py       # Connection handling
│   ├── models/                  # Model definitions
│   │   ├── __init__.py
│   │   ├── base.py             # Base model class
│   │   └── mixins.py           # Common model mixins
│   ├── repositories/            # Repository pattern
│   │   ├── __init__.py
│   │   ├── base.py             # Base repository
│   │   ├── generic.py          # Generic repository
│   │   └── specialized.py      # Specialized repositories
│   ├── queries/                 # Query builders
│   │   ├── __init__.py
│   │   ├── builder.py          # Query builder
│   │   └── filters.py          # Filter definitions
│   ├── migration/               # Migration utilities
│   │   ├── __init__.py
│   │   └── manager.py          # Migration management
│   ├── testing/                 # Testing utilities
│   │   ├── __init__.py
│   │   ├── fixtures.py         # Test fixtures
│   │   └── database.py         # Test database management
│   └── scripts/                 # CLI tools
│       ├── __init__.py
│       └── cli.py              # Command line interface
├── examples/                    # Example-driven development
│   ├── basic/                   # Basic usage examples
│   ├── advanced/               # Advanced patterns
│   └── integration/            # Integration examples
├── tests/                       # Comprehensive test suite
│   ├── unit/                   # Unit tests (isolated)
│   ├── integration/            # Integration tests (with DB)
│   └── e2e/                    # End-to-end tests
├── docs/                       # Documentation
│   ├── api/                    # API documentation
│   ├── guides/                 # Usage guides
│   └── examples/               # Example documentation
├── benchmarks/                 # Performance benchmarks
└── docker/                     # Docker configurations for testing
    ├── postgres/               # PostgreSQL test setup
    ├── mysql/                  # MySQL test setup
    └── mongodb/                # MongoDB test setup
```

## Development Workflow

### 1. Example-Driven Development
- Start with practical examples in `/examples/`
- Create clear, self-contained use cases
- Document expected behavior and usage patterns
- Examples should be executable and demonstrate real-world scenarios

### 2. Test-Driven Development
- Write tests immediately after examples
- Use real database instances for integration tests
- Achieve 100% code coverage
- Support parallel test execution
- No mocking of database operations

### 3. Implementation
- Implement functionality to pass tests
- Follow async-first patterns
- Maintain type safety throughout
- Optimize for performance with uvloop

## Testing Strategy

### Test Database Management
- Docker containers for consistent test databases
- Separate database per test worker for parallel execution
- Automatic setup/teardown of test schemas
- Support for PostgreSQL, MySQL, SQLite, and MongoDB

### Test Categories
1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test database operations with real databases
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Benchmark critical operations

### Parallel Testing Configuration
- pytest-xdist for parallel execution
- Database isolation per worker
- Proper resource cleanup
- No shared state between tests

## Dependencies (Latest Versions)

### Core Dependencies
- `sqlalchemy>=2.0.23` - Core ORM functionality
- `duckdb>=0.9.0` - DuckDB async driver (primary database)
- `uvloop>=0.19.0` - High-performance event loop
- `pydantic>=2.5.0` - Data validation
- `alembic>=1.13.0` - Database migrations

### Testing Dependencies
- `pytest>=7.4.3` - Test framework
- `pytest-asyncio>=0.21.1` - Async test support
- `pytest-xdist>=3.5.0` - Parallel test execution
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-docker>=2.0.0` - Docker container management
- `factory-boy>=3.3.0` - Test data factories

### Development Dependencies
- `mypy>=1.7.0` - Type checking
- `black>=23.11.0` - Code formatting
- `isort>=5.12.0` - Import sorting
- `ruff>=0.1.6` - Fast linting
- `pre-commit>=3.6.0` - Pre-commit hooks

## Performance Requirements

### Response Times
- Simple queries: < 1ms
- Complex queries: < 10ms
- Bulk operations: < 100ms for 1000 records
- Connection acquisition: < 5ms

### Scalability
- Support for connection pooling
- Efficient memory usage
- Proper resource cleanup
- Graceful handling of high concurrency

## Integration Points

### Andamios Ecosystem
- `andamios-llm`: Database operations for LLM data
- `andamios-api`: FastAPI integration
- `andamios-core`: Shared utilities and patterns

### External Integrations
- FastAPI dependency injection
- Pydantic model integration
- Alembic migration support
- Docker development environment

## Quality Gates

### Code Quality
- 100% type coverage (mypy strict mode)
- 100% test coverage
- All linting checks pass (ruff, black, isort)
- No security vulnerabilities (bandit)

### Performance
- All benchmarks within acceptable ranges
- Memory usage within limits
- No performance regressions

### Documentation
- All public APIs documented
- Examples for all major features
- Architecture documentation up-to-date
- Migration guides for breaking changes

## CLI Commands

```bash
# Development
poetry run andamios-orm dev-setup      # Setup development environment
poetry run andamios-orm db-start       # Start test databases
poetry run andamios-orm db-stop        # Stop test databases

# Testing
poetry run andamios-orm test           # Run all tests
poetry run andamios-orm test-parallel  # Run tests in parallel
poetry run andamios-orm benchmark      # Run performance benchmarks

# Database
poetry run andamios-orm migrate         # Run migrations
poetry run andamios-orm db-reset        # Reset database
poetry run andamios-orm db-seed         # Seed test data
```

## Contributing Guidelines

1. **Start with Examples**: Always begin with clear usage examples
2. **Write Tests First**: Follow TDD principles strictly
3. **Type Everything**: Full type annotations required
4. **Real Databases**: Use actual databases for integration tests
5. **Performance Matters**: Consider performance implications
6. **Documentation**: Update docs with all changes

## Success Metrics

- 100% test coverage maintained
- All tests pass in parallel execution
- Performance benchmarks within targets
- Zero critical security vulnerabilities
- Complete type safety (mypy strict)
- Successful integration with Andamios ecosystem