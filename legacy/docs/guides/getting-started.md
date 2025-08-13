# Getting Started with Andamios ORM

## Overview

Andamios ORM is an async-first Python ORM built on DuckDB and SQLAlchemy 2.0+. This guide will walk you through the basics of setting up and using the library.

## Installation

```bash
pip install andamios-orm
# or with poetry
poetry add andamios-orm
```

## Quick Start

### 1. Basic Setup

```python
import asyncio
from andamios_orm import create_engine, sessionmaker, Base

# Create async engine
engine = create_engine("duckdb:///example.db")
SessionLocal = sessionmaker(engine)

# Define a model
class User(Base):
    __tablename__ = "users"
    
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100), nullable=False)
    email: str = Column(String(255), unique=True)
```

### 2. Basic Operations

```python
async def main():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with SessionLocal() as session:
        # Create user
        user = User(name="John Doe", email="john@example.com")
        session.add(user)
        await session.commit()
        
        # Query users
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        print(f"Found {len(users)} users")

# Run with uvloop for best performance
import uvloop
uvloop.run(main())
```

## Key Concepts

### Async-First Design

Andamios ORM is built for async operations from the ground up:

```python
# All database operations are async
async with SessionLocal() as session:
    user = await session.get(User, 1)
    users = await session.execute(select(User).where(User.name.like("John%")))
    await session.commit()
```

### Repository Pattern

Use repositories for clean data access:

```python
from andamios_orm.repositories import BaseRepository

class UserRepository(BaseRepository[User]):
    async def find_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

# Usage
async with SessionLocal() as session:
    user_repo = UserRepository(session)
    user = await user_repo.find_by_email("john@example.com")
```

### Query Builder

Build complex queries fluently:

```python
from andamios_orm.queries import QueryBuilder

# Complex query with builder
query = (QueryBuilder(User)
    .where(User.name.like("John%"))
    .order_by(User.created_at.desc())
    .limit(10))

async with SessionLocal() as session:
    users = await query.execute(session)
```

## Next Steps

- Read the [API Documentation](../api/) for complete reference
- Check out [Examples](../examples/) for real-world patterns
- Learn about [Testing](./testing.md) with real databases
- Explore [Performance](./performance.md) optimization

## Best Practices

1. **Always use async**: Never mix sync and async operations
2. **Use uvloop**: Set uvloop as your event loop for best performance
3. **Repository pattern**: Organize data access with repositories
4. **Type hints**: Use full type annotations for better IDE support
5. **Real testing**: Test with actual DuckDB instances, not mocks