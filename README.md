# Andamios ORM

A modern, async-first Python ORM library built specifically for DuckDB. Designed for high-performance analytical workloads with uvloop optimization and 100% test coverage.

## 🚀 Features

- **DuckDB Optimized**: Built specifically for DuckDB 1.1+ columnar architecture
- **Async + uvloop**: Full async/await support with uvloop for maximum performance
- **SQLAlchemy 2.0+**: Built on SQLAlchemy 2.0.35+ for modern database operations
- **Type Safety**: Full type hints with mypy strict mode support
- **100% Coverage**: Mandatory 100% test coverage with parallel testing
- **Real Database Testing**: Uses actual DuckDB instances, no mocking

## 📋 Prerequisites

- **Python**: 3.13+
- **DuckDB**: 1.1.0+
- **SQLAlchemy**: 2.0.35+
- **uvloop**: 0.20.0+
- **Poetry**: Latest version for dependency management

## 📦 Installation

Using Poetry (recommended):

```bash
poetry add andamios-orm
```

Using pip:

```bash
pip install andamios-orm
```

## 🏗️ Project Structure

```
andamios-orm/
├── andamios_orm/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py              # Base model classes
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── base.py              # Repository pattern implementation
│   ├── scripts/
│   │   ├── __init__.py
│   │   └── cli.py               # CLI tools
│   └── migration/
│       ├── __init__.py
│       └── ...                  # Migration utilities
├── alembic/
│   ├── versions/                # Migration files
│   ├── env.py
│   └── script.py.mako
├── docs/                        # Documentation
├── examples/
│   ├── basic/                   # Basic usage examples
│   └── advanced/                # Advanced usage examples
├── tests/
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── alembic.ini                  # Alembic configuration
└── pyproject.toml              # Poetry configuration
```

## 🔧 Quick Start

```python
import asyncio
import uvloop
from andamios_orm import create_memory_engine, sessionmaker, AsyncSession

# Import your models (example using legacy database models)
from legacy.database.models import Base, Project

async def main():
    # Create DuckDB engine (optimized with uvloop)
    engine = create_memory_engine(echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Use the ORM
    async with SessionLocal() as session:
        # Create object in memory
        project = Project(
            name="My Project",
            project_idea="Build something awesome"
        )
        
        # Save to DuckDB
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        print(f"Project created with ID: {project.id}")
    
    await engine.dispose()

if __name__ == "__main__":
    uvloop.run(main())
```

## 🧪 Development

### Prerequisites

- Python 3.8+
- Poetry
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/andresclaroavocado/andamios-orm.git
cd andamios-orm
```

2. Install dependencies:
```bash
poetry install
```

3. Install pre-commit hooks:
```bash
poetry run pre-commit install
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=andamios_orm

# Run only unit tests
poetry run pytest tests/unit/

# Run only integration tests
poetry run pytest tests/integration/
```

### Code Quality

```bash
# Format code
poetry run black andamios_orm tests

# Sort imports
poetry run isort andamios_orm tests

# Lint code
poetry run flake8 andamios_orm tests

# Type checking
poetry run mypy andamios_orm
```

## 🗺️ Roadmap

- [ ] **Phase 1**: Core ORM Implementation
  - [ ] Base model classes
  - [ ] Repository pattern
  - [ ] Basic CRUD operations
  
- [ ] **Phase 2**: Advanced Features
  - [ ] Relationship handling
  - [ ] Query builders
  - [ ] Connection pooling
  
- [ ] **Phase 3**: Integration & Ecosystem
  - [ ] Advanced DuckDB features
  - [ ] Andamios ecosystem integration
  - [ ] Performance optimizations

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to the main branch.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- **andamios-llm**: LLM integration library
- **andamios-api**: API framework and utilities
- More Andamios libraries coming soon!

## 📞 Support

- Create an issue on GitHub for bug reports
- Start a discussion for questions and feature requests
- Email: adnres.claro@avocadoblock.com

---

*This project is currently in early development. The API is subject to change.*