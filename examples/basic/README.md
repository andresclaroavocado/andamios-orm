# Basic Examples

Simple CRUD examples using Model class methods.

## Examples

### Repository CRUD
```bash
python repository_simple_final.py
```

**Usage pattern:**
```python
# CREATE - Just Model.create() and done!
repo = await Repository.create(
    project_id=1,
    name="backend-api",
    description="Main backend API service",
    repo_type="backend",
    github_url="https://github.com/user/backend-api"
)

# READ - Simple Model.read()
found_repo = await Repository.read(repo.id)

# UPDATE - Simple Model.update()  
updated_repo = await Repository.update(
    repo.id, 
    name="advanced-backend-api",
    repo_type="microservice"
)

# DELETE - Simple Model.delete()
deleted = await Repository.delete(repo.id)
```

### Project CRUD
```bash
python project_simple_final.py
```

Same pattern for Project model.

## Features

- `Model.create()` - creates and persists immediately
- `Model.read(id)` - reads by ID
- `Model.update(id, **kwargs)` - updates fields
- `Model.delete(id)` - deletes by ID
- Uses async/await
- Works with existing models
- Clean, simple operations