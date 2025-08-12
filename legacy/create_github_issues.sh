#!/bin/bash

# GitHub Issues Creation Script
# Run this after pushing the repository to GitHub
# Requires: gh CLI tool (install with: brew install gh or apt install gh)

echo "🚀 Creating GitHub Issues for Project Architect DB"
echo "================================================="

# Ensure you're logged into GitHub CLI
gh auth status || {
    echo "❌ Please login to GitHub CLI first: gh auth login"
    exit 1
}

# Phase 1: Core Foundation
echo "📋 Creating Phase 1 Issues (Core Foundation)..."

gh issue create \
    --title "Setup Project Structure and Configuration" \
    --body "Set up the complete project structure following modern Python best practices with async-first design.

**Acceptance Criteria:**
- [ ] Create complete directory structure as per ARCHITECTURE.md
- [ ] Configure \`pyproject.toml\` with all dependencies (DuckDB, SQLAlchemy 2.0+, uvloop, etc.)
- [ ] Set up development dependencies (pytest, mypy, black, ruff, etc.)
- [ ] Configure \`pytest.ini\` for async testing and parallel execution
- [ ] Set up \`mypy.ini\` for strict type checking
- [ ] Create \`.github/workflows/\` for CI/CD
- [ ] Set up pre-commit hooks configuration
- [ ] Create initial \`README.md\` with installation and quick start

**Technical Requirements:**
- Python 3.11+ support with 3.12 optimization
- DuckDB as primary database with \`duckdb-engine\` for SQLAlchemy
- All dependencies use latest stable versions
- Support for parallel testing with pytest-xdist
- Strict mypy configuration

**Definition of Done:**
- All configuration files created and validated
- CI/CD pipeline successfully runs tests, linting, and type checking
- Project can be installed via \`pip install -e .\`
- All quality gates pass (mypy, black, ruff, pytest)" \
    --milestone "Phase 1 - Core Foundation" \
    --label "setup,infrastructure,high-priority"

gh issue create \
    --title "Core Database Engine and Session Management" \
    --body "Implement the core database engine management with DuckDB optimization and async session handling.

**Acceptance Criteria:**
- [ ] Create \`DatabaseEngine\` class with async connection pooling
- [ ] Implement \`SessionManager\` with async context managers
- [ ] Add transaction support with rollback capabilities
- [ ] Configure DuckDB-specific optimizations (memory limits, threads, etc.)
- [ ] Implement graceful connection cleanup and shutdown
- [ ] Add connection health checks and monitoring
- [ ] Create async initialization and migration support

**Technical Requirements:**
- Use \`create_async_engine\` with optimized pool configuration
- Support both memory and file-based DuckDB instances
- Implement proper async context managers for sessions and transactions
- Add connection pooling with overflow and timeout handling
- Include performance monitoring hooks

**Definition of Done:**
- All engine and session classes implemented and tested
- Async context managers work correctly
- Connection pooling configured and validated
- Performance benchmarks meet targets (< 1ms connection acquisition)
- Comprehensive unit and integration tests with 100% coverage" \
    --milestone "Phase 1 - Core Foundation" \
    --label "core,async,database,high-priority"

gh issue create \
    --title "Base Models with SQLAlchemy 2.0 and Pydantic Integration" \
    --body "Create SQLAlchemy 2.0 models for Project, Conversation, Document, and Repository with full async support and Pydantic schema integration.

**Acceptance Criteria:**
- [ ] Create \`Base\` declarative base with common configuration
- [ ] Implement \`TimestampMixin\` for created_at/updated_at fields
- [ ] Create all four core models (Project, Conversation, Document, Repository)
- [ ] Add proper relationships with async loading strategies
- [ ] Configure indexes optimized for DuckDB
- [ ] Create corresponding Pydantic schemas for validation
- [ ] Implement proper type hints throughout

**Technical Requirements:**
- Use SQLAlchemy 2.0 syntax with \`Mapped\` types
- JSON fields for architecture and messages with proper typing
- Optimized indexes for common query patterns
- Async-compatible relationships with selectin loading
- Pydantic v2 schemas with proper validation

**Definition of Done:**
- All models created with proper typing and relationships
- Pydantic schemas for Create, Update, and Read operations
- Database migrations created and tested
- Models can be created, updated, and queried asynchronously
- All model tests pass with 100% coverage" \
    --milestone "Phase 1 - Core Foundation" \
    --label "models,sqlalchemy,pydantic,high-priority"

# Phase 2: Repository Pattern
echo "📋 Creating Phase 2 Issues (Repository Pattern)..."

gh issue create \
    --title "Base Repository with Generic Async Operations" \
    --body "Implement a generic base repository providing common async CRUD operations with type safety.

**Acceptance Criteria:**
- [ ] Create \`BaseRepository[T]\` with generic type support
- [ ] Implement async CRUD operations (create, read, update, delete)
- [ ] Add pagination support with limit/offset
- [ ] Implement filtering capabilities with type safety
- [ ] Add bulk operations for performance (bulk_create, bulk_update)
- [ ] Include soft delete functionality
- [ ] Add comprehensive error handling

**Technical Requirements:**
- Use Python 3.12 generic syntax: \`BaseRepository[T]\`
- All operations must be async with proper exception handling
- Support both dict and Pydantic model inputs
- Implement optimistic locking for updates
- Include query performance monitoring

**Definition of Done:**
- Base repository fully implemented with all methods
- Type safety validated with mypy strict mode
- Comprehensive test suite with real DuckDB testing
- Performance benchmarks meet targets
- Documentation with usage examples" \
    --milestone "Phase 2 - Repository Pattern" \
    --label "repository,async,generics,high-priority"

gh issue create \
    --title "Specialized Repository Implementations" \
    --body "Create specialized repositories for each domain model with business logic and domain-specific queries.

**Acceptance Criteria:**
- [ ] Implement \`ProjectRepository\` with project-specific operations
- [ ] Create \`ConversationRepository\` with message handling
- [ ] Build \`DocumentRepository\` with file management
- [ ] Develop \`RepositoryRepository\` for code repo tracking
- [ ] Add domain-specific filtering and search capabilities
- [ ] Implement cross-entity queries and joins
- [ ] Add specialized bulk operations

**Technical Requirements:**
- Domain-specific methods for each repository
- Complex queries optimized for DuckDB
- Cross-repository analytics capabilities
- Full-text search where appropriate
- JSON field querying support

**Definition of Done:**
- All four specialized repositories implemented
- Domain-specific methods tested and documented
- Complex queries optimized for DuckDB
- Cross-repository analytics working
- 100% test coverage with real database tests" \
    --milestone "Phase 2 - Repository Pattern" \
    --label "repository,specialized,domain-logic,high-priority"

gh issue create \
    --title "Advanced Query Builder and Filtering" \
    --body "Build an advanced async query builder with DuckDB-optimized filtering and JSON query support.

**Acceptance Criteria:**
- [ ] Create \`QueryBuilder[T]\` with fluent interface
- [ ] Implement common filtering operations
- [ ] Add JSON field querying using DuckDB JSON functions
- [ ] Support date range filtering with optimization
- [ ] Add ordering and pagination
- [ ] Implement aggregation queries
- [ ] Add query performance monitoring

**Technical Requirements:**
- Fluent interface for complex queries
- JSON querying optimized for DuckDB
- Performance monitoring and optimization
- Type-safe query building
- Comprehensive filtering capabilities

**Definition of Done:**
- Query builder with full fluent interface
- JSON querying optimized for DuckDB
- All filtering operations tested
- Performance benchmarks validated
- Comprehensive documentation with examples" \
    --milestone "Phase 2 - Repository Pattern" \
    --label "query-builder,filtering,duckdb,medium-priority"

echo "✅ Created 6 GitHub issues for Phases 1-2"
echo "🔄 Continue creating remaining issues manually or extend this script"
echo "📖 See GITHUB_ISSUES.md for all 16 issues"