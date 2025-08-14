# Andamios ORM Examples

Simple CRUD examples demonstrating how to use Andamios ORM with the project's actual models. Each example shows how to create ORM objects in memory and save them to DuckDB.

## Available Examples

### 📚 [Basic CRUD Operations](./basic/)
Simple Create, Read, Update, Delete operations using project models:
- `01_simple_crud.py` - Project model CRUD operations
- `02_conversation_crud.py` - Conversation model CRUD operations  
- `03_document_crud.py` - Document model CRUD operations
- `04_repository_crud.py` - Repository model CRUD operations

## Running Examples

Each example is self-contained and can be run directly:

```bash
# Run a specific example
python examples/basic/01_simple_crud.py
python examples/basic/02_conversation_crud.py
python examples/basic/03_document_crud.py
python examples/basic/04_repository_crud.py
```

## What Each Example Shows

### Create
- Create an ORM object in memory
- Save it to DuckDB using `session.add()` and `session.commit()`

### Read  
- Retrieve objects from DuckDB using `session.get()`
- Access object properties

### Update
- Modify object properties
- Save changes using `session.commit()`

### Delete
- Remove objects using `session.delete()`
- Verify deletion

## Example Pattern

Each example follows this simple pattern:

```python
# Create object in memory
obj = Model(field1="value1", field2="value2")

# Save to DuckDB  
session.add(obj)
await session.commit()
```

## Prerequisites

- Python 3.13+
- Poetry
- DuckDB (installed automatically)

## Setup

```bash
poetry install
python examples/basic/01_simple_crud.py
```