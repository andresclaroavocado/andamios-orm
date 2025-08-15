# Basic Examples

Simple CRUD examples with clean factory pattern and real ORM functionality.

## Examples

### 🚀 Project CRUD
```bash
python project_crud.py
```

SQLAlchemy model with clean factory pattern:
```python
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    
    @classmethod
    def create(cls, id: int, name: str):
        return cls(id=id, name=name)

# Usage - works with real DuckDB
project = Project.create(id=1, name="MyWebApp")
session.add(project)
await session.commit()
```

### 📁 Repository CRUD
```bash
python repository_crud.py
```

Same pattern for Repository with actual database operations:
```python
class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    
    @classmethod
    def create(cls, id: int, name: str):
        return cls(id=id, name=name)

# Usage - persists to DuckDB
repo = Repository.create(id=1, name="MyProject")
```

## Implementation Details

✅ **Simple Factory Pattern:**
- Clean `create()` class method
- Clear `__repr__` methods
- Basic CRUD operations
- Minimal complexity

✅ **Real ORM Integration:**
- SQLAlchemy models with `Base`
- Actual database table creation
- Real CRUD operations with DuckDB
- Proper async/await with sessions

**Result:** Simple examples with working ORM functionality!