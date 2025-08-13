# Andamios ORM - Architecture Design

## Overview

Andamios ORM is a modern, async-first Python ORM library built on DuckDB and SQLAlchemy 2.0+. It follows Example-Driven Development (EDD) followed by Test-Driven Development (TDD) principles, emphasizing real database testing and 100% coverage.

## Core Architectural Principles

### 1. Async-First Design
- All operations are async by default
- Built on `uvloop` for maximum performance
- Proper connection pooling and resource management
- Graceful concurrent operation handling

### 2. Example-Driven Development (EDD) → Test-Driven Development (TDD)
- **Phase 1**: Create practical, executable examples in `/examples/`
- **Phase 2**: Write comprehensive tests based on examples
- **Phase 3**: Implement functionality to satisfy tests
- **Phase 4**: Refactor and optimize

### 3. Real Database Testing
- Use actual DuckDB instances for all database tests
- No mocking of database operations
- Parallel test execution with isolated database instances
- Docker containers for consistent test environments

### 4. Type Safety & Performance
- Full type hints with mypy strict mode
- Generic repository patterns
- Optimized for DuckDB's columnar architecture
- Connection pooling and resource management

## Architecture Layers

### 1. Core Layer (`src/andamios_orm/core/`)
- **Engine Management**: DuckDB connection handling and pooling
- **Session Management**: Async session lifecycle and transaction management
- **Connection Handling**: Low-level connection operations and resource cleanup

### 2. Models Layer (`src/andamios_orm/models/`)
- **Base Model**: Foundation class with common functionality
- **Mixins**: Reusable model behaviors (timestamps, soft delete, etc.)
- **Type System**: Enhanced type support for DuckDB-specific features

### 3. Repository Layer (`src/andamios_orm/repositories/`)
- **Base Repository**: Common CRUD operations
- **Generic Repository**: Type-safe generic repository implementations
- **Specialized Repositories**: Domain-specific repository patterns
- **Transaction Management**: Repository-level transaction handling

### 4. Query Layer (`src/andamios_orm/queries/`)
- **Query Builder**: Fluent API for complex queries
- **Filter System**: Reusable filter definitions
- **Aggregation**: DuckDB-optimized aggregation operations
- **Raw Query Support**: Direct SQL execution with safety

### 5. Migration Layer (`src/andamios_orm/migration/`)
- **Migration Manager**: Database schema evolution
- **Version Control**: Migration versioning and dependency tracking
- **Rollback Support**: Safe migration rollback capabilities

### 6. Testing Layer (`src/andamios_orm/testing/`)
- **Test Fixtures**: Reusable test data and setup
- **Database Management**: Test database lifecycle
- **Parallel Support**: Multi-worker test database isolation
- **Factory System**: Test data generation

## Technology Stack

### Core Dependencies
- **Python 3.12+**: Latest Python features and performance
- **DuckDB 0.9.0+**: Primary database engine (columnar, analytical)
- **SQLAlchemy 2.0+**: ORM foundation with async support
- **uvloop 0.19.0+**: High-performance async event loop
- **Pydantic 2.5.0+**: Data validation and serialization

### Testing Stack
- **pytest 7.4.3+**: Test framework
- **pytest-asyncio 0.21.1+**: Async test support
- **pytest-xdist 3.5.0+**: Parallel test execution
- **pytest-cov 4.1.0+**: Coverage reporting
- **factory-boy 3.3.0+**: Test data factories

### Development Tools
- **mypy 1.7.0+**: Static type checking
- **ruff 0.1.6+**: Fast linting and formatting
- **pre-commit 3.6.0+**: Git hooks for quality

## Data Flow Architecture

```
Examples → Tests → Implementation → Optimization

┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Examples  │───▶│    Tests     │───▶│Implementation│
│             │    │              │    │             │
│ - Use cases │    │ - Unit tests │    │ - Core logic│
│ - Patterns  │    │ - Integration│    │ - Repositories│
│ - Workflows │    │ - E2E tests  │    │ - Queries   │
└─────────────┘    └──────────────┘    └─────────────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │Optimization │
                                       │             │
                                       │ - Performance│
                                       │ - Refactoring│
                                       │ - Documentation│
                                       └─────────────┘
```

## Database Strategy

### Primary Database: DuckDB
- **Columnar Storage**: Optimized for analytical workloads
- **In-Process**: No separate server process required
- **SQL Compliance**: Full SQL standard support
- **Performance**: Excellent for OLAP operations
- **Python Integration**: Native Python API

### Test Database Isolation
- Each test worker gets isolated DuckDB instance
- Parallel execution without interference
- Automatic cleanup after test completion
- Docker containers for consistent environments

## Performance Targets

### Response Times
- Simple queries: < 1ms
- Complex queries: < 10ms
- Bulk operations: < 100ms for 10,000 records
- Connection acquisition: < 5ms

### Scalability
- Support for 1000+ concurrent connections
- Efficient memory usage (< 100MB base)
- Proper resource cleanup and connection pooling
- Graceful degradation under load

## Security Considerations

### SQL Injection Prevention
- Parameterized queries only
- Input validation at all layers
- No dynamic SQL construction from user input

### Connection Security
- Secure connection string handling
- No credentials in logs or error messages
- Proper resource cleanup

## Extension Points

### Custom Repository Patterns
- Plugin architecture for specialized repositories
- Custom query builders for domain-specific needs
- Middleware support for cross-cutting concerns

### Event System
- Model lifecycle events (before/after operations)
- Transaction events (commit/rollback hooks)
- Custom event handlers

## Monitoring & Observability

### Metrics Collection
- Query performance metrics
- Connection pool statistics
- Error rates and patterns

### Logging
- Structured logging with correlation IDs
- Configurable log levels
- Query logging for debugging

## Future Considerations

### DuckDB Extensions
- Custom DuckDB extensions for specialized operations
- Advanced columnar operations and optimizations
- Vector operations and analytics functions

### Caching Layer
- Query result caching
- Model instance caching
- Cache invalidation strategies

### Distributed Features
- Connection pooling across instances
- Load balancing support
- Horizontal scaling patterns