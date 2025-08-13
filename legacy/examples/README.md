# Andamios ORM Examples

This directory contains comprehensive examples following our Example-Driven Development approach. All examples are executable and tested.

## Example Structure

### 📚 [Basic Examples](./basic/)
Foundation concepts and simple usage patterns:
- `01_connection.py` - Database connection and engine setup
- `02_models.py` - Model definition and basic fields
- `03_crud.py` - Create, Read, Update, Delete operations
- `04_queries.py` - Basic querying and filtering
- `05_transactions.py` - Transaction management

### 🔧 [Intermediate Examples](./intermediate/)
More advanced patterns and real-world usage:
- `01_repositories.py` - Repository pattern implementation
- `02_complex_queries.py` - Advanced querying techniques
- `03_relationships.py` - Model relationships and joins
- `04_migrations.py` - Database migrations and schema evolution
- `05_testing.py` - Testing patterns with real databases

### 🚀 [Advanced Examples](./advanced/)
Performance optimization and sophisticated patterns:
- `01_performance.py` - Performance optimization techniques
- `02_custom_types.py` - Custom field types and validators
- `03_events.py` - Event handling and lifecycle hooks
- `04_middleware.py` - Middleware and request processing
- `05_extensions.py` - Custom extensions and plugins

## Running Examples

Each example is self-contained and can be run directly:

```bash
# Run a basic example
python examples/basic/01_connection.py

# Run with uvloop for best performance
python -c "import uvloop; uvloop.run(main())" examples/basic/01_connection.py
```

## Example Guidelines

### 1. Self-Contained
Each example should run independently without external dependencies beyond the core library.

### 2. Well-Documented
Examples include:
- Clear docstrings explaining the purpose
- Inline comments for complex logic
- Expected output and behavior

### 3. Real-World Focused
Examples solve actual problems:
- Common use cases developers face
- Performance optimization scenarios
- Error handling patterns

### 4. Async-First
All examples demonstrate async patterns:
- Proper async/await usage
- uvloop integration
- Connection management

## Example Development Process

### Phase 1: Example Creation
1. Identify a real-world use case
2. Create a minimal, executable example
3. Document expected behavior
4. Ensure async-first patterns

### Phase 2: Test Development
1. Create corresponding tests in `/tests/`
2. Test the example behavior
3. Verify performance characteristics
4. Ensure parallel test execution

### Phase 3: Implementation
1. Implement library functionality
2. Ensure examples still work
3. Optimize for performance
4. Update documentation

## Common Patterns

### Database Connection
```python
import asyncio
import uvloop
from andamios_orm import create_engine, sessionmaker

async def main():
    engine = create_engine("duckdb:///example.db")
    SessionLocal = sessionmaker(engine)
    
    async with SessionLocal() as session:
        # Your code here
        pass

if __name__ == "__main__":
    uvloop.run(main())
```

### Error Handling
```python
from andamios_orm.exceptions import AndamiosORMError

try:
    async with SessionLocal() as session:
        # Database operations
        pass
except AndamiosORMError as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Performance Monitoring
```python
import time
from contextlib import asynccontextmanager

@asynccontextmanager
async def measure_time():
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        print(f"Operation took {end - start:.3f} seconds")

async with measure_time():
    # Database operations to measure
    pass
```

## Contributing Examples

When adding new examples:

1. **Follow the naming convention**: `NN_descriptive_name.py`
2. **Include docstrings**: Explain what the example demonstrates
3. **Make it executable**: Can be run with `python filename.py`
4. **Add to tests**: Create corresponding tests
5. **Update documentation**: Add to relevant guides

## Testing Examples

All examples are automatically tested:

```bash
# Test all examples
pytest tests/examples/

# Test specific category
pytest tests/examples/test_basic_examples.py
```

Examples are tested by:
- Executing them in isolated environments
- Verifying expected output
- Checking performance characteristics
- Ensuring no resource leaks