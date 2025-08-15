# Basic Examples

## 🎯 Minimal Examples (Start Here!)

These follow the principle of "simplest possible" - no session management, no async complexity.

### Ultra Simple CREATE
```bash
python minimal_example.py
```

**The simplest possible example** (addresses all complexity concerns):
```python
from sqlalchemy import Column, String
from andamios_orm import SimpleModel, save, create_tables

class Repository(SimpleModel):
    __tablename__ = "repositories"
    name = Column(String(255), nullable=False)

# Setup (one line)
create_tables()

# Use (two lines) 
repo = Repository(name="backend-api")
saved_repo = save(repo)

print(f"Created repository: {saved_repo.name} (ID: {saved_repo.id})")
```

### Simple Operations
```bash
python simple_create.py  # CREATE operation
python simple_read.py    # READ operations
```

## 🔧 Advanced Examples

For users who need more control over sessions and async operations:

```bash
python project_crud.py    # Full CRUD with session management
python repository_crud.py # Complete example with all operations
```

## Key Differences

**✅ Simple API (Recommended for examples):**
- No session management visible
- No async/await complexity
- Focus on single operations
- Self-contained models
- Minimal setup: `create_tables()`
- Simple functions: `save()`, `find_by_id()`, `find_all()`

**🔧 Advanced API (For production use):**
- Full session control
- Async/await for performance
- Complete CRUD operations
- External model references
- Manual engine/session setup

**Use Simple API for learning and demos, Advanced API for real applications.**