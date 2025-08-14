# Andamios ORM Examples - Ultra-Simple EDD

Ultra-simple Example-Driven Development (EDD) examples. Each example demonstrates one CRUD operation using existing models, following the narrative: **instantiate ORM object → create → persisted in DuckDB**.

## Examples Structure

**4 examples per model × 4 models = 16 total examples**

### CREATE Examples
- **`create_project.py`** - Project: instantiate → create → persisted
- **`create_conversation.py`** - Conversation: instantiate → create → persisted  
- **`create_document.py`** - Document: instantiate → create → persisted
- **`create_repository.py`** - Repository: instantiate → create → persisted

### READ Examples
- **`read_project.py`** - Project: create → read from DuckDB
- **`read_conversation.py`** - Conversation: create → read from DuckDB
- **`read_document.py`** - Document: create → read from DuckDB
- **`read_repository.py`** - Repository: create → read from DuckDB

### UPDATE Examples
- **`update_project.py`** - Project: create → read → update → persisted
- **`update_conversation.py`** - Conversation: create → read → update → persisted
- **`update_document.py`** - Document: create → read → update → persisted
- **`update_repository.py`** - Repository: create → read → update → persisted

### DELETE Examples
- **`delete_project.py`** - Project: create → read → delete → removed
- **`delete_conversation.py`** - Conversation: create → read → delete → removed
- **`delete_document.py`** - Document: create → read → delete → removed
- **`delete_repository.py`** - Repository: create → read → delete → removed

## Running Examples

```bash
# Run any specific example
python examples/basic/create_project.py
python examples/basic/read_conversation.py
python examples/basic/update_document.py
python examples/basic/delete_repository.py

# Run all examples
python examples/run_examples.py
```

## Example Pattern

Each example follows this ultra-simple pattern:

```python
"""
[OPERATION] [Model] Example

Narrative: [specific flow for this operation]
"""

import asyncio
import uvloop
from andamios_orm import create_memory_engine, sessionmaker, AsyncSession

# Import existing models (no model definitions here)
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../legacy'))
from database.models import Base, [Model]

async def main():
    # [Operation implementation following the narrative]
    pass

if __name__ == "__main__":
    uvloop.run(main())
```

## EDD Principles

- **Ultra-Simple**: One operation per example
- **No Model Definitions**: Uses existing models only
- **Clear Narrative**: Each example follows exact story
- **Real DuckDB**: No mocks, actual database operations
- **Async + uvloop**: Modern async patterns