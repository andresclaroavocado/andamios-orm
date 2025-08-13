# Andamios ORM

[![CI](https://github.com/andamios/andamios-orm/workflows/CI/badge.svg)](https://github.com/andamios/andamios-orm/actions)
[![codecov](https://codecov.io/gh/andamios/andamios-orm/branch/main/graph/badge.svg)](https://codecov.io/gh/andamios/andamios-orm)
[![PyPI version](https://badge.fury.io/py/andamios-orm.svg)](https://badge.fury.io/py/andamios-orm)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, async-first Python ORM library built on DuckDB and SQLAlchemy 2.0+. Designed for high-performance analytical workloads with a focus on Example-Driven Development and 100% test coverage.

## 🚀 Features

- **Async-First**: Built from the ground up for async/await patterns with uvloop
- **DuckDB Integration**: Optimized for DuckDB's columnar architecture and analytical capabilities
- **Type Safe**: Full type annotations with mypy strict mode compliance
- **Example-Driven**: Comprehensive examples that serve as living documentation
- **Real Database Testing**: 100% test coverage using actual DuckDB instances, no mocks
- **High Performance**: Optimized for analytical workloads and bulk operations
- **Modern Python**: Supports Python 3.8+ with compatible dependency versions

## 📋 Quick Start

### Installation

```bash
pip install andamios-orm
# or with poetry
poetry add andamios-orm
```

### Basic Usage

```python
import asyncio
import uvloop
from andamios_orm import create_engine, sessionmaker, Base, Column, Integer, String

# Define a model
class User(Base):
    __tablename__ = "users"
    
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100), nullable=False)
    email: str = Column(String(255), unique=True)

async def main():
    # Create engine and session
    engine = create_engine("duckdb:///example.db")
    SessionLocal = sessionmaker(engine)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Use the ORM
    async with SessionLocal() as session:
        user = User(name="Alice", email="alice@example.com")
        session.add(user)
        await session.commit()
        
        # Query users
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"Found {len(users)} users")

# Run with uvloop for best performance
uvloop.run(main())
```

## 🏗️ Architecture

Andamios ORM follows a layered architecture optimized for DuckDB:

- **Core Layer**: Engine, session, and connection management
- **Models Layer**: Base models, field types, and validation
- **Repository Layer**: Data access patterns and transaction management
- **Query Layer**: Fluent query building and optimization
- **Migration Layer**: Schema evolution and version control

## 📚 Documentation

- **[Getting Started Guide](docs/guides/getting-started.md)** - Learn the basics
- **[Examples](examples/)** - Practical, executable examples
- **[API Reference](docs/api/)** - Complete API documentation
- **[Architecture](ARCHITECTURE.md)** - System design and technical decisions

## 🧪 Development Philosophy

### Example-Driven Development (EDD) → Test-Driven Development (TDD)

1. **Phase 1 - Examples**: Create practical, executable examples
2. **Phase 2 - Tests**: Write comprehensive tests based on examples
3. **Phase 3 - Implementation**: Implement functionality to pass tests
4. **Phase 4 - Optimization**: Optimize performance and update docs

### Real Database Testing

- All tests use actual DuckDB instances
- No mocking of database operations
- Parallel test execution with isolated databases
- 100% test coverage requirement

## 🔧 Development Setup

### Prerequisites

- Python 3.8+ (supports all modern Python versions)
- Poetry for dependency management
- Git with pre-commit hooks
- Docker (for test database containers)
- DuckDB 0.8.0+ (automatically installed with andamios-orm)

### Setup

```bash
# Clone the repository
git clone https://github.com/andamios/andamios-orm.git
cd andamios-orm

# Install dependencies
poetry install

# Set up pre-commit hooks
poetry run pre-commit install

# Run tests
poetry run pytest

# Run examples
cd examples/basic
python 01_connection.py
```

### Development Commands

```bash
# Testing
poetry run pytest                    # Run all tests
poetry run pytest -n auto          # Run tests in parallel
poetry run pytest --cov-report=html # Generate coverage report

# Code quality
poetry run mypy src/                # Type checking
poetry run ruff check src/          # Linting
poetry run ruff format src/         # Formatting
poetry run pre-commit run --all-files # All quality checks

# Performance
poetry run pytest -m performance    # Run performance tests
```

## 📊 Performance Targets

- **Simple queries**: < 1ms
- **Complex queries**: < 10ms
- **Bulk operations**: < 100ms for 10,000 records
- **Connection acquisition**: < 5ms
- **Memory usage**: < 100MB base footprint

## 🤝 Contributing

We follow a structured development process:

1. **Start with examples** - Create practical usage examples
2. **Write tests** - Comprehensive tests based on examples
3. **Implement** - Make tests pass with clean code
4. **Document** - Update docs and guides

See our [Contributing Guide](CONTRIBUTING.md) for detailed information.

### Issue Types

- 🌟 **Examples** - Create new usage examples
- 🧪 **Tests** - Write tests for functionality
- ⚙️ **Implementation** - Implement core features
- 🔧 **Optimization** - Performance improvements
- 📚 **Documentation** - Update guides and API docs

## 📈 Project Status

**Current Phase**: Foundation Development

- [x] Project structure and documentation
- [x] Example framework setup
- [x] Testing infrastructure with real databases
- [x] CI/CD pipeline with quality gates
- [ ] Core engine implementation
- [ ] Model system implementation
- [ ] Repository pattern implementation
- [ ] Query builder implementation
- [ ] Migration system implementation

## 🔗 Related Projects

- [SQLAlchemy](https://sqlalchemy.org/) - ORM foundation
- [DuckDB](https://duckdb.org/) - Analytical database engine
- [uvloop](https://github.com/MagicStack/uvloop) - High-performance event loop
- [Pydantic](https://pydantic.dev/) - Data validation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- SQLAlchemy team for the excellent ORM foundation
- DuckDB team for the high-performance analytical database
- Python async community for async/await patterns
- All contributors who help make this project better

---

**Built with ❤️ by the Andamios Team**