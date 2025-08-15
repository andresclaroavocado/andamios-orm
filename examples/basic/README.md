# Basic Examples

Simple CRUD examples using Model class methods for all 4 models.

## Complete Example (All Models)

### All Models in One File
```bash
python all_models_crud.py
```

Demonstrates CRUD operations for all 4 models:
- **Project** - Main project management
- **Repository** - Code repositories  
- **Conversation** - Project conversations
- **Document** - Project documentation

## Individual Model Examples

### Project CRUD
```bash
python project_simple_final.py
```

### Repository CRUD  
```bash
python repository_simple_final.py
```

### Conversation CRUD
```bash
python conversation_simple_final.py
```

### Document CRUD
```bash
python document_simple_final.py
```

## Usage Pattern

All models follow the same simple pattern:

```python
# CREATE - Just Model.create() and done!
model = await Model.create(field1="value1", field2="value2")

# READ - Simple Model.read()
found = await Model.read(model.id)

# UPDATE - Simple Model.update()  
updated = await Model.update(model.id, field1="new_value")

# DELETE - Simple Model.delete()
deleted = await Model.delete(model.id)
```

## Features

- `Model.create()` - creates and persists immediately
- `Model.read(id)` - reads by ID
- `Model.update(id, **kwargs)` - updates fields
- `Model.delete(id)` - deletes by ID
- Uses async/await
- Works with all existing models
- Clean, simple operations

## Model Coverage

✅ **Project** - project_simple_final.py  
✅ **Repository** - repository_simple_final.py  
✅ **Conversation** - conversation_simple_final.py  
✅ **Document** - document_simple_final.py  
✅ **All Models** - all_models_crud.py

**Status: 4/4 models completed (100%)**