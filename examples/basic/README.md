# Basic Examples

## Ultra Simple Usage (NEW WAY ✨)

The boss wanted examples to be **super easy** - no session management, no engine setup. Just define models and use them!

### 🚀 Start Here - Ultra Simple CRUD
```bash
cd examples/basic
python ultra_simple_crud.py
```

Shows the simplest possible ORM usage:
```python
from simple_models import Project

# Just create and save - library handles everything!
project = Project(name="My App", project_idea="Build something")
await project.save()

# Get by ID - super simple
found = await Project.get(project.id)

# Update and save
found.name = "Updated App"
await found.save()

# Delete
await found.delete()
```

### 📁 Repository Example
```bash
python repository_simple.py
```

### 📄 Document/Conversation Examples
Use the same pattern with `simple_models.py` - all models work the same way!

## Before/After Comparison

### ❌ OLD WAY (Complex)
```bash
python project_crud.py  # See how complex it was before
```

The old way required:
- Manual engine creation
- Session management  
- Context managers
- Manual commits
- Table creation

### ✅ NEW WAY (Simple)
```bash  
python ultra_simple_crud.py  # See how simple it is now
```

The new way requires:
- Just import the model
- Use `await model.save()`, `await Model.get(id)`, etc.
- Library handles everything internally

## Key Benefits

1. **Zero Configuration** - No setup needed
2. **No Session Management** - Library handles it
3. **Auto Table Creation** - Tables created automatically  
4. **Simple API** - Just `save()`, `get()`, `delete()`
5. **One Import** - `from simple_models import Model`

This is exactly what the boss wanted - **"super fácil de usar"**!