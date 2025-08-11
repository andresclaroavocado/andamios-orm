# Test Configuration for Parallel Testing with Real Databases

## Overview

The Andamios ORM test suite is designed to run with 100% test coverage using real databases instead of mocks. Tests execute in parallel using pytest-xdist with isolated database instances per worker to ensure no test interference.

## Test Architecture

### Database Isolation Strategy

Each pytest worker gets its own isolated database instance:
- Worker 0: `test_andamios_orm_worker_0`
- Worker 1: `test_andamios_orm_worker_1` 
- Worker N: `test_andamios_orm_worker_N`

### Docker Test Infrastructure

```yaml
# docker/test-databases.yml
version: '3.8'
services:
  postgres-test:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
      POSTGRES_HOST_AUTH_METHOD: trust
    ports:
      - "5432:5432"
    volumes:
      - postgres_test_data:/var/lib/postgresql/data
    tmpfs:
      - /tmp
    shm_size: 256m

  mysql-test:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: test_password
      MYSQL_DATABASE: test_andamios_orm
      MYSQL_USER: test_user
      MYSQL_PASSWORD: test_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_test_data:/var/lib/mysql
    tmpfs:
      - /tmp

  mongodb-test:
    image: mongo:7-jammy
    environment:
      MONGO_INITDB_ROOT_USERNAME: test_user
      MONGO_INITDB_ROOT_PASSWORD: test_password
      MONGO_INITDB_DATABASE: test_andamios_orm
    ports:
      - "27017:27017"
    volumes:
      - mongodb_test_data:/data/db

  redis-test:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_test_data:/data

volumes:
  postgres_test_data:
  mysql_test_data:
  mongodb_test_data:
  redis_test_data:
```

## Test Configuration Files

### pytest.ini Enhanced Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --cov=andamios_orm
    --cov-report=term-missing:skip-covered
    --cov-report=html:htmlcov
    --cov-report=xml:coverage.xml
    --cov-fail-under=100
    --durations=10
    --tb=short
    -ra
    --disable-warnings
asyncio_mode = auto
markers =
    unit: Unit tests (isolated, fast)
    integration: Integration tests (with database)
    e2e: End-to-end tests (full workflows)
    slow: Slow tests (may take >5 seconds)
    performance: Performance benchmarking tests
    postgresql: Tests requiring PostgreSQL
    mysql: Tests requiring MySQL
    mongodb: Tests requiring MongoDB
    redis: Tests requiring Redis
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
    error::UserWarning
```

### Parallel Test Configuration

```python
# conftest.py - Root test configuration
import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
import uvloop

# Use uvloop for all async tests
@pytest.fixture(scope="session", autouse=True)
def event_loop_policy():
    """Set uvloop as the default event loop policy."""
    if os.name != 'nt':  # Not on Windows
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    return asyncio.get_event_loop_policy()

# Database test manager
from andamios_orm.testing.database import TestDatabaseManager

@pytest.fixture(scope="session")
def database_manager() -> TestDatabaseManager:
    """Provide database manager for test isolation."""
    return TestDatabaseManager()

@pytest.fixture(scope="session")
async def setup_test_databases(database_manager, worker_id):
    """Setup isolated test databases for parallel testing."""
    await database_manager.setup_worker_databases(worker_id)
    yield
    await database_manager.cleanup_worker_databases(worker_id)

# Session-scoped fixtures for database connections
@pytest.fixture(scope="session")
async def postgres_engine(setup_test_databases, worker_id):
    """Provide PostgreSQL engine for tests."""
    from andamios_orm.core.engine import create_async_engine
    
    database_url = f"postgresql+asyncpg://test_user:test_password@localhost:5432/test_andamios_orm_{worker_id}"
    engine = create_async_engine(database_url, echo=False)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="session") 
async def mysql_engine(setup_test_databases, worker_id):
    """Provide MySQL engine for tests."""
    from andamios_orm.core.engine import create_async_engine
    
    database_url = f"mysql+aiomysql://test_user:test_password@localhost:3306/test_andamios_orm_{worker_id}"
    engine = create_async_engine(database_url, echo=False)
    yield engine
    await engine.dispose()

# Function-scoped fixtures for clean sessions
@pytest.fixture
async def db_session(postgres_engine):
    """Provide clean database session for each test."""
    from andamios_orm.core.session import AsyncSession
    
    async with AsyncSession(postgres_engine) as session:
        # Start a transaction
        trans = await session.begin()
        
        yield session
        
        # Rollback transaction to leave database clean
        await trans.rollback()

@pytest.fixture
async def user_repository(db_session):
    """Provide user repository for tests."""
    from andamios_orm.repositories.user import UserRepository
    return UserRepository(db_session)
```

### Test Database Manager Implementation

```python
# src/andamios_orm/testing/database.py
import asyncio
import os
from typing import Dict, Optional
import asyncpg
import aiomysql
from motor.motor_asyncio import AsyncIOMotorClient

class TestDatabaseManager:
    """Manages isolated test databases for parallel testing."""
    
    def __init__(self):
        self.worker_databases: Dict[str, Dict[str, str]] = {}
        
    async def setup_worker_databases(self, worker_id: str) -> None:
        """Create isolated databases for a test worker."""
        databases = {}
        
        # PostgreSQL
        pg_db_name = f"test_andamios_orm_{worker_id}"
        await self._create_postgres_database(pg_db_name)
        databases['postgresql'] = pg_db_name
        
        # MySQL
        mysql_db_name = f"test_andamios_orm_{worker_id}"
        await self._create_mysql_database(mysql_db_name)
        databases['mysql'] = mysql_db_name
        
        # MongoDB
        mongo_db_name = f"test_andamios_orm_{worker_id}"
        databases['mongodb'] = mongo_db_name
        
        self.worker_databases[worker_id] = databases
        
    async def cleanup_worker_databases(self, worker_id: str) -> None:
        """Clean up databases for a test worker."""
        if worker_id not in self.worker_databases:
            return
            
        databases = self.worker_databases[worker_id]
        
        # PostgreSQL cleanup
        if 'postgresql' in databases:
            await self._drop_postgres_database(databases['postgresql'])
            
        # MySQL cleanup  
        if 'mysql' in databases:
            await self._drop_mysql_database(databases['mysql'])
            
        # MongoDB cleanup (collections are auto-cleaned)
        
        del self.worker_databases[worker_id]
        
    async def _create_postgres_database(self, db_name: str) -> None:
        """Create PostgreSQL test database."""
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='test_user',
            password='test_password',
            database='postgres'
        )
        
        try:
            # Drop if exists, then create
            await conn.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
            await conn.execute(f'CREATE DATABASE "{db_name}"')
        finally:
            await conn.close()
            
    async def _drop_postgres_database(self, db_name: str) -> None:
        """Drop PostgreSQL test database."""
        conn = await asyncpg.connect(
            host='localhost',
            port=5432, 
            user='test_user',
            password='test_password',
            database='postgres'
        )
        
        try:
            await conn.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
        finally:
            await conn.close()
            
    async def _create_mysql_database(self, db_name: str) -> None:
        """Create MySQL test database."""
        conn = await aiomysql.connect(
            host='localhost',
            port=3306,
            user='test_user',
            password='test_password',
            database='mysql'
        )
        
        try:
            cursor = await conn.cursor()
            await cursor.execute(f'DROP DATABASE IF EXISTS `{db_name}`')
            await cursor.execute(f'CREATE DATABASE `{db_name}`')
        finally:
            conn.close()
            
    async def _drop_mysql_database(self, db_name: str) -> None:
        """Drop MySQL test database." ""
        conn = await aiomysql.connect(
            host='localhost',
            port=3306,
            user='test_user', 
            password='test_password',
            database='mysql'
        )
        
        try:
            cursor = await conn.cursor()
            await cursor.execute(f'DROP DATABASE IF EXISTS `{db_name}`')
        finally:
            conn.close()
```

### Test Data Factories

```python
# tests/factories.py
import factory
import factory.fuzzy
from datetime import datetime, timezone
from typing import Any, Dict

from andamios_orm.models.user import User
from andamios_orm.models.profile import Profile

class AsyncFactory(factory.Factory):
    """Base factory for async model creation."""
    
    class Meta:
        abstract = True
        
    @classmethod
    async def create_async(cls, **kwargs) -> Any:
        """Create instance asynchronously."""
        return cls.create(**kwargs)
        
    @classmethod
    async def create_batch_async(cls, size: int, **kwargs) -> list:
        """Create multiple instances asynchronously."""
        return [await cls.create_async(**kwargs) for _ in range(size)]

class UserFactory(AsyncFactory):
    """Factory for User model."""
    
    class Meta:
        model = User
        
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_verified = False
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

class ProfileFactory(AsyncFactory):
    """Factory for Profile model."""
    
    class Meta:
        model = Profile
        
    bio = factory.Faker('text', max_nb_chars=200)
    avatar_url = factory.Faker('url')
    birth_date = factory.Faker('date_of_birth', minimum_age=18, maximum_age=80)
    location = factory.Faker('city')
```

### Performance Test Configuration

```python
# tests/conftest_performance.py
import pytest
import time
import psutil
import asyncio
from typing import Dict, Any

class PerformanceMonitor:
    """Monitor performance metrics during tests."""
    
    def __init__(self):
        self.start_time: float = 0
        self.start_memory: float = 0
        self.metrics: Dict[str, Any] = {}
        
    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        self.start_time = time.perf_counter()
        self.start_memory = psutil.Process().memory_info().rss
        
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return metrics."""
        end_time = time.perf_counter()
        end_memory = psutil.Process().memory_info().rss
        
        self.metrics.update({
            'duration_seconds': end_time - self.start_time,
            'memory_usage_mb': (end_memory - self.start_memory) / 1024 / 1024,
            'peak_memory_mb': psutil.Process().memory_info().rss / 1024 / 1024
        })
        
        return self.metrics

@pytest.fixture
def performance_monitor():
    """Provide performance monitoring for tests."""
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    yield monitor
    metrics = monitor.stop_monitoring()
    
    # Log performance metrics
    print(f"\nPerformance Metrics: {metrics}")

# Performance test markers
@pytest.mark.performance
async def test_bulk_insert_performance(db_session, performance_monitor):
    """Test bulk insert performance."""
    # Test implementation
    pass

@pytest.mark.slow
async def test_complex_query_performance(db_session, performance_monitor):
    """Test complex query performance."""
    # Test implementation  
    pass
```

## Test Execution Commands

### Local Development Testing

```bash
# Run all tests
poetry run pytest

# Run tests in parallel (4 workers)
poetry run pytest -n 4

# Run only unit tests
poetry run pytest -m "unit" -n 4

# Run only integration tests  
poetry run pytest -m "integration" -n 2

# Run specific database tests
poetry run pytest -m "postgresql" -n 2

# Run performance tests
poetry run pytest -m "performance" --durations=0

# Run with verbose output and coverage
poetry run pytest -v --cov=andamios_orm --cov-report=html -n 4

# Run specific test file in parallel
poetry run pytest tests/unit/test_models.py -n 4
```

### CI/CD Pipeline Testing

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
        database: ["postgresql", "mysql"]
        
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_USER: test_user
          POSTGRES_DB: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
          
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: test_password
          MYSQL_DATABASE: test_andamios_orm
          MYSQL_USER: test_user
          MYSQL_PASSWORD: test_password
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
        ports:
          - 3306:3306

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install Poetry
      uses: snok/install-poetry@v1
      
    - name: Install dependencies
      run: poetry install --with test,dev
      
    - name: Wait for databases
      run: |
        sleep 10
        
    - name: Run tests
      run: |
        poetry run pytest -n 4 --cov=andamios_orm --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Docker Test Environment

```bash
# Start test databases
docker-compose -f docker/test-databases.yml up -d

# Wait for databases to be ready
docker-compose -f docker/test-databases.yml exec postgres-test pg_isready
docker-compose -f docker/test-databases.yml exec mysql-test mysqladmin ping

# Run tests with parallel execution
poetry run pytest -n 4

# Stop test databases
docker-compose -f docker/test-databases.yml down -v
```

### Test Coverage Requirements

- **Unit Tests**: 100% coverage of all non-async code paths
- **Integration Tests**: 100% coverage of database operations 
- **End-to-End Tests**: Coverage of complete user workflows
- **Performance Tests**: Baseline metrics for all operations
- **Error Handling**: 100% coverage of exception paths

### Test Organization

```
tests/
├── unit/                           # Fast, isolated tests
│   ├── test_models.py             # Model unit tests
│   ├── test_repositories.py       # Repository unit tests
│   └── test_queries.py            # Query builder unit tests
├── integration/                    # Database integration tests
│   ├── test_crud_operations.py    # CRUD integration tests
│   ├── test_transactions.py       # Transaction tests
│   └── test_migrations.py         # Migration tests
├── e2e/                           # End-to-end workflow tests
│   ├── test_user_workflows.py     # Complete user scenarios
│   └── test_api_integration.py    # API integration tests
├── performance/                    # Performance benchmarks
│   ├── test_bulk_operations.py    # Bulk operation benchmarks
│   └── test_query_performance.py  # Query performance tests
├── factories/                      # Test data factories
│   ├── user_factory.py           # User test data
│   └── profile_factory.py        # Profile test data
└── fixtures/                      # Test fixtures and utilities
    ├── database_fixtures.py       # Database setup fixtures
    └── mock_data.py               # Mock data utilities
```

This test configuration ensures reliable, fast, and comprehensive testing with real databases while supporting parallel execution for optimal development workflow.