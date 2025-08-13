# Contributing to Andamios ORM

Thank you for your interest in contributing to Andamios ORM! This document outlines our development process and guidelines.

## 🎯 Development Philosophy

We follow a strict **Example-Driven Development (EDD) → Test-Driven Development (TDD)** approach:

1. **Phase 1 - Examples**: Create practical, executable examples
2. **Phase 2 - Tests**: Write comprehensive tests based on examples
3. **Phase 3 - Implementation**: Implement functionality to make tests pass
4. **Phase 4 - Optimization**: Optimize performance and update documentation

## 🚀 Quick Start

### Prerequisites

- Python 3.12+ (optimized for Python 3.12)
- Poetry for dependency management
- Git
- Docker (required for test database containers)
- DuckDB 0.9.0+ (automatically installed with andamios-orm)
- uvloop 0.19.0+ (for high-performance async operations)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/andamios/andamios-orm.git
cd andamios-orm

# Run the setup script
./scripts/dev-setup.sh

# Or manually:
poetry install --with dev,performance
poetry run pre-commit install
```

## 📋 Development Workflow

### 1. Choose an Issue

We organize work through GitHub issues with specific labels:

- 🌟 **Examples** (`examples`, `phase-1`) - Create usage examples
- 🧪 **Tests** (`tests`, `phase-2`) - Write comprehensive tests
- ⚙️ **Implementation** (`implementation`, `phase-3`) - Implement functionality
- 🔧 **Optimization** (`optimization`, `phase-4`) - Performance improvements

**Start with `good-first-issue` labels if you're new to the project.**

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-fix-name
```

### 3. Follow the Development Process

#### For Examples (Phase 1)
- Create in `examples/[category]/`
- Make them executable and self-contained
- Include comprehensive docstrings
- Use realistic data and scenarios
- Follow async-first patterns

#### For Tests (Phase 2)
- Create in `tests/[category]/`
- Use real DuckDB instances (no mocks)
- Achieve 100% code coverage
- Support parallel execution
- Test error conditions and edge cases

#### For Implementation (Phase 3)
- Create in `src/andamios_orm/[component]/`
- Make all corresponding tests pass
- Use full type annotations
- Follow async-first design patterns
- Meet performance requirements

### 4. Quality Checks

Before committing, ensure all quality checks pass:

```bash
# Run all quality checks
poetry run pre-commit run --all-files

# Individual checks
poetry run pytest                    # All tests
poetry run mypy src/                # Type checking
poetry run ruff check src/          # Linting
poetry run ruff format src/         # Formatting
```

### 5. Commit and Push

```bash
git add .
git commit -m "feat: your descriptive commit message"
git push origin feature/your-feature-name
```

### 6. Create Pull Request

- Use the PR template
- Link to the related issue
- Ensure CI passes
- Request review from maintainers

## 🧪 Testing Guidelines

### Real Database Testing

**We use real DuckDB instances for all database tests. No mocking allowed.**

```python
# ✅ Good - uses real database
async def test_user_creation(session):
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    await session.commit()
    
    result = await session.get(User, user.id)
    assert result.name == "Alice"

# ❌ Bad - uses mocks
@patch('andamios_orm.session.execute')
async def test_user_creation(mock_execute):
    # Don't do this!
```

### Test Structure

```bash
tests/
├── conftest.py              # Test configuration and fixtures
├── factories.py             # Test data factories
├── unit/                    # Unit tests (isolated components)
├── integration/             # Integration tests (with database)
├── e2e/                     # End-to-end tests (complete workflows)
└── examples/                # Tests for examples
```

### Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test with real database operations
- **E2E Tests**: Test complete workflows
- **Performance Tests**: Benchmark critical operations

### Coverage Requirements

- **100% line coverage** required
- **100% branch coverage** for complex logic
- All public API methods must be tested
- All error conditions must be tested

## 📝 Code Style Guidelines

### General Principles

- **Async-first**: All database operations must be async
- **Type safety**: Full type annotations required
- **Performance**: Optimize for DuckDB's columnar architecture
- **Documentation**: Clear docstrings for all public APIs

### Code Formatting

We use automated formatting tools:

- **Ruff**: Linting and formatting
- **Black**: Code formatting (integrated with Ruff)
- **isort**: Import sorting (integrated with Ruff)

### Type Annotations

```python
# ✅ Good - complete type annotations
async def create_user(
    session: AsyncSession,
    name: str,
    email: str
) -> User:
    """Create a new user with the given details."""
    user = User(name=name, email=email)
    session.add(user)
    await session.commit()
    return user

# ❌ Bad - missing type annotations
async def create_user(session, name, email):
    user = User(name=name, email=email)
    session.add(user)
    await session.commit()
    return user
```

### Error Handling

```python
# ✅ Good - comprehensive error handling
async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Get user by email address."""
    try:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching user: {e}")
        raise DatabaseError(f"Failed to fetch user with email {email}") from e
    except Exception as e:
        logger.error(f"Unexpected error while fetching user: {e}")
        raise
```

## 📚 Documentation Guidelines

### Docstring Format

We use Google-style docstrings:

```python
async def create_user_with_orders(
    session: AsyncSession,
    user_data: dict,
    orders: list[dict]
) -> tuple[User, list[Order]]:
    """
    Create a user with associated orders in a single transaction.
    
    This function demonstrates transaction management and bulk operations
    for optimal performance with DuckDB's columnar storage.
    
    Args:
        session: Database session for the transaction
        user_data: User information dictionary with name and email
        orders: List of order dictionaries with order details
        
    Returns:
        Tuple of created user and list of created orders
        
    Raises:
        ValidationError: If user_data or orders contain invalid data
        DatabaseError: If database operation fails
        
    Example:
        ```python
        async with SessionLocal() as session:
            user_data = {"name": "Alice", "email": "alice@example.com"}
            orders = [{"product": "Widget", "quantity": 5}]
            
            user, orders = await create_user_with_orders(
                session, user_data, orders
            )
        ```
    """
```

### Example Documentation

All examples must include:

```python
"""
Example NN: [Title]

This example demonstrates how to:
- [Key concept 1]
- [Key concept 2]
- [Key concept 3]

Expected behavior:
- [What should happen when run]
- [Performance characteristics]
- [Error conditions handled]

Performance targets:
- Operation time: < Xms
- Memory usage: < XMB
- Database operations: X queries

Prerequisites:
- [Any setup required]
- [Dependencies needed]
"""
```

## 🔍 Code Review Process

### Pull Request Requirements

- [ ] All tests pass
- [ ] Code coverage at 100%
- [ ] Type checking passes (mypy)
- [ ] Linting passes (ruff)
- [ ] Examples are executable
- [ ] Documentation is updated
- [ ] Performance targets met

### Review Checklist

Reviewers will check for:

- **Correctness**: Does the code do what it's supposed to do?
- **Testing**: Are there comprehensive tests with real databases?
- **Performance**: Does it meet performance requirements?
- **Type Safety**: Are there complete type annotations?
- **Documentation**: Is the code well-documented?
- **Architecture**: Does it fit the overall design?

## 📊 Performance Requirements

### Response Time Targets

- **Simple queries**: < 1ms
- **Complex queries**: < 10ms
- **Bulk operations**: < 100ms for 10,000 records
- **Connection acquisition**: < 5ms

### Memory Usage

- **Base footprint**: < 100MB
- **Per connection**: < 1MB
- **Query overhead**: < 100KB per query

### Benchmarking

Include performance tests for new features:

```python
@pytest.mark.performance
async def test_bulk_insert_performance(session, performance_monitor):
    """Test bulk insert performance meets targets."""
    users = [UserFactory.build() for _ in range(10000)]
    
    with performance_monitor.measure("bulk_insert"):
        session.add_all(users)
        await session.commit()
    
    measurements = performance_monitor.get_measurements()
    assert measurements["bulk_insert"] < 0.1  # < 100ms
```

## 🐛 Bug Reports

When reporting bugs:

1. **Use the bug report template**
2. **Include minimal reproduction example**
3. **Specify Python version and dependencies**
4. **Include full error traceback**
5. **Describe expected vs actual behavior**

## 💡 Feature Requests

When requesting features:

1. **Use the feature request template**
2. **Explain the use case and motivation**
3. **Provide example code showing desired API**
4. **Consider performance implications**
5. **Think about testing strategy**

## 🏷️ Issue Labels

### Phase Labels
- `phase-1` - Example-Driven Development
- `phase-2` - Test-Driven Development
- `phase-3` - Implementation
- `phase-4` - Optimization & Documentation

### Component Labels
- `core` - Engine, connection, session management
- `models` - Model system and field types
- `repository` - Repository pattern
- `queries` - Query building
- `migrations` - Database migrations
- `testing` - Testing utilities

### Priority Labels
- `high-priority` - Critical features
- `medium-priority` - Important features
- `low-priority` - Nice-to-have features
- `good-first-issue` - Good for new contributors

## 🎖️ Recognition

Contributors will be recognized in:

- GitHub contributors list
- Release notes for significant contributions
- Documentation acknowledgments
- Project README

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check docs/ directory
- **Examples**: Look at examples/ directory

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Andamios ORM! 🚀