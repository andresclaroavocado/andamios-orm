# Andamios ORM Examples - Ultra-Simple EDD

Ultra-simple Example-Driven Development (EDD) examples. Each example demonstrates complete CRUD operations using existing models, following the narrative: **instantiate ORM object → create → persisted in DuckDB → read/update/delete**.

## Examples Structure

**1 comprehensive example per model × 4 models = 4 total examples**

### Complete CRUD Examples
- **`project_crud.py`** - Project: Complete CREATE → READ → UPDATE → DELETE operations
- **`conversation_crud.py`** - Conversation: Complete CREATE → READ → UPDATE → DELETE operations
- **`document_crud.py`** - Document: Complete CREATE → READ → UPDATE → DELETE operations
- **`repository_crud.py`** - Repository: Complete CREATE → READ → UPDATE → DELETE operations

## Running Examples

```bash
# Run any specific example
python examples/basic/project_crud.py
python examples/basic/conversation_crud.py
python examples/basic/document_crud.py
python examples/basic/repository_crud.py

# Run all examples
python examples/run_examples.py
```

## Example Pattern

Each example follows this comprehensive CRUD pattern:

```python
"""
[Model] CRUD Example

Complete Create, Read, Update, Delete operations for [Model] model.
Narrative: instantiate ORM object → create → persisted in DuckDB → read/update/delete
"""

import asyncio
import uvloop
from andamios_orm import create_memory_engine, sessionmaker, AsyncSession

# Import existing models (no model definitions here)
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../legacy'))
from database.models import Base, [Model]

async def main():
    # CREATE: instantiate → create → persisted in DuckDB
    # READ: retrieve object from DuckDB
    # UPDATE: modify and persist changes
    # DELETE: remove from DuckDB
    pass

if __name__ == "__main__":
    uvloop.run(main())
```

## EDD Principles

- **Comprehensive**: All CRUD operations in one example
- **No Model Definitions**: Uses existing models only
- **Clear Narrative**: Each example follows complete story
- **Real DuckDB**: No mocks, actual database operations
- **Async + uvloop**: Modern async patterns