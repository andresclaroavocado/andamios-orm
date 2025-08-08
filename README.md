# Andamios ORM

A Python ORM library for database interactions, designed to be part of the broader Andamios ecosystem alongside andamios-llm, andamios-api, and other related libraries.

## 🚀 Features

- **SQLAlchemy Integration**: Built on top of SQLAlchemy 2.0 for robust database operations
- **Async Support**: Full async/await support for modern Python applications
- **Repository Pattern**: Clean repository pattern implementation for data access
- **Migration Support**: Alembic integration for database schema migrations
- **Multiple Database Support**: PostgreSQL, MongoDB, Redis, and more
- **FastAPI Integration**: Optional FastAPI integration for web applications
- **Type Safety**: Full type hints and mypy support
- **Extensible**: Designed to work seamlessly with other Andamios libraries

## 📦 Installation

Using Poetry (recommended):

```bash
# Basic installation
poetry add andamios-orm

# With PostgreSQL support
poetry add andamios-orm[postgresql]

# With MongoDB support
poetry add andamios-orm[mongodb]

# With FastAPI integration
poetry add andamios-orm[fastapi]

# With all optional dependencies
poetry add andamios-orm[all]
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

*Note: Actual implementation coming soon. This is the initial project structure.*

```python
# TODO: Add quick start example when implementation is ready
from andamios_orm import Model, Repository

# Example model definition (placeholder)
class User(Model):
    pass

# Example repository usage (placeholder)
class UserRepository(Repository[User]):
    pass
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
  - [ ] FastAPI integration
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