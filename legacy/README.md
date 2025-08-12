# Project Architect DB

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![DuckDB](https://img.shields.io/badge/database-DuckDB-orange.svg)](https://duckdb.org/)
[![Async](https://img.shields.io/badge/async-uvloop-green.svg)](https://github.com/MagicStack/uvloop)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Modern, async-first Python database library for project management and architecture systems. Built specifically for the Web-Based Project Architect platform using DuckDB for high-performance analytical queries.

## 🚀 Features

- **Async-First**: Built on uvloop for maximum performance
- **DuckDB Optimized**: Leverages analytical capabilities for complex queries
- **Type-Safe**: Full SQLAlchemy 2.0+ and Pydantic v2 integration
- **100% Test Coverage**: Real database testing, no mocks
- **Parallel Testing**: Isolated databases per test worker
- **Example-Driven**: Comprehensive examples for all features
- **Production-Ready**: CI/CD, monitoring, and security built-in

## 🏗️ Architecture

### Core Models
- **Project**: Software project management with architecture tracking
- **Conversation**: Multi-phase conversation and workflow management  
- **Document**: Document and specification management
- **Repository**: Code repository tracking and analytics

### Repository Pattern
- Generic base repository with async CRUD operations
- Specialized repositories with domain-specific logic
- Advanced query builder with DuckDB optimization
- Cross-entity analytics and reporting

## 📋 Development Status

This project follows **Example-Driven Development** followed by **Test-Driven Development**. 

### Development Phases

- [ ] **Phase 1**: Core Foundation (Setup, Engine, Models)
- [ ] **Phase 2**: Repository Pattern (Base & Specialized Repos, Query Builder)
- [ ] **Phase 3**: Analytics (Advanced Analytics, CLI Tools)
- [ ] **Phase 4**: Testing (100% Coverage, Performance Benchmarks)
- [ ] **Phase 5**: Integration (Examples, FastAPI, Real-time)
- [ ] **Phase 6**: Release (Documentation, CI/CD, Security)

See [GITHUB_ISSUES.md](GITHUB_ISSUES.md) for detailed development roadmap with 16 comprehensive issues.

## 📖 Documentation

- [**CLAUDE.md**](CLAUDE.md) - Complete project specifications and requirements
- [**ARCHITECTURE.md**](ARCHITECTURE.md) - Detailed technical architecture
- [**TEST_CONFIGURATION.md**](TEST_CONFIGURATION.md) - Testing strategy and setup
- [**EXAMPLES_STRUCTURE.md**](EXAMPLES_STRUCTURE.md) - Example-driven development framework
- [**GITHUB_ISSUES.md**](GITHUB_ISSUES.md) - Development roadmap and issues

## 🛠️ Quick Start (Coming Soon)

```python
# Example usage (implementation coming in Phase 1-2)
from project_architect_db import DatabaseEngine, ProjectRepository
from project_architect_db.schemas import ProjectCreate

async def main():
    engine = DatabaseEngine("duckdb:///projects.db")
    
    async with engine.session() as session:
        async with ProjectRepository(session) as repo:
            project = await repo.create(ProjectCreate(
                name="My Project",
                description="A cool project",
                project_idea="Build something awesome"
            ))
            
            print(f"Created project: {project.name}")

# More examples coming in examples/ directory
```

## 🧪 Testing (Coming Soon)

```bash
# Install dependencies
poetry install

# Run tests in parallel with real DuckDB
poetry run pytest -n auto --cov=src/project_architect_db

# Run performance benchmarks
poetry run pytest tests/performance/ --benchmark-only
```

## 🤝 Contributing

1. Check out the [development issues](https://github.com/YOUR_USERNAME/project-architect-db/issues)
2. Start with Phase 1 issues for core foundation
3. Follow example-driven → test-driven development
4. Ensure 100% test coverage with real databases
5. Meet performance benchmarks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [DuckDB](https://duckdb.org/) for analytical performance
- Powered by [SQLAlchemy 2.0+](https://www.sqlalchemy.org/) for async ORM
- Enhanced with [Pydantic v2](https://pydantic.dev/) for validation
- Optimized with [uvloop](https://github.com/MagicStack/uvloop) for async performance

---

**Status**: 📋 Planning Phase - Ready for Development

See [GITHUB_ISSUES.md](GITHUB_ISSUES.md) for the complete development roadmap.