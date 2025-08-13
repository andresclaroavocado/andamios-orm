"""
Pytest configuration for Andamios ORM tests.

This file configures:
- Async test support with pytest-asyncio
- Real database fixtures for integration tests
- Parallel test execution with pytest-xdist
- Test data factories
- Performance monitoring
"""

import asyncio
import os
import tempfile
import uuid
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
import uvloop
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from andamios_orm import Base, sessionmaker


# Configure pytest-asyncio
pytest_asyncio.fixture(scope="session")
def event_loop_policy():
    """Use uvloop for all async tests."""
    return uvloop.EventLoopPolicy()


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    policy = uvloop.EventLoopPolicy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test databases."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope="session")
async def test_engine(temp_dir: Path):
    """
    Create a test database engine for the session.
    
    Each test session gets its own database file to avoid conflicts
    during parallel test execution.
    """
    # Create unique database file for this test session
    db_file = temp_dir / f"test_{uuid.uuid4().hex}.db"
    database_url = f"duckdb:///{db_file}"
    
    engine = create_async_engine(
        database_url,
        echo=False,  # Set to True for SQL debugging
        pool_size=5,
        max_overflow=10,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()
    if db_file.exists():
        db_file.unlink()


@pytest.fixture
async def session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a database session for a test.
    
    Each test gets a fresh session with automatic rollback
    to ensure test isolation.
    """
    SessionLocal = sessionmaker(test_engine, class_=AsyncSession)
    
    async with SessionLocal() as session:
        # Start a transaction
        await session.begin()
        
        try:
            yield session
        finally:
            # Always rollback to ensure test isolation
            await session.rollback()


@pytest.fixture
async def clean_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a clean database session that commits changes.
    
    Use this for tests that need to verify actual database state
    or test transaction behavior.
    """
    SessionLocal = sessionmaker(test_engine, class_=AsyncSession)
    
    async with SessionLocal() as session:
        yield session


# Test data factories
@pytest.fixture
def user_factory():
    """Factory for creating test users."""
    def create_user(**kwargs):
        from tests.factories import UserFactory
        return UserFactory.build(**kwargs)
    return create_user


@pytest.fixture
def product_factory():
    """Factory for creating test products."""
    def create_product(**kwargs):
        from tests.factories import ProductFactory
        return ProductFactory.build(**kwargs)
    return create_product


@pytest.fixture
def order_factory():
    """Factory for creating test orders."""
    def create_order(**kwargs):
        from tests.factories import OrderFactory
        return OrderFactory.build(**kwargs)
    return create_order


# Performance monitoring fixtures
@pytest.fixture
def performance_monitor():
    """Fixture to monitor test performance."""
    import time
    from contextlib import contextmanager
    
    measurements = {}
    
    @contextmanager
    def measure(operation_name: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            end = time.perf_counter()
            measurements[operation_name] = end - start
    
    def get_measurements():
        return measurements.copy()
    
    # Return helper functions
    return type('PerformanceMonitor', (), {
        'measure': measure,
        'get_measurements': get_measurements
    })()


# Database isolation for parallel tests
@pytest.fixture(scope="function")
async def isolated_db(temp_dir: Path) -> AsyncGenerator[AsyncSession, None]:
    """
    Create an isolated database for tests that need complete isolation.
    
    This is useful for tests that modify global state or need
    to test database-level operations.
    """
    # Create unique database for this test
    db_file = temp_dir / f"isolated_{uuid.uuid4().hex}.db"
    database_url = f"duckdb:///{db_file}"
    
    engine = create_async_engine(database_url, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with SessionLocal() as session:
        yield session
    
    await engine.dispose()
    if db_file.exists():
        db_file.unlink()


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Test collection configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add automatic markers."""
    for item in items:
        # Add markers based on test file location
        if "unit" in item.fspath.dirname:
            item.add_marker(pytest.mark.unit)
        elif "integration" in item.fspath.dirname:
            item.add_marker(pytest.mark.integration)
        elif "e2e" in item.fspath.dirname:
            item.add_marker(pytest.mark.e2e)
        
        # Mark async tests
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


# Environment setup
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    # Set test-specific environment variables
    os.environ["ANDAMIOS_ORM_TESTING"] = "true"
    os.environ["ANDAMIOS_ORM_LOG_LEVEL"] = "WARNING"
    
    yield
    
    # Cleanup
    os.environ.pop("ANDAMIOS_ORM_TESTING", None)
    os.environ.pop("ANDAMIOS_ORM_LOG_LEVEL", None)


# Coverage configuration
def pytest_configure_coverage():
    """Configure coverage settings."""
    return {
        'source': ['src/andamios_orm'],
        'omit': [
            '*/tests/*',
            '*/test_*',
            '*/__pycache__/*',
            '*/venv/*',
            '*/virtualenv/*',
        ],
        'fail_under': 100,  # Require 100% coverage
        'show_missing': True,
        'precision': 2,
    }