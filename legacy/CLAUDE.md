# Project Architect DB - Claude Context & Project Guide

## Project Overview

Project Architect DB is a modern, async-first Python database library for project management and architecture systems. Built specifically for the Web-Based Project Architect platform, it provides high-performance database operations for projects, conversations, documents, and repositories management.

## Core Requirements

### Technical Stack
- **Python**: 3.11+ (optimized for 3.12)
- **Database**: DuckDB (primary) with SQLAlchemy 2.0+ async support
- **Async Framework**: Built on `uvloop` for maximum performance
- **Type Safety**: Full type hints with mypy strict mode
- **Data Validation**: Pydantic v2 for robust data models
- **Dependencies**: Latest stable versions of all packages

### Development Philosophy
1. **Example-Driven Development (EDD)**: Start with clear, practical examples
2. **Test-Driven Development (TDD)**: Follow examples with comprehensive tests
3. **Real Database Testing**: Use actual DuckDB instances, avoid mocks completely
4. **100% Test Coverage**: Mandatory coverage with meaningful tests
5. **Parallel Testing**: Support for concurrent test execution with isolated databases

## Architecture Principles

### Async-First Design
- All database operations async by default
- Use `uvloop` as the event loop for optimal performance
- Proper connection pooling and resource management
- Graceful handling of concurrent database operations
- Async context managers for transactions

### Repository Pattern with DuckDB Optimization
- Clean separation between models and data access
- Repository interfaces optimized for DuckDB's analytical capabilities
- Support for complex aggregations and analytical queries
- Batch operations for high-performance bulk inserts
- Transaction management at repository level

### Type Safety & Data Validation
- Comprehensive type hints throughout codebase
- Pydantic models for data validation and serialization
- Generic repository types with proper async annotations
- mypy strict mode compliance
- Runtime type checking where appropriate

## Project Structure

```
project-architect-db/
├── src/project_architect_db/
│   ├── __init__.py              # Main exports and version
│   ├── core/                    # Core database functionality
│   │   ├── __init__.py
│   │   ├── engine.py           # DuckDB async engine management
│   │   ├── session.py          # Async session management
│   │   ├── connection.py       # Connection pooling and management
│   │   └── transaction.py      # Transaction context managers
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py             # Base model with common fields
│   │   ├── project.py          # Project model
│   │   ├── conversation.py     # Conversation model
│   │   ├── document.py         # Document model
│   │   ├── repository.py       # Repository model
│   │   └── mixins.py           # Common model mixins (timestamps, etc.)
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── project.py          # Project Pydantic models
│   │   ├── conversation.py     # Conversation Pydantic models
│   │   ├── document.py         # Document Pydantic models
│   │   ├── repository.py       # Repository Pydantic models
│   │   └── common.py           # Common schema types
│   ├── repositories/            # Repository pattern implementation
│   │   ├── __init__.py
│   │   ├── base.py             # Base async repository
│   │   ├── project.py          # Project repository
│   │   ├── conversation.py     # Conversation repository
│   │   ├── document.py         # Document repository
│   │   ├── repository.py       # Repository model repository
│   │   └── analytics.py        # Cross-model analytics queries
│   ├── queries/                 # Query builders and filters
│   │   ├── __init__.py
│   │   ├── builder.py          # Async query builder
│   │   ├── filters.py          # Common filter implementations
│   │   └── aggregations.py     # Analytics and aggregation queries
│   ├── migration/               # Database migration utilities
│   │   ├── __init__.py
│   │   ├── manager.py          # Migration management
│   │   └── versions/           # Migration version files
│   ├── testing/                 # Testing utilities
│   │   ├── __init__.py
│   │   ├── fixtures.py         # Async test fixtures
│   │   ├── database.py         # Test database management
│   │   ├── factories.py        # Data factories for testing
│   │   └── parallel.py         # Parallel test database isolation
│   ├── exceptions/              # Custom exceptions
│   │   ├── __init__.py
│   │   ├── database.py         # Database-related exceptions
│   │   └── validation.py       # Validation exceptions
│   └── cli/                     # Command line interface
│       ├── __init__.py
│       ├── main.py             # Main CLI entry point
│       ├── database.py         # Database management commands
│       └── migration.py        # Migration commands
├── examples/                    # Example-driven development
│   ├── basic/                   # Basic CRUD operations
│   │   ├── __init__.py
│   │   ├── project_crud.py     # Project CRUD examples
│   │   ├── conversation_flow.py # Conversation management
│   │   └── document_handling.py # Document operations
│   ├── advanced/                # Advanced patterns
│   │   ├── __init__.py
│   │   ├── analytics.py        # Complex analytics queries
│   │   ├── bulk_operations.py  # Batch processing examples
│   │   └── concurrent_access.py # Concurrent operation patterns
│   ├── integration/             # Integration examples
│   │   ├── __init__.py
│   │   ├── fastapi_integration.py # FastAPI integration
│   │   ├── websocket_updates.py   # Real-time updates
│   │   └── background_tasks.py    # Background processing
│   └── performance/             # Performance examples
│       ├── __init__.py
│       ├── bulk_insert.py      # High-performance bulk operations
│       └── query_optimization.py # Query optimization examples
├── tests/                       # Comprehensive test suite
│   ├── conftest.py             # Pytest configuration and fixtures
│   ├── unit/                   # Unit tests (isolated components)
│   │   ├── test_models.py      # Model validation tests
│   │   ├── test_schemas.py     # Pydantic schema tests
│   │   └── test_exceptions.py  # Exception handling tests
│   ├── integration/            # Integration tests (with DuckDB)
│   │   ├── test_repositories.py # Repository functionality
│   │   ├── test_transactions.py # Transaction management
│   │   └── test_migrations.py  # Migration testing
│   ├── performance/            # Performance and load tests
│   │   ├── test_bulk_operations.py # Bulk operation performance
│   │   └── test_concurrent_access.py # Concurrency testing
│   └── e2e/                    # End-to-end workflow tests
│       ├── test_project_lifecycle.py # Complete project workflows
│       └── test_conversation_flows.py # Conversation management flows
├── benchmarks/                 # Performance benchmarking
│   ├── __init__.py
│   ├── crud_operations.py      # CRUD performance benchmarks
│   ├── bulk_operations.py      # Bulk operation benchmarks
│   └── analytics_queries.py    # Analytics query performance
├── docs/                       # Documentation
│   ├── architecture.md         # Architecture documentation
│   ├── getting_started.md      # Getting started guide
│   ├── api_reference.md        # API documentation
│   ├── performance.md          # Performance guidelines
│   └── examples/               # Example documentation
├── docker/                     # Docker configurations
│   ├── duckdb/                 # DuckDB test configurations
│   └── testing/                # Testing environment setup
├── .github/                    # GitHub configuration
│   ├── workflows/              # CI/CD workflows
│   └── ISSUE_TEMPLATE/         # Issue templates
├── pyproject.toml              # Project configuration
├── poetry.lock                 # Dependency lock file
├── pytest.ini                 # Pytest configuration
├── mypy.ini                    # MyPy configuration
└── README.md                   # Project README
```

## Database Models Architecture

### Core Models

1. **Project**: Central entity for project management
   - Enhanced with async validation
   - JSON fields for flexible architecture storage
   - Full-text search capabilities with DuckDB

2. **Conversation**: Communication and workflow tracking
   - JSON message storage with efficient querying
   - Phase-based workflow management
   - Real-time capabilities support

3. **Document**: Document and specification management
   - File path management with async I/O
   - Content indexing and search
   - Version control support

4. **Repository**: Code repository tracking
   - GitHub integration support
   - Build and deployment status tracking
   - Analytics on repository metrics

### Enhanced Features for DuckDB

- **Analytical Queries**: Leverage DuckDB's analytical capabilities
- **JSON Processing**: Efficient JSON operations for architecture and messages
- **Bulk Operations**: Optimized batch inserts and updates
- **Aggregations**: Real-time analytics and reporting
- **Full-Text Search**: Document content search capabilities

## Development Workflow

### 1. Example-Driven Development
- Start with practical examples in `/examples/`
- Create self-contained, executable use cases
- Document expected behavior and performance characteristics
- Examples must demonstrate real-world async patterns

### 2. Test-Driven Development
- Write comprehensive tests immediately after examples
- Use real DuckDB instances for all integration tests
- Achieve 100% code coverage with meaningful tests
- Support parallel test execution with database isolation
- No mocking of database operations

### 3. Implementation Phases
- **Phase 1**: Core models and basic CRUD operations
- **Phase 2**: Repository pattern with async support
- **Phase 3**: Advanced querying and analytics
- **Phase 4**: Performance optimization and bulk operations
- **Phase 5**: Integration patterns and real-time features

## Testing Strategy

### DuckDB Test Database Management
- Isolated DuckDB files per test worker
- Automatic setup/teardown of test schemas
- Parallel execution with no shared state
- Memory-based databases for speed
- Persistent databases for integration tests

### Test Categories
1. **Unit Tests**: Individual component validation
2. **Integration Tests**: Full database operations with real DuckDB
3. **Performance Tests**: Benchmark critical operations
4. **Concurrency Tests**: Parallel access patterns
5. **End-to-End Tests**: Complete workflow validation

### Parallel Testing Configuration
- `pytest-xdist` for parallel execution
- Unique DuckDB file per worker process
- Proper async resource cleanup
- No shared state between test processes
- Test data factories for consistent test data

## Dependencies (Latest Versions)

### Core Dependencies
```toml
python = "^3.11"
sqlalchemy = "^2.0.23"
duckdb = "^0.9.2"
duckdb-engine = "^0.9.4"
uvloop = "^0.19.0"
pydantic = "^2.5.0"
alembic = "^1.13.0"
asyncio = "^3.11.0"
```

### Testing Dependencies
```toml
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-xdist = "^3.5.0"
pytest-cov = "^4.1.0"
pytest-benchmark = "^4.0.0"
factory-boy = "^3.3.0"
faker = "^20.1.0"
```

### Development Dependencies
```toml
mypy = "^1.7.0"
black = "^23.11.0"
isort = "^5.12.0"
ruff = "^0.1.6"
pre-commit = "^3.6.0"
```

## Performance Requirements

### Response Times (with DuckDB optimization)
- Simple queries: < 0.5ms
- Complex analytics: < 5ms
- Bulk operations: < 50ms for 10,000 records
- Connection acquisition: < 1ms

### Scalability Targets
- Support for millions of projects
- Efficient memory usage with connection pooling
- Graceful handling of high concurrency
- Optimized for analytical workloads

## Quality Gates

### Code Quality
- 100% type coverage (mypy strict mode)
- 100% test coverage with real database tests
- All linting checks pass (ruff, black, isort)
- No security vulnerabilities
- Performance benchmarks within targets

### Performance Benchmarks
- CRUD operations within response time targets
- Memory usage optimized for large datasets
- Concurrent access performance validated
- Analytics query performance benchmarked

## CLI Commands

```bash
# Development setup
project-architect-db init          # Initialize new database
project-architect-db migrate       # Run database migrations
project-architect-db seed          # Seed test data

# Testing
project-architect-db test          # Run all tests
project-architect-db test-parallel # Run tests in parallel
project-architect-db benchmark     # Run performance benchmarks

# Database management
project-architect-db db-reset      # Reset database
project-architect-db db-analyze    # Analyze database performance
project-architect-db db-vacuum     # Optimize database
```

## Success Metrics

- 100% test coverage maintained
- All tests pass in parallel execution
- Performance benchmarks consistently met
- Zero critical security vulnerabilities
- Complete type safety (mypy strict)
- Real-world usage validation with examples
- Comprehensive documentation and examples

## Key Implementation Priorities

1. **Async-First**: Every database operation must be async
2. **DuckDB Optimization**: Leverage analytical capabilities
3. **Type Safety**: Comprehensive typing throughout
4. **Real Testing**: No mocks, only real database tests
5. **Performance**: Meet all response time targets
6. **Examples**: Clear, executable examples for all features