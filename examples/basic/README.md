# Basic Examples

Simple CRUD examples just like boss wanted - following Grok's pattern.

## Examples

### 🚀 Project CRUD
```bash
python project_crud.py
```

Simple Project class with `create()` method:
```python
class Project:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
    
    @classmethod
    def create(cls, id: int, name: str):
        return cls(id=id, name=name)

# Usage
project = Project.create(id=1, name="MyWebApp")
```

### 📁 Repository CRUD
```bash
python repository_crud.py
```

Same pattern for Repository:
```python
class Repository:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
    
    @classmethod
    def create(cls, id: int, name: str):
        return cls(id=id, name=name)

# Usage  
repo = Repository.create(id=1, name="MyProject")
```

## Pattern

All examples follow the same simple pattern from Grok:
1. Simple class with `__init__` and `__repr__`
2. Class method `create()` for instantiation  
3. Basic CRUD operations in async functions
4. No complex ORM features

Just like boss wanted - **simple examples, no over-engineering!**