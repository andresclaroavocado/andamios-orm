"""
Pytest configuration and fixtures for Andamios ORM tests
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Generator, AsyncGenerator
import logging

# Import the modules we're testing
from src.andamios_orm.core.engine import create_memory_engine, get_engine, set_engine
from src.andamios_orm.core.session import init_db, get_session, SessionManager
from src.andamios_orm.core.database import DatabaseInitializer
from src.andamios_orm.models.base import Base
from src.andamios_orm.logging import setup_logging, TESTING_CONFIG


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Setup logging for tests with minimal output."""
    TESTING_CONFIG.apply()
    yield
    # Clear handlers after each test
    logger = logging.getLogger("andamios_orm")
    logger.handlers.clear()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def memory_engine():
    """Create an in-memory engine for testing."""
    engine = create_memory_engine(echo=False)
    yield engine
    engine.dispose()


@pytest.fixture
def test_engine(memory_engine):
    """Set up a test engine and clean up after test."""
    original_engine = get_engine() if hasattr(get_engine, '_engine') else None
    set_engine(memory_engine)
    
    yield memory_engine
    
    # Restore original engine if it existed
    if original_engine:
        set_engine(original_engine)


@pytest.fixture
async def test_session(test_engine):
    """Create a test session with automatic cleanup."""
    session = await get_session()
    yield session
    await session.close()


@pytest.fixture
async def initialized_db(test_engine):
    """Initialize database with test tables."""
    init_db(test_engine)
    # Create all tables
    db_init = DatabaseInitializer(test_engine)
    await db_init.create_all_tables()
    yield test_engine
    # Cleanup is handled by engine fixture


@pytest.fixture
def session_manager(test_engine):
    """Create a session manager for testing."""
    return SessionManager(test_engine)


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing logging functionality."""
    mock = Mock()
    mock.debug = Mock()
    mock.info = Mock()
    mock.warning = Mock()
    mock.error = Mock()
    mock.critical = Mock()
    return mock


@pytest.fixture
def mock_async_logger():
    """Create a mock async logger for testing async logging functionality."""
    mock = AsyncMock()
    mock.debug = AsyncMock()
    mock.info = AsyncMock()
    mock.warning = AsyncMock()
    mock.error = AsyncMock()
    mock.critical = AsyncMock()
    return mock


@pytest.fixture
async def sample_data():
    """Provide sample data for testing."""
    return {
        "projects": [
            {
                "id": 1,
                "name": "Test Project",
                "description": "A test project",
                "project_idea": "Build something awesome",
                "status": "active"
            }
        ],
        "conversations": [
            {
                "id": 1,
                "project_id": 1,
                "phase": "project_idea",
                "messages": ["Hello", "World"]
            }
        ],
        "documents": [
            {
                "id": 1,
                "project_id": 1,
                "name": "README.md",
                "content": "# Test Project",
                "doc_type": "markdown"
            }
        ],
        "repositories": [
            {
                "id": 1,
                "project_id": 1,
                "name": "test-repo",
                "description": "Test repository",
                "repo_type": "git"
            }
        ]
    }


@pytest.fixture
def mock_uvloop():
    """Mock uvloop for testing without actual uvloop dependency."""
    with patch('src.andamios_orm.core.engine.uvloop') as mock:
        mock.install = Mock()
        mock.EventLoopPolicy = Mock()
        yield mock


@pytest.fixture
def mock_sqlalchemy_engine():
    """Mock SQLAlchemy engine for testing."""
    mock = Mock()
    mock.dispose = Mock()
    mock.connect = Mock()
    mock.execute = Mock()
    return mock


@pytest.fixture
def mock_sqlalchemy_session():
    """Mock SQLAlchemy session for testing."""
    mock = Mock()
    mock.add = Mock()
    mock.commit = Mock()
    mock.rollback = Mock()
    mock.refresh = Mock()
    mock.get = Mock()
    mock.delete = Mock()
    mock.close = Mock()
    mock.execute = Mock()
    mock.bulk_insert_mappings = Mock()
    mock.bulk_update_mappings = Mock()
    return mock


@pytest.fixture
def mock_asyncio():
    """Mock asyncio for testing async functionality."""
    with patch('asyncio.to_thread') as mock_to_thread:
        # Configure to return the result directly for testing
        mock_to_thread.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)
        yield mock_to_thread


class AsyncContextManagerMock:
    """Mock for async context managers."""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
    
    async def __aenter__(self):
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def async_context_mock():
    """Create an async context manager mock."""
    return AsyncContextManagerMock


# Test data fixtures for specific model types
@pytest.fixture
def project_data():
    """Sample project data."""
    return {
        "name": "Test Project",
        "description": "A test project for unit testing",
        "project_idea": "Create comprehensive tests",
        "status": "draft"
    }


@pytest.fixture
def conversation_data():
    """Sample conversation data."""
    return {
        "project_id": 1,
        "phase": "project_idea",
        "messages": ["Initial message", "Follow-up message"]
    }


@pytest.fixture
def document_data():
    """Sample document data."""
    return {
        "project_id": 1,
        "name": "test_document.md",
        "content": "# Test Document\nThis is a test document.",
        "doc_type": "markdown",
        "file_path": "/path/to/test_document.md"
    }


@pytest.fixture
def repository_data():
    """Sample repository data."""
    return {
        "project_id": 1,
        "name": "test-repository",
        "description": "Test repository for unit testing",
        "repo_type": "git",
        "github_url": "https://github.com/test/test-repository"
    }


# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.perf_counter()
        
        def stop(self):
            self.end_time = time.perf_counter()
        
        @property
        def elapsed(self):
            if self.start_time is None or self.end_time is None:
                return None
            return self.end_time - self.start_time
    
    return Timer()


# Exception testing fixtures
@pytest.fixture
def sample_exception():
    """Sample exception for testing error handling."""
    return Exception("Test exception for unit testing")


@pytest.fixture
def sample_context():
    """Sample context data for exception testing."""
    return {
        "operation": "test_operation",
        "table": "test_table",
        "field": "test_field",
        "value": "test_value"
    }


# Cleanup fixtures
@pytest.fixture(autouse=True)
async def cleanup_globals():
    """Clean up global state between tests."""
    yield
    
    # Clear any global engine state
    try:
        from src.andamios_orm.core.engine import _engine, _async_engine
        _engine = None
        _async_engine = None
    except (ImportError, AttributeError):
        pass
    
    # Clear any global session state
    try:
        from src.andamios_orm.core.session import _global_engine, _global_sessionmaker
        _global_engine = None
        _global_sessionmaker = None
    except (ImportError, AttributeError):
        pass