---
name: Example Development Task
about: Create a task for developing examples (Phase 1 - EDD)
title: 'Example: [Brief description of what the example demonstrates]'
labels: ['examples', 'phase-1', 'good-first-issue']
assignees: ''
---

## 📝 Example Description

**What this example demonstrates:**
<!-- Describe what practical use case this example shows -->

**Target audience:**
<!-- Who is this example for? (beginners, intermediate, advanced) -->

## 🎯 Acceptance Criteria

- [ ] Example is self-contained and executable
- [ ] Includes comprehensive docstring explaining purpose
- [ ] Demonstrates async-first patterns
- [ ] Includes error handling where appropriate
- [ ] Shows expected output/behavior in comments
- [ ] Uses realistic data and scenarios
- [ ] Follows project code style guidelines
- [ ] Is well-commented for educational value

## 📂 Files to Create/Modify

**Example file:**
- `examples/[category]/[number]_[name].py`

**Documentation:**
- Add to `examples/README.md` if needed
- Update relevant guide in `docs/guides/`

## 🔄 Related Issues

**Follows (examples that should be completed first):**
- [ ] #[issue-number] - [prerequisite example]

**Leads to (what depends on this example):**
- [ ] #[issue-number] - [corresponding test issue]

## 📋 Example Content Checklist

- [ ] **Import statements** - Show proper imports
- [ ] **Setup code** - Database connection, engine setup
- [ ] **Main functionality** - Core demonstration
- [ ] **Error handling** - Show proper error handling
- [ ] **Cleanup** - Proper resource cleanup
- [ ] **Performance monitoring** - Include timing where relevant
- [ ] **Multiple scenarios** - Show different use cases
- [ ] **Documentation** - Clear explanations and comments

## 🎨 Example Template

```python
"""
Example [NN]: [Title]

This example demonstrates how to:
- [Key concept 1]
- [Key concept 2]  
- [Key concept 3]

Expected behavior:
- [What should happen when run]
- [Performance characteristics]
- [Error conditions handled]
"""

import asyncio
import uvloop
from andamios_orm import [imports]

async def example_function():
    """[Description of what this function demonstrates]."""
    print("🚀 Starting [example name]...")
    
    # Your example code here
    
    print("✅ [Example name] completed successfully!")

async def main():
    """Main example runner."""
    print("📚 [Example Category] Examples")
    print("=" * 50)
    
    await example_function()
    
    print("\n✨ All examples completed!")

if __name__ == "__main__":
    uvloop.run(main())
```

## 🧪 Testing Considerations

When this example is complete, the corresponding test issue should verify:
- [ ] Example runs without errors
- [ ] Produces expected output
- [ ] Meets performance requirements
- [ ] Handles edge cases properly
- [ ] Uses real database operations (no mocks)

## 📝 Definition of Done

- [ ] Example code is complete and tested
- [ ] Example runs successfully in isolation
- [ ] Documentation is updated
- [ ] Code review completed
- [ ] Example added to automated testing