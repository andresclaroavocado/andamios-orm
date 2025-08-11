# Andamios ORM Examples

This directory contains comprehensive examples demonstrating all features of the Andamios ORM library. Examples follow the Example-Driven Development (EDD) approach where clear, practical examples drive the API design and implementation.

## Example Categories

### 1. Basic Examples (`basic/`)
- Simple CRUD operations
- Basic model definitions
- Repository pattern usage
- Database connections

### 2. Advanced Examples (`advanced/`)
- Complex relationships
- Advanced querying
- Performance optimizations
- Custom repository implementations

### 3. Integration Examples (`integration/`)
- FastAPI integration
- Pydantic model integration
- Alembic migrations
- Testing patterns

### 4. Real-World Examples (`real_world/`)
- Complete application examples
- Production patterns
- Performance considerations
- Best practices

## Running Examples

Each example is self-contained and can be run independently:

```bash
# Setup virtual environment
poetry install

# Start test database
docker-compose -f docker/test-databases.yml up -d

# Run a specific example
cd examples/basic
python user_crud.py

# Run all examples
python -m examples.run_all
```

## Example Structure

Each example follows this structure:

```python
"""
Example: [Title]

Description: [What this example demonstrates]

Key Concepts:
- [Concept 1]
- [Concept 2]
- [Concept 3]

Prerequisites:
- [Requirement 1]
- [Requirement 2]
"""

# 1. Setup and imports
# 2. Model definitions (if needed)
# 3. Repository setup
# 4. Example operations
# 5. Cleanup

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
```

## Contributing Examples

When adding new examples:

1. **Start with the use case**: What problem does this solve?
2. **Keep it focused**: One example, one concept
3. **Make it executable**: Example should run without modification
4. **Add comprehensive comments**: Explain what and why
5. **Include error handling**: Show proper exception handling
6. **Demonstrate best practices**: Use optimal patterns
7. **Add to the test suite**: Each example should have tests