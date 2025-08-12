# Project Architect DB - Architecture Documentation

## Overview

Project Architect DB is a high-performance, async-first database library designed specifically for project management and architecture systems. Built on DuckDB and SQLAlchemy 2.0+, it provides a modern, type-safe foundation for handling projects, conversations, documents, and repositories.

## Architecture Principles

### 1. Async-First Design
Every operation in the library is designed to be asynchronous by default:

```python
# All operations are async
async with ProjectRepository(session) as repo:
    project = await repo.create(project_data)
    projects = await repo.list_by_status("active")
    await repo.update(project.id, {"status": "completed"})
```

### 2. Repository Pattern
Clean separation of concerns with repository interfaces:

```python
# Base repository provides common operations
class BaseRepository[T]:
    async def create(self, data: dict) -> T
    async def get_by_id(self, id: int) -> T | None
    async def update(self, id: int, data: dict) -> T
    async def delete(self, id: int) -> bool
    async def list(self, **filters) -> list[T]

# Specialized repositories extend base functionality
class ProjectRepository(BaseRepository[Project]):
    async def get_by_status(self, status: str) -> list[Project]
    async def get_with_conversations(self, id: int) -> Project
    async def analytics_summary(self) -> ProjectAnalytics
```

### 3. Type Safety & Validation
Comprehensive type system with runtime validation:

```python
# Pydantic schemas for validation
class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    project_idea: str = Field(min_length=10)
    architecture: dict[str, Any] | None = None

# SQLAlchemy models with full typing
class Project(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

## Core Components

### 1. Database Engine Management

**File**: `src/project_architect_db/core/engine.py`

Manages DuckDB connections with async support and connection pooling:

```python
class DatabaseEngine:
    def __init__(self, database_url: str, **kwargs):
        self.engine = create_async_engine(
            database_url,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            **kwargs
        )
    
    async def get_session(self) -> AsyncSession:
        """Get async database session"""
        
    async def execute_raw(self, query: str) -> Result:
        """Execute raw SQL with DuckDB optimizations"""
        
    async def close(self):
        """Graceful shutdown"""
```

**Key Features**:
- Async connection pooling optimized for DuckDB
- Automatic connection health checks
- Query performance monitoring
- Graceful shutdown handling

### 2. Session Management

**File**: `src/project_architect_db/core/session.py`

Provides async session context managers and transaction support:

```python
class SessionManager:
    @asynccontextmanager
    async def session(self) -> AsyncSession:
        """Basic session context manager"""
        
    @asynccontextmanager
    async def transaction(self) -> AsyncSession:
        """Transaction context manager with rollback support"""
        
    async def execute_in_transaction(self, operations: list[Callable]):
        """Execute multiple operations in single transaction"""
```

**Transaction Patterns**:
```python
# Automatic transaction management
async with session_manager.transaction() as session:
    await project_repo.create(project_data)
    await conversation_repo.create(conversation_data)
    # Automatic commit or rollback on exception

# Manual transaction control
async with session_manager.session() as session:
    async with session.begin():
        result = await session.execute(complex_query)
        await session.commit()
```

### 3. Repository Layer

**Base Repository** (`src/project_architect_db/repositories/base.py`):

```python
class BaseRepository[T]:
    def __init__(self, session: AsyncSession, model_class: type[T]):
        self.session = session
        self.model_class = model_class
    
    async def create(self, data: dict | BaseModel) -> T:
        """Create new record with validation"""
        
    async def get_by_id(self, id: int) -> T | None:
        """Get record by ID with async loading"""
        
    async def update(self, id: int, data: dict | BaseModel) -> T:
        """Update record with optimistic locking"""
        
    async def delete(self, id: int) -> bool:
        """Soft delete with audit trail"""
        
    async def list(self, 
                  limit: int = 100, 
                  offset: int = 0, 
                  **filters) -> list[T]:
        """Paginated listing with filters"""
        
    async def count(self, **filters) -> int:
        """Count records matching filters"""
        
    async def bulk_create(self, data_list: list[dict]) -> list[T]:
        """High-performance bulk insert"""
        
    async def bulk_update(self, updates: list[dict]) -> int:
        """Bulk update operations"""
```

**Specialized Repositories**:

```python
# Project Repository
class ProjectRepository(BaseRepository[Project]):
    async def get_by_status(self, status: str) -> list[Project]:
        """Get projects by status with analytics"""
        
    async def get_with_conversations(self, id: int) -> Project:
        """Eager load project with conversations"""
        
    async def search_by_name(self, query: str) -> list[Project]:
        """Full-text search using DuckDB capabilities"""
        
    async def analytics_summary(self, 
                               date_range: tuple[datetime, datetime] = None
                               ) -> ProjectAnalytics:
        """Project analytics and metrics"""

# Conversation Repository  
class ConversationRepository(BaseRepository[Conversation]):
    async def get_by_project(self, project_id: int) -> list[Conversation]:
        """Get all conversations for a project"""
        
    async def get_by_phase(self, phase: str) -> list[Conversation]:
        """Get conversations in specific phase"""
        
    async def add_message(self, id: int, message: dict) -> Conversation:
        """Add message to conversation JSON field"""
        
    async def conversation_analytics(self) -> ConversationMetrics:
        """Analytics on conversation patterns"""
```

### 4. Query Builder & Filters

**File**: `src/project_architect_db/queries/builder.py`

Advanced query building with DuckDB optimizations:

```python
class QueryBuilder[T]:
    def __init__(self, model_class: type[T], session: AsyncSession):
        self.model_class = model_class
        self.session = session
        self._query = select(model_class)
    
    def filter(self, **conditions) -> QueryBuilder[T]:
        """Add WHERE conditions"""
        
    def filter_by_date_range(self, 
                            field: str, 
                            start: datetime, 
                            end: datetime) -> QueryBuilder[T]:
        """Date range filtering"""
        
    def filter_json(self, 
                   field: str, 
                   json_path: str, 
                   value: Any) -> QueryBuilder[T]:
        """JSON field filtering using DuckDB JSON functions"""
        
    def order_by(self, *fields) -> QueryBuilder[T]:
        """Ordering with multiple fields"""
        
    def limit(self, count: int) -> QueryBuilder[T]:
        """Result limiting"""
        
    def offset(self, count: int) -> QueryBuilder[T]:
        """Result offset for pagination"""
        
    async def all(self) -> list[T]:
        """Execute and return all results"""
        
    async def first(self) -> T | None:
        """Execute and return first result"""
        
    async def count(self) -> int:
        """Execute count query"""
        
    async def exists(self) -> bool:
        """Check if any records match"""

# Usage examples
projects = await (QueryBuilder(Project, session)
    .filter(status="active")
    .filter_by_date_range("created_at", start_date, end_date)
    .filter_json("architecture", "$.framework", "FastAPI")
    .order_by(Project.created_at.desc())
    .limit(50)
    .all())
```

### 5. Analytics & Aggregations

**File**: `src/project_architect_db/repositories/analytics.py`

Leverages DuckDB's analytical capabilities:

```python
class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def project_metrics(self, 
                             date_range: tuple[datetime, datetime] = None
                             ) -> ProjectMetrics:
        """Comprehensive project analytics"""
        
    async def conversation_flow_analysis(self) -> ConversationFlowMetrics:
        """Analyze conversation patterns and bottlenecks"""
        
    async def document_usage_stats(self) -> DocumentUsageStats:
        """Document creation and access patterns"""
        
    async def repository_health_metrics(self) -> RepositoryHealthMetrics:
        """Repository activity and health indicators"""
        
    async def cross_entity_analytics(self) -> CrossEntityMetrics:
        """Complex analytics across all entities"""
        
    async def time_series_analysis(self, 
                                  metric: str, 
                                  granularity: str = "day"
                                  ) -> TimeSeriesData:
        """Time-based trend analysis"""

# Example analytics queries using DuckDB features
SELECT 
    date_trunc('day', created_at) as date,
    count(*) as project_count,
    avg(json_extract(architecture, '$.complexity_score')) as avg_complexity,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY json_array_length(conversations)) as median_conversations
FROM projects 
WHERE created_at >= $1 
GROUP BY date_trunc('day', created_at)
ORDER BY date;
```

## Data Models & Schemas

### SQLAlchemy Models

Enhanced with async support and DuckDB optimizations:

```python
# Base model with common functionality
class Base(DeclarativeBase):
    type_annotation_map = {
        datetime: DateTime(timezone=True),
        dict: JSON,
        list: JSON,
    }

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())

class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    project_idea: Mapped[str] = mapped_column(Text)
    architecture: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True)
    
    # Relationships
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="project", lazy="selectin"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="project", lazy="selectin"  
    )
    repositories: Mapped[list["Repository"]] = relationship(
        "Repository", back_populates="project", lazy="selectin"
    )
    
    # Indexes for DuckDB optimization
    __table_args__ = (
        Index("idx_project_status_created", "status", "created_at"),
        Index("idx_project_name_search", "name"),
    )
```

### Pydantic Schemas

Type-safe data validation and serialization:

```python
# Base schemas
class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: datetime | None = None

# Project schemas
class ProjectBase(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    project_idea: str = Field(min_length=10, max_length=10000)
    architecture: dict[str, Any] | None = None
    status: str = Field(default="draft", pattern="^(draft|active|completed|archived)$")

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseSchema):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    project_idea: str | None = Field(None, min_length=10, max_length=10000)
    architecture: dict[str, Any] | None = None
    status: str | None = Field(None, pattern="^(draft|active|completed|archived)$")

class Project(ProjectBase, TimestampSchema):
    id: int
    conversations: list["ConversationSummary"] = []
    documents: list["DocumentSummary"] = []
    repositories: list["RepositorySummary"] = []

# Analytics schemas
class ProjectMetrics(BaseSchema):
    total_projects: int
    active_projects: int
    completed_projects: int
    average_completion_time: timedelta | None
    project_by_status: dict[str, int]
    complexity_distribution: dict[str, int]
    top_frameworks: list[tuple[str, int]]
```

## Testing Architecture

### Test Database Management

Isolated DuckDB instances for parallel testing:

```python
# Test database configuration
class TestDatabaseManager:
    def __init__(self, worker_id: str = "main"):
        self.worker_id = worker_id
        self.db_path = f"test_db_{worker_id}_{uuid4().hex[:8]}.duckdb"
        
    async def setup(self):
        """Create isolated test database"""
        self.engine = create_async_engine(f"duckdb:///{self.db_path}")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
    async def teardown(self):
        """Clean up test database"""
        await self.engine.dispose()
        Path(self.db_path).unlink(missing_ok=True)
        
    @asynccontextmanager
    async def session(self) -> AsyncSession:
        """Get test session"""
        async with AsyncSession(self.engine) as session:
            yield session
```

### Test Fixtures & Factories

```python
# Async test fixtures
@pytest_asyncio.fixture
async def db_session(test_db_manager):
    async with test_db_manager.session() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def sample_project(db_session):
    project_data = ProjectFactory.build()
    async with ProjectRepository(db_session) as repo:
        return await repo.create(project_data)

# Data factories
class ProjectFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Project
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Faker("company")
    description = factory.Faker("text", max_nb_chars=200)
    project_idea = factory.Faker("text", max_nb_chars=500)
    architecture = factory.LazyFunction(lambda: {
        "framework": faker.random_element(["FastAPI", "Django", "Flask"]),
        "database": faker.random_element(["PostgreSQL", "DuckDB", "SQLite"]),
        "complexity_score": faker.random_int(1, 10)
    })
    status = factory.Faker("random_element", elements=["draft", "active", "completed"])
```

### Parallel Test Execution

```python
# pytest configuration for parallel execution
def pytest_configure_node(node):
    """Configure each test worker with isolated database"""
    node.workerinput["worker_id"] = node.workerinput.get("workerid", "main")

@pytest.fixture(scope="session")
def worker_id(request):
    """Get worker ID for database isolation"""
    return getattr(request.config, "workerinput", {}).get("worker_id", "main")

@pytest_asyncio.fixture(scope="session")
async def test_db_manager(worker_id):
    """Session-scoped database manager per worker"""
    manager = TestDatabaseManager(worker_id)
    await manager.setup()
    yield manager
    await manager.teardown()
```

## Performance Optimizations

### DuckDB-Specific Optimizations

1. **Analytical Queries**: Leverage columnar storage for analytics
2. **JSON Processing**: Use DuckDB's native JSON functions
3. **Bulk Operations**: Optimized batch inserts using DuckDB's bulk loading
4. **Memory Management**: Efficient memory usage for large datasets
5. **Query Planning**: Optimized query execution plans

### Connection Pooling

```python
# Optimized connection pool configuration
engine = create_async_engine(
    database_url,
    pool_size=20,           # Base pool size
    max_overflow=30,        # Additional connections under load
    pool_timeout=30,        # Connection timeout
    pool_recycle=3600,      # Recycle connections hourly
    pool_pre_ping=True,     # Validate connections
    query_cache_size=1200,  # Query plan cache
    connect_args={
        "pragma": "threads=4",    # DuckDB thread configuration
        "memory_limit": "2GB",    # Memory limit
        "temp_directory": "/tmp/duckdb_temp"
    }
)
```

### Bulk Operations

```python
# High-performance bulk operations
class BulkOperations:
    @staticmethod
    async def bulk_insert_projects(session: AsyncSession, 
                                  projects: list[dict]) -> list[Project]:
        """Optimized bulk insert using DuckDB capabilities"""
        
    @staticmethod  
    async def bulk_update_status(session: AsyncSession,
                               project_ids: list[int],
                               status: str) -> int:
        """Bulk status updates"""
        
    @staticmethod
    async def bulk_analytics_refresh(session: AsyncSession) -> None:
        """Refresh materialized analytics views"""
```

This architecture provides a solid foundation for a high-performance, async-first database library that leverages DuckDB's analytical capabilities while maintaining type safety and comprehensive testing.