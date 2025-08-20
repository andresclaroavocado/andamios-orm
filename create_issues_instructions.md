# Instructions to Create GitHub Issues

Since GitHub CLI is not available and I don't have API authentication, please create these issues manually at:

**https://github.com/andresclaroavocado/andamios-orm/issues/new**

## Issue 1: Implement Project model with async CRUD operations

**Copy this title:**
```
Implement Project model with async CRUD operations
```

**Copy this body:**
```markdown
## Summary
Implement the Project model class with async CRUD operations to support the project_crud.py example.

## Requirements

### Model Definition
- [ ] Create Project model class with SQLAlchemy ORM mapping
- [ ] Fields: id (primary key), name, description, project_idea, status, timestamps
- [ ] Proper type hints and async support

### Async CRUD Methods
- [ ] `Project.create(**kwargs)` - Create new project instance
- [ ] `Project.read(id)` - Retrieve project by ID (returns None if not found)
- [ ] `Project.update(id, **kwargs)` - Update existing project
- [ ] `Project.delete(id)` - Delete project by ID

### Database Integration
- [ ] Proper SQLAlchemy table definition
- [ ] Database session management
- [ ] Connection handling with DuckDB

### Expected Behavior
The implementation should make this example work:
```python
from andamios_orm import Project

# CREATE
project = await Project.create(
    name="My Web App",
    description="A task management system", 
    project_idea="Build a productivity tool",
    status="draft"
)

# READ  
found = await Project.read(project.id)

# UPDATE
updated = await Project.update(project.id, name="Updated Web App", status="active")

# DELETE
await Project.delete(project.id)
gone = await Project.read(project.id)  # Should return None
```

## Acceptance Criteria
- [ ] Project model is importable from `andamios_orm`
- [ ] All CRUD operations work asynchronously
- [ ] Returns proper instances with correct data
- [ ] DELETE followed by READ returns None
- [ ] Compatible with DuckDB and uvloop
```

---

## Issue 2: Implement Conversation model with async CRUD operations

**Copy this title:**
```
Implement Conversation model with async CRUD operations
```

**Copy this body:**
```markdown
## Summary
Implement the Conversation model class with async CRUD operations to support the conversation_crud.py example.

## Requirements

### Model Definition
- [ ] Create Conversation model class with SQLAlchemy ORM mapping
- [ ] Fields: id (primary key), project_id (foreign key), phase, messages (JSON), timestamps
- [ ] Proper type hints and async support
- [ ] JSON field handling for messages array

### Async CRUD Methods
- [ ] `Conversation.create(**kwargs)` - Create new conversation instance
- [ ] `Conversation.read(id)` - Retrieve conversation by ID (returns None if not found)
- [ ] `Conversation.update(id, **kwargs)` - Update existing conversation
- [ ] `Conversation.delete(id)` - Delete conversation by ID

### Database Integration
- [ ] Proper SQLAlchemy table definition with JSON column support
- [ ] Database session management
- [ ] Connection handling with DuckDB
- [ ] Foreign key relationship to Project model

### Expected Behavior
The implementation should make this example work:
```python
from andamios_orm import Conversation

# CREATE
convo = await Conversation.create(
    project_id=1,
    phase="requirements",
    messages=[
        {"role": "user", "content": "Let's start building"},
        {"role": "assistant", "content": "Great! What's your project idea?"}
    ]
)

# READ
found = await Conversation.read(convo.id)

# UPDATE
updated = await Conversation.update(
    convo.id,
    phase="design", 
    messages=found.messages + [{"role": "user", "content": "Design the architecture"}]
)

# DELETE
await Conversation.delete(convo.id)
gone = await Conversation.read(convo.id)  # Should return None
```

## Acceptance Criteria
- [ ] Conversation model is importable from `andamios_orm`
- [ ] All CRUD operations work asynchronously
- [ ] JSON messages field works correctly
- [ ] Foreign key relationship with Project works
- [ ] DELETE followed by READ returns None
- [ ] Compatible with DuckDB and uvloop
```

---

## Issue 3: Implement Document model with async CRUD operations

**Copy this title:**
```
Implement Document model with async CRUD operations
```

**Copy this body:**
```markdown
## Summary
Implement the Document model class with async CRUD operations to support the document_crud.py example.

## Requirements

### Model Definition
- [ ] Create Document model class with SQLAlchemy ORM mapping
- [ ] Fields: id (primary key), project_id (foreign key), name, content, doc_type, file_path, timestamps
- [ ] Proper type hints and async support
- [ ] Support for large text content

### Async CRUD Methods
- [ ] `Document.create(**kwargs)` - Create new document instance
- [ ] `Document.read(id)` - Retrieve document by ID (returns None if not found)
- [ ] `Document.update(id, **kwargs)` - Update existing document
- [ ] `Document.delete(id)` - Delete document by ID

### Database Integration
- [ ] Proper SQLAlchemy table definition
- [ ] Database session management
- [ ] Connection handling with DuckDB
- [ ] Foreign key relationship to Project model

### Expected Behavior
The implementation should make this example work:
```python
from andamios_orm import Document

# CREATE
doc = await Document.create(
    project_id=1,
    name="API Documentation",
    content="# API Specification\n\nThis document describes the REST API endpoints...",
    doc_type="api_spec",
    file_path="/docs/api-spec.md"
)

# READ
found = await Document.read(doc.id)

# UPDATE
updated = await Document.update(
    doc.id,
    name="Complete API Documentation",
    doc_type="complete_api_spec",
    content="# Complete API Specification\n\nThis comprehensive document..."
)

# DELETE
await Document.delete(doc.id)
gone = await Document.read(doc.id)  # Should return None
```

## Acceptance Criteria
- [ ] Document model is importable from `andamios_orm`
- [ ] All CRUD operations work asynchronously
- [ ] Large text content handling works
- [ ] Foreign key relationship with Project works
- [ ] DELETE followed by READ returns None
- [ ] Compatible with DuckDB and uvloop
```

---

## Issue 4: Implement Repository model with async CRUD operations

**Copy this title:**
```
Implement Repository model with async CRUD operations
```

**Copy this body:**
```markdown
## Summary
Implement the Repository model class with async CRUD operations to support the repository_crud.py example.

## Requirements

### Model Definition
- [ ] Create Repository model class with SQLAlchemy ORM mapping
- [ ] Fields: id (primary key), project_id (foreign key), name, description, repo_type, github_url, timestamps
- [ ] Proper type hints and async support

### Async CRUD Methods
- [ ] `Repository.create(**kwargs)` - Create new repository instance
- [ ] `Repository.read(id)` - Retrieve repository by ID (returns None if not found)
- [ ] `Repository.update(id, **kwargs)` - Update existing repository
- [ ] `Repository.delete(id)` - Delete repository by ID

### Database Integration
- [ ] Proper SQLAlchemy table definition
- [ ] Database session management
- [ ] Connection handling with DuckDB
- [ ] Foreign key relationship to Project model

### Expected Behavior
The implementation should make this example work:
```python
from andamios_orm import Repository

# CREATE
repo = await Repository.create(
    project_id=1,
    name="backend-api",
    description="Main backend API service",
    repo_type="backend",
    github_url="https://github.com/user/backend-api"
)

# READ
found = await Repository.read(repo.id)

# UPDATE
updated = await Repository.update(
    repo.id,
    name="backend-api-v2",
    repo_type="microservice"
)

# DELETE
await Repository.delete(repo.id)
gone = await Repository.read(repo.id)  # Should return None
```

## Acceptance Criteria
- [ ] Repository model is importable from `andamios_orm`
- [ ] All CRUD operations work asynchronously
- [ ] Returns proper instances with correct data
- [ ] Foreign key relationship with Project works
- [ ] DELETE followed by READ returns None
- [ ] Compatible with DuckDB and uvloop
```

---

## Issue 5: Implement database engine and session management

**Copy this title:**
```
Implement database engine and session management for async operations
```

**Copy this body:**
```markdown
## Summary
Implement the core database infrastructure to support async CRUD operations for all models.

## Requirements

### Engine Management
- [ ] DuckDB async engine configuration
- [ ] Connection pooling setup
- [ ] uvloop integration for performance
- [ ] Environment-based configuration (memory vs file database)

### Session Management
- [ ] Async session factory
- [ ] Context manager for sessions
- [ ] Automatic session cleanup
- [ ] Transaction handling

### Database Initialization
- [ ] Automatic table creation
- [ ] Migration support foundation
- [ ] Schema validation
- [ ] Test database setup utilities

### Core Infrastructure
- [ ] Base model class with async CRUD methods
- [ ] Generic repository pattern (if needed)
- [ ] Error handling and logging
- [ ] Performance monitoring hooks

### Integration Requirements
- [ ] Works with all four models (Project, Conversation, Document, Repository)
- [ ] Supports the examples runner
- [ ] Compatible with testing framework
- [ ] Memory database for tests, file database for production

## Acceptance Criteria
- [ ] All models can be imported from `andamios_orm`
- [ ] Database tables are created automatically
- [ ] Async operations work with uvloop
- [ ] Session management is transparent to users
- [ ] Examples run successfully without manual setup
- [ ] Compatible with DuckDB's columnar architecture
```

---

## Issue 6: Update package exports and imports

**Copy this title:**
```
Update package exports and imports for model availability
```

**Copy this body:**
```markdown
## Summary
Update the main package `__init__.py` to export all four models (Project, Conversation, Document, Repository) so they can be imported directly from `andamios_orm`.

## Requirements

### Package Structure
- [ ] Export Project, Conversation, Document, Repository from main package
- [ ] Maintain existing core API exports
- [ ] Ensure proper module organization
- [ ] Clean import paths for examples

### Import Structure
```python
# This should work:
from andamios_orm import Project, Conversation, Document, Repository

# Also maintain existing core API:
from andamios_orm import create_engine, AsyncSession, etc.
```

### Documentation
- [ ] Update docstrings in `__init__.py`
- [ ] Add proper `__all__` exports
- [ ] Version management
- [ ] Type hint exports

## Acceptance Criteria
- [ ] All models importable from `andamios_orm`
- [ ] Examples run without import errors
- [ ] Backward compatibility with existing core API
- [ ] Clean module organization
- [ ] Proper type hints for IDEs
```

---

## Quick Creation Links:

1. [Create Issue 1](https://github.com/andresclaroavocado/andamios-orm/issues/new)
2. [Create Issue 2](https://github.com/andresclaroavocado/andamios-orm/issues/new)
3. [Create Issue 3](https://github.com/andresclaroavocado/andamios-orm/issues/new)
4. [Create Issue 4](https://github.com/andresclaroavocado/andamios-orm/issues/new)
5. [Create Issue 5](https://github.com/andresclaroavocado/andamios-orm/issues/new)
6. [Create Issue 6](https://github.com/andresclaroavocado/andamios-orm/issues/new)

---

## Issue 7: Fix Base Model CRUD Implementation Issues

**Copy this title:**
```
Fix async CRUD operations in base Model class
```

**Copy this body:**
```markdown
## Summary
The current base Model class in `src/andamios_orm/models/base.py` has several issues that prevent the async CRUD operations from working correctly.

## Problems Identified
1. Session management issues in the CRUD methods
2. Potential async/await inconsistencies
3. Error handling needs improvement
4. Table auto-creation might not work properly

## Requirements

### Session Management
- [ ] Fix `get_session()` import and usage
- [ ] Ensure proper async session handling
- [ ] Implement proper session cleanup in all methods
- [ ] Add error handling for database operations

### CRUD Method Fixes
- [ ] Verify `create()` method works with auto-commit
- [ ] Fix `read()` method to handle None returns properly
- [ ] Ensure `update()` method refreshes instances correctly
- [ ] Fix `delete()` method session handling

### Auto-Initialization
- [ ] Ensure tables are created automatically on first use
- [ ] Handle database initialization transparently
- [ ] Support both memory and file databases

## Acceptance Criteria
- [ ] All CRUD methods work without errors
- [ ] Proper session management and cleanup
- [ ] Auto-table creation works
- [ ] Error handling for all database operations
- [ ] Examples can use the models successfully
```

---

## Issue 8: Add DuckDB Driver Dependencies

**Copy this title:**
```
Add required DuckDB async driver to project dependencies
```

**Copy this body:**
```markdown
## Summary
The project currently references DuckDB in the engine configuration but doesn't have the required async driver dependency installed.

## Requirements

### Dependencies
- [ ] Add `duckdb-engine` to pyproject.toml
- [ ] Ensure compatibility with SQLAlchemy 2.0+
- [ ] Update to latest stable versions
- [ ] Add any additional async dependencies needed

### Configuration
- [ ] Verify DuckDB engine URLs work correctly
- [ ] Test async connection establishment
- [ ] Ensure uvloop compatibility

## Expected Engine URLs
```python
# These should work:
"duckdb+duckdb_engine:///:memory:"           # Memory database
"duckdb+duckdb_engine:///path/to/file.db"    # File database
```

## Acceptance Criteria
- [ ] `duckdb-engine` dependency added
- [ ] Engine creation works without import errors
- [ ] Examples can connect to DuckDB successfully
- [ ] Both memory and file databases work
```

---

## Issue 9: Implement Concrete Model Classes

**Copy this title:**
```
Create Project, Conversation, Document, and Repository model classes
```

**Copy this body:**
```markdown
## Summary
Implement the four concrete model classes that the examples expect to import from the main package.

## Requirements

### Project Model (`src/andamios_orm/models/project.py`)
```python
class Project(Model):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    project_idea = Column(Text)
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### Conversation Model (`src/andamios_orm/models/conversation.py`)
```python
class Conversation(Model):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    phase = Column(String)
    messages = Column(JSON)  # Array of message objects
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### Document Model (`src/andamios_orm/models/document.py`)
```python
class Document(Model):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    content = Column(Text)
    doc_type = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### Repository Model (`src/andamios_orm/models/repository.py`)
```python
class Repository(Model):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    repo_type = Column(String)
    github_url = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

## Package Exports
- [ ] Update `src/andamios_orm/models/__init__.py` to export all models
- [ ] Update `src/andamios_orm/__init__.py` to include models in public API
- [ ] Maintain proper `__all__` lists

## Acceptance Criteria
- [ ] All four model classes created with proper SQLAlchemy definitions
- [ ] Models inherit from base Model class for CRUD operations
- [ ] Foreign key relationships defined correctly
- [ ] Models are importable from `andamios_orm` package
- [ ] All timestamp fields work correctly
- [ ] JSON field works for Conversation messages
```

---

## Updated Quick Creation Links:

1. [Create Issue 1](https://github.com/andresclaroavocado/andamios-orm/issues/new)
2. [Create Issue 2](https://github.com/andresclaroavocado/andamios-orm/issues/new)
3. [Create Issue 3](https://github.com/andresclaroavocado/andamios-orm/issues/new)
4. [Create Issue 4](https://github.com/andresclaroavocado/andamios-orm/issues/new)
5. [Create Issue 5](https://github.com/andresclaroavocado/andamios-orm/issues/new)
6. [Create Issue 6](https://github.com/andresclaroavocado/andamios-orm/issues/new)
7. [Create Issue 7](https://github.com/andresclaroavocado/andamios-orm/issues/new)
8. [Create Issue 8](https://github.com/andresclaroavocado/andamios-orm/issues/new)
9. [Create Issue 9](https://github.com/andresclaroavocado/andamios-orm/issues/new)

## Implementation Priority

**Priority Order:**
1. **Issue 8** - Add DuckDB dependencies (required for everything)
2. **Issue 7** - Fix base Model CRUD implementation 
3. **Issue 9** - Implement concrete model classes
4. **Issue 5** - Complete database infrastructure (if needed)
5. **Issue 6** - Update package exports (final integration)
6. **Issues 1-4** - Individual model implementations (can be done in parallel)

## Recommended Labels:
- `enhancement`
- `backend`
- `models`
- `async`
- `crud`
- `database`