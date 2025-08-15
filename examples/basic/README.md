# Basic Examples

Simple CRUD examples using Model class methods for all 4 models.

## Examples

### Project CRUD
```bash
python project_crud.py
```

### Repository CRUD  
```bash
python repository_crud.py
```

### Conversation CRUD
```bash
python conversation_crud.py
```

### Document CRUD
```bash
python document_crud.py
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

✅ **Project** - project_crud.py  
✅ **Repository** - repository_crud.py  
✅ **Conversation** - conversation_crud.py  
✅ **Document** - document_crud.py  

**Status: 4/4 models completed (100%)**