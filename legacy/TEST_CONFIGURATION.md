# Test Configuration for Project Architect DB

## Overview

This document outlines the comprehensive testing strategy for Project Architect DB, focusing on real database testing with DuckDB, parallel execution, and 100% coverage requirements.

## Testing Philosophy

### Core Principles
1. **Real Database Testing**: No mocks - all tests use actual DuckDB instances
2. **Parallel Execution**: Tests run in parallel with isolated databases per worker
3. **100% Coverage**: Mandatory test coverage with meaningful tests
4. **Async-First**: All tests are async and use real async operations
5. **Example-Driven**: Tests validate examples work as documented

### Test Categories
- **Unit Tests**: Individual component validation
- **Integration Tests**: Full database operations with real DuckDB
- **Performance Tests**: Benchmark critical operations
- **Concurrency Tests**: Parallel access validation  
- **End-to-End Tests**: Complete workflow testing

## Test Environment Setup

### Dependencies

```toml
[tool.poetry.group.test.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-xdist = "^3.5.0"
pytest-cov = "^4.1.0"
pytest-benchmark = "^4.0.0"
pytest-mock = "^3.12.0"  # Only for external service mocking, not database
factory-boy = "^3.3.0"
faker = "^20.1.0"
pytest-timeout = "^2.2.0"
pytest-repeat = "^0.9.3"
pytest-randomly = "^3.15.0"
```

### Pytest Configuration

**File**: `pytest.ini`
```ini
[tool:pytest]
minversion = 7.0
addopts = 
    --strict-markers
    --strict-config
    --disable-warnings
    --cov=src/project_architect_db
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=100
    --asyncio-mode=auto
    --timeout=300
testpaths = tests
markers =
    unit: Unit tests (isolated components)
    integration: Integration tests (with database)
    performance: Performance and benchmark tests
    e2e: End-to-end workflow tests
    slow: Tests that take longer than 10 seconds
    parallel: Tests that can run in parallel
    serial: Tests that must run serially
asyncio_mode = auto
asyncio_default_fixture_loop_scope = session
timeout = 300
timeout_method = thread
```

### MyPy Configuration for Tests

**File**: `mypy.ini` (test-specific settings)
```ini
[mypy-tests.*]
disable_error_code = import-untyped
allow_untyped_defs = true
allow_untyped_calls = true
```

## Database Test Management

### Test Database Architecture

Each test worker gets an isolated DuckDB instance to enable parallel execution:

```python
# tests/conftest.py
import asyncio
import uuid
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from project_architect_db.core.engine import DatabaseEngine
from project_architect_db.models.base import Base


class TestDatabaseManager:
    """Manages isolated test databases for parallel execution"""
    
    def __init__(self, worker_id: str = "main"):
        self.worker_id = worker_id
        self.test_id = uuid.uuid4().hex[:8]
        self.db_path = Path(f"test_db_{worker_id}_{self.test_id}.duckdb")
        self.engine = None
        self.session_factory = None
    
    async def setup(self):
        """Initialize test database with schema"""
        # Use memory database for unit tests, file for integration
        db_url = f"duckdb:///{self.db_path}"
        
        self.engine = create_async_engine(
            db_url,
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,
            connect_args={
                "config": {
                    "memory_limit": "512MB",
                    "threads": "2",
                    "temp_directory": "/tmp/duckdb_test_temp"
                }
            }
        )
        
        # Create all tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Create session factory
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def teardown(self):
        """Clean up test database and connections"""
        if self.engine:
            await self.engine.dispose()
        
        # Remove test database file
        if self.db_path.exists():
            self.db_path.unlink()
    
    async def get_session(self) -> AsyncSession:
        """Get a new database session"""
        if not self.session_factory:
            raise RuntimeError("Database not initialized. Call setup() first.")
        
        return self.session_factory()
    
    async def reset_database(self):
        """Reset database to clean state between tests"""
        if not self.engine:
            return
            
        async with self.engine.begin() as conn:
            # Drop and recreate all tables
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)


# Worker ID detection for parallel execution
def pytest_configure_node(node):
    """Configure each test worker with unique identifier"""
    node.workerinput["worker_id"] = getattr(node, "workerinput", {}).get("workerid", "main")


@pytest.fixture(scope="session")
def worker_id(request):
    """Get unique worker ID for database isolation"""
    if hasattr(request.config, "workerinput"):
        return request.config.workerinput.get("worker_id", "main")
    return "main"


@pytest_asyncio.fixture(scope="session")
async def test_db_manager(worker_id) -> AsyncGenerator[TestDatabaseManager, None]:
    """Session-scoped database manager per worker"""
    manager = TestDatabaseManager(worker_id)
    await manager.setup()
    yield manager
    await manager.teardown()


@pytest_asyncio.fixture
async def db_session(test_db_manager) -> AsyncGenerator[AsyncSession, None]:
    """Function-scoped database session with automatic rollback"""
    async with test_db_manager.get_session() as session:
        # Start a transaction
        transaction = await session.begin()
        
        try:
            yield session
        finally:
            # Always rollback to maintain test isolation
            await transaction.rollback()
            await session.close()


@pytest_asyncio.fixture
async def clean_db_session(test_db_manager) -> AsyncGenerator[AsyncSession, None]:
    """Function-scoped session with database reset for integration tests"""
    await test_db_manager.reset_database()
    async with test_db_manager.get_session() as session:
        yield session
        await session.close()
```

## Test Data Factories

### Factory Configuration

```python
# tests/factories.py
import factory
import factory.fuzzy
from datetime import datetime, timedelta
from faker import Faker

from project_architect_db.models.project import Project
from project_architect_db.models.conversation import Conversation
from project_architect_db.models.document import Document
from project_architect_db.models.repository import Repository

fake = Faker()


class BaseFactory(factory.Factory):
    """Base factory with common configuration"""
    
    class Meta:
        abstract = True
    
    created_at = factory.LazyFunction(lambda: fake.date_time_between(
        start_date="-30d", 
        end_date="now"
    ))


class ProjectFactory(BaseFactory):
    """Factory for creating test projects"""
    
    class Meta:
        model = Project
    
    name = factory.Faker("company")
    description = factory.Faker("text", max_nb_chars=200)
    project_idea = factory.Faker("text", max_nb_chars=500)
    status = factory.fuzzy.FuzzyChoice(["draft", "active", "completed", "archived"])
    
    architecture = factory.LazyFunction(lambda: {
        "framework": fake.random_element([
            "FastAPI", "Django", "Flask", "Starlette"
        ]),
        "database": fake.random_element([
            "PostgreSQL", "DuckDB", "SQLite", "MySQL"
        ]),
        "deployment": fake.random_element([
            "Docker", "Kubernetes", "Serverless", "Traditional"
        ]),
        "complexity_score": fake.random_int(1, 10),
        "estimated_duration": fake.random_int(1, 52),  # weeks
        "team_size": fake.random_int(1, 10),
        "technologies": fake.random_elements([
            "Python", "JavaScript", "TypeScript", "React", "Vue", 
            "Redis", "Celery", "GraphQL", "REST", "WebSockets"
        ], length=fake.random_int(2, 6), unique=True)
    })


class ConversationFactory(BaseFactory):
    """Factory for creating test conversations"""
    
    class Meta:
        model = Conversation
    
    project_id = factory.SelfAttribute("project.id")
    phase = factory.fuzzy.FuzzyChoice([
        "project_idea", "architecture", "implementation", 
        "testing", "deployment", "maintenance"
    ])
    
    messages = factory.LazyFunction(lambda: [
        {
            "role": "user",
            "content": fake.text(max_nb_chars=200),
            "timestamp": fake.date_time_between(start_date="-1d", end_date="now").isoformat()
        },
        {
            "role": "assistant", 
            "content": fake.text(max_nb_chars=400),
            "timestamp": fake.date_time_between(start_date="-1d", end_date="now").isoformat()
        }
        for _ in range(fake.random_int(1, 10))
    ])


class DocumentFactory(BaseFactory):
    """Factory for creating test documents"""
    
    class Meta:
        model = Document
    
    project_id = factory.SelfAttribute("project.id")
    name = factory.Faker("file_name")
    content = factory.Faker("text", max_nb_chars=1000)
    doc_type = factory.fuzzy.FuzzyChoice([
        "architecture", "api_spec", "deployment", "testing", 
        "documentation", "requirements", "design"
    ])
    file_path = factory.LazyAttribute(
        lambda obj: f"/docs/{obj.project_id}/{obj.name}"
    )


class RepositoryFactory(BaseFactory):
    """Factory for creating test repositories"""
    
    class Meta:
        model = Repository
    
    project_id = factory.SelfAttribute("project.id")
    name = factory.LazyAttribute(
        lambda obj: f"{obj.project.name.lower().replace(' ', '-')}-{fake.word()}"
    )
    description = factory.Faker("text", max_nb_chars=200)
    repo_type = factory.fuzzy.FuzzyChoice([
        "backend", "frontend", "docs", "infrastructure", 
        "shared", "tools", "tests"
    ])
    github_url = factory.LazyAttribute(
        lambda obj: f"https://github.com/test-org/{obj.name}"
    )


# Factory for creating related objects
class ProjectWithRelatedFactory(ProjectFactory):
    """Factory that creates a project with related objects"""
    
    @factory.post_generation
    def conversations(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            # If specific conversations provided
            for conv_data in extracted:
                ConversationFactory(project=self, **conv_data)
        else:
            # Create random conversations
            ConversationFactory.create_batch(
                size=fake.random_int(1, 5),
                project=self
            )
    
    @factory.post_generation
    def documents(self, create, extracted, **kwargs):
        if not create:
            return
            
        if extracted:
            for doc_data in extracted:
                DocumentFactory(project=self, **doc_data)
        else:
            DocumentFactory.create_batch(
                size=fake.random_int(1, 8),
                project=self
            )
    
    @factory.post_generation  
    def repositories(self, create, extracted, **kwargs):
        if not create:
            return
            
        if extracted:
            for repo_data in extracted:
                RepositoryFactory(project=self, **repo_data)
        else:
            RepositoryFactory.create_batch(
                size=fake.random_int(1, 4),
                project=self
            )
```

## Test Structure and Organization

### Directory Structure

```
tests/
├── conftest.py                 # Global test configuration
├── factories.py               # Test data factories
├── utils.py                   # Test utilities
├── unit/                      # Unit tests (isolated components)
│   ├── __init__.py
│   ├── test_models.py         # Model validation tests
│   ├── test_schemas.py        # Pydantic schema tests
│   ├── test_exceptions.py     # Exception handling tests
│   ├── core/
│   │   ├── test_engine.py     # Database engine tests
│   │   ├── test_session.py    # Session management tests
│   │   └── test_connection.py # Connection handling tests
│   └── repositories/
│       ├── test_base.py       # Base repository tests
│       └── test_specialized.py # Specialized repository tests
├── integration/               # Integration tests (with database)
│   ├── __init__.py
│   ├── test_crud_operations.py # CRUD with real database
│   ├── test_transactions.py   # Transaction management
│   ├── test_relationships.py  # Model relationships
│   ├── test_migrations.py     # Database migrations
│   └── test_bulk_operations.py # Bulk operation testing
├── performance/               # Performance and benchmark tests
│   ├── __init__.py
│   ├── test_crud_performance.py # CRUD operation benchmarks
│   ├── test_bulk_performance.py # Bulk operation benchmarks
│   ├── test_analytics_performance.py # Analytics query benchmarks
│   └── test_concurrent_access.py # Concurrency testing
├── e2e/                       # End-to-end workflow tests
│   ├── __init__.py
│   ├── test_project_lifecycle.py # Complete project workflows
│   ├── test_conversation_flows.py # Conversation management
│   └── test_analytics_workflows.py # Analytics workflows
└── examples/                  # Example validation tests
    ├── __init__.py
    ├── test_basic_examples.py  # Validate basic examples work
    ├── test_advanced_examples.py # Validate advanced examples
    └── test_integration_examples.py # Validate integration examples
```

## Test Execution Configuration

### Parallel Execution

```bash
# Run all tests in parallel
pytest -n auto

# Run with specific number of workers
pytest -n 4

# Run with coverage in parallel
pytest -n auto --cov=src/project_architect_db --cov-report=html

# Run only fast tests in parallel
pytest -n auto -m "not slow"

# Run specific test categories
pytest -n auto tests/unit/          # Unit tests only
pytest -n auto tests/integration/   # Integration tests only
pytest -n auto tests/performance/   # Performance tests only
```

### Performance Testing

```python
# tests/performance/conftest.py
import pytest
from pytest_benchmark.plugin import BenchmarkFixture


@pytest.fixture
def benchmark_config():
    """Configure benchmark parameters"""
    return {
        "min_rounds": 10,
        "max_time": 30.0,
        "timer": "time.perf_counter",
        "disable_gc": True,
        "warmup": True,
        "warmup_iterations": 3
    }


# Example performance test
@pytest.mark.performance
async def test_crud_performance(db_session, benchmark):
    """Benchmark basic CRUD operations"""
    
    async def create_project():
        project_data = ProjectFactory.build().__dict__
        async with ProjectRepository(db_session) as repo:
            return await repo.create(project_data)
    
    # Benchmark project creation
    result = await benchmark(create_project)
    assert result.id is not None
    
    # Performance assertions
    assert benchmark.stats["mean"] < 0.001  # < 1ms average
    assert benchmark.stats["max"] < 0.005   # < 5ms max
```

### Memory Testing

```python
# tests/performance/test_memory_usage.py
import asyncio
import psutil
import pytest
from memory_profiler import profile


@pytest.mark.performance
async def test_memory_usage_bulk_operations(clean_db_session):
    """Test memory usage during bulk operations"""
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Create large dataset
    projects_data = [ProjectFactory.build().__dict__ for _ in range(10000)]
    
    async with ProjectRepository(clean_db_session) as repo:
        projects = await repo.bulk_create(projects_data)
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    # Assert memory usage is reasonable (< 100MB for 10k records)
    assert memory_increase < 100
    assert len(projects) == 10000


@profile
async def memory_profiled_function():
    """Function with memory profiling decorator"""
    # Implementation to be profiled
    pass
```

## Continuous Integration Configuration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
        
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install Poetry
      uses: snok/install-poetry@v1
      with:
        virtualenvs-create: true
        virtualenvs-in-project: true
    
    - name: Load cached venv
      id: cached-poetry-dependencies
      uses: actions/cache@v3
      with:
        path: .venv
        key: venv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('**/poetry.lock') }}
    
    - name: Install dependencies
      if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
      run: poetry install --no-interaction --no-root
    
    - name: Install package
      run: poetry install --no-interaction
    
    - name: Run linting
      run: |
        poetry run black --check src tests
        poetry run isort --check-only src tests
        poetry run ruff check src tests
        poetry run mypy src
    
    - name: Run tests with coverage
      run: |
        poetry run pytest -n auto --cov=src/project_architect_db \
          --cov-report=xml --cov-report=term-missing \
          --cov-fail-under=100
    
    - name: Run performance benchmarks
      run: |
        poetry run pytest tests/performance/ \
          --benchmark-only --benchmark-json=benchmark.json
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
    
    - name: Upload benchmark results
      uses: actions/upload-artifact@v3
      with:
        name: benchmark-results-${{ matrix.python-version }}
        path: benchmark.json

  integration-test:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python 3.12
      uses: actions/setup-python@v4
      with:
        python-version: "3.12"
    
    - name: Install Poetry
      uses: snok/install-poetry@v1
    
    - name: Install dependencies
      run: poetry install --no-interaction
    
    - name: Run integration tests
      run: |
        poetry run pytest tests/integration/ tests/e2e/ \
          -n auto --maxfail=5 --tb=short
    
    - name: Validate examples
      run: |
        poetry run pytest tests/examples/ \
          --tb=short --disable-warnings
```

## Test Quality Gates

### Coverage Requirements

```python
# tests/test_coverage.py
import subprocess
import pytest


def test_coverage_requirements():
    """Ensure 100% test coverage is maintained"""
    result = subprocess.run(
        ["poetry", "run", "pytest", "--cov=src/project_architect_db", 
         "--cov-report=term", "--cov-fail-under=100"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Coverage below 100%: {result.stdout}"


def test_no_uncovered_lines():
    """Ensure no lines are uncovered in critical modules"""
    critical_modules = [
        "src/project_architect_db/core/",
        "src/project_architect_db/repositories/",
        "src/project_architect_db/models/"
    ]
    
    for module in critical_modules:
        result = subprocess.run(
            ["poetry", "run", "coverage", "report", "--show-missing", module],
            capture_output=True,
            text=True
        )
        
        assert "100%" in result.stdout, f"Uncovered lines in {module}"
```

### Performance Benchmarks

```python
# tests/performance/test_benchmarks.py
import pytest


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmark validation"""
    
    async def test_crud_operation_benchmarks(self, db_session, benchmark):
        """CRUD operations must meet performance targets"""
        
        async def crud_operations():
            async with ProjectRepository(db_session) as repo:
                # Create
                project = await repo.create(ProjectFactory.build().__dict__)
                
                # Read
                retrieved = await repo.get_by_id(project.id)
                
                # Update
                updated = await repo.update(project.id, {"status": "active"})
                
                # Delete (soft delete)
                deleted = await repo.delete(project.id)
                
                return project, retrieved, updated, deleted
        
        result = await benchmark(crud_operations)
        
        # Performance assertions
        assert benchmark.stats["mean"] < 0.005  # < 5ms total for CRUD cycle
        assert benchmark.stats["max"] < 0.010   # < 10ms worst case
    
    async def test_bulk_operation_benchmarks(self, clean_db_session, benchmark):
        """Bulk operations must meet performance targets"""
        
        async def bulk_create():
            projects_data = [ProjectFactory.build().__dict__ for _ in range(1000)]
            async with ProjectRepository(clean_db_session) as repo:
                return await repo.bulk_create(projects_data)
        
        result = await benchmark(bulk_create)
        
        # Performance assertions
        assert len(result) == 1000
        assert benchmark.stats["mean"] < 0.050  # < 50ms for 1000 records
        assert benchmark.stats["max"] < 0.100   # < 100ms worst case
    
    async def test_analytics_query_benchmarks(self, clean_db_session, benchmark):
        """Analytics queries must meet performance targets"""
        
        # Setup test data
        projects = [ProjectFactory.build().__dict__ for _ in range(5000)]
        async with ProjectRepository(clean_db_session) as repo:
            await repo.bulk_create(projects)
        
        async def analytics_query():
            async with AnalyticsRepository(clean_db_session) as repo:
                return await repo.project_metrics()
        
        result = await benchmark(analytics_query)
        
        # Performance assertions
        assert result.total_projects == 5000
        assert benchmark.stats["mean"] < 0.005  # < 5ms for analytics
        assert benchmark.stats["max"] < 0.015   # < 15ms worst case
```

## Test Utilities

### Common Test Utilities

```python
# tests/utils.py
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any
from unittest.mock import AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession


class AsyncTestCase:
    """Base class for async test cases"""
    
    @staticmethod
    async def assert_async_equal(coro1, coro2):
        """Assert two coroutines return equal results"""
        result1 = await coro1
        result2 = await coro2
        assert result1 == result2
    
    @staticmethod
    async def assert_async_raises(exception_class, coro):
        """Assert coroutine raises specific exception"""
        with pytest.raises(exception_class):
            await coro


@asynccontextmanager
async def temporary_data(session: AsyncSession, factory_class, **kwargs) -> AsyncGenerator[Any, None]:
    """Context manager for temporary test data"""
    instance = factory_class(**kwargs)
    session.add(instance)
    await session.commit()
    await session.refresh(instance)
    
    try:
        yield instance
    finally:
        await session.delete(instance)
        await session.commit()


async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1):
    """Wait for an async condition to become true"""
    start_time = asyncio.get_event_loop().time()
    
    while asyncio.get_event_loop().time() - start_time < timeout:
        if await condition_func():
            return True
        await asyncio.sleep(interval)
    
    raise TimeoutError(f"Condition not met within {timeout} seconds")


class MockAsyncRepository:
    """Mock repository for unit testing"""
    
    def __init__(self):
        self._data = {}
        self._next_id = 1
    
    async def create(self, data: dict):
        item = {**data, "id": self._next_id}
        self._data[self._next_id] = item
        self._next_id += 1
        return item
    
    async def get_by_id(self, id: int):
        return self._data.get(id)
    
    async def update(self, id: int, data: dict):
        if id in self._data:
            self._data[id].update(data)
            return self._data[id]
        return None
    
    async def delete(self, id: int):
        return self._data.pop(id, None) is not None
```

This comprehensive test configuration ensures robust, parallel-capable testing with real DuckDB instances while maintaining 100% coverage and performance validation.