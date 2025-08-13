---
name: Test Development Task
about: Create a task for writing tests (Phase 2 - TDD)
title: 'Tests: [Component/functionality to test]'
labels: ['tests', 'phase-2', 'integration']
assignees: ''
---

## 🧪 Test Description

**What functionality to test:**
<!-- Describe what specific functionality these tests cover -->

**Test category:**
- [ ] Unit tests (isolated component testing)
- [ ] Integration tests (with real database)
- [ ] End-to-end tests (complete workflows)
- [ ] Performance tests (benchmarking)

## 🎯 Acceptance Criteria

- [ ] Tests cover all example functionality from corresponding examples
- [ ] Use real DuckDB instances (no mocking of database operations)
- [ ] Support parallel test execution
- [ ] Achieve 100% code coverage for tested components
- [ ] Include performance assertions where relevant
- [ ] Test error conditions and edge cases
- [ ] Follow async testing patterns
- [ ] Include test data factories where needed

## 📂 Files to Create/Modify

**Test files:**
- `tests/unit/test_[component].py` (if unit tests)
- `tests/integration/test_[component].py` (if integration tests)
- `tests/e2e/test_[workflow].py` (if e2e tests)

**Supporting files:**
- Update `tests/conftest.py` if needed
- Add to `tests/factories.py` if test data needed
- Update test documentation

## 🔗 Dependencies

**Must be completed first:**
- [ ] #[issue-number] - [corresponding example issue]

**Blocks:**
- [ ] #[issue-number] - [implementation issue that depends on these tests]

## 📋 Test Coverage Checklist

### Functional Testing
- [ ] **Happy path scenarios** - Normal usage patterns
- [ ] **Edge cases** - Boundary conditions
- [ ] **Error conditions** - Invalid inputs, database errors
- [ ] **Data validation** - Input validation and constraints
- [ ] **Async behavior** - Proper async/await patterns

### Integration Testing
- [ ] **Database operations** - Real database CRUD operations
- [ ] **Transaction handling** - Commit, rollback scenarios
- [ ] **Connection management** - Connection lifecycle
- [ ] **Resource cleanup** - Proper cleanup after operations
- [ ] **Concurrent operations** - Multiple simultaneous operations

### Performance Testing
- [ ] **Response time assertions** - Meet performance targets
- [ ] **Memory usage** - No memory leaks
- [ ] **Connection pooling** - Efficient connection usage
- [ ] **Bulk operations** - Large dataset handling

## 🏗️ Test Structure Template

```python
"""
Tests for [component/functionality].

These tests verify the behavior demonstrated in the corresponding examples
and ensure the implementation meets all requirements.
"""

import pytest
import asyncio
from andamios_orm import [imports]

class Test[ComponentName]:
    """Test suite for [component] functionality."""
    
    @pytest.mark.asyncio
    async def test_basic_functionality(self, session):
        """Test basic [component] functionality."""
        # Test the happy path scenario
        pass
    
    @pytest.mark.asyncio
    async def test_error_handling(self, session):
        """Test error handling in [component]."""
        # Test error conditions
        pass
    
    @pytest.mark.asyncio
    async def test_edge_cases(self, session):
        """Test edge cases for [component]."""
        # Test boundary conditions
        pass

@pytest.mark.integration
class Test[ComponentName]Integration:
    """Integration tests for [component] with real database."""
    
    @pytest.mark.asyncio
    async def test_database_operations(self, clean_session):
        """Test [component] with real database operations."""
        # Test with actual database
        pass

@pytest.mark.performance
class Test[ComponentName]Performance:
    """Performance tests for [component]."""
    
    @pytest.mark.asyncio
    async def test_performance_targets(self, session, performance_monitor):
        """Test that [component] meets performance targets."""
        with performance_monitor.measure("[operation]"):
            # Performance test code
            pass
        
        measurements = performance_monitor.get_measurements()
        assert measurements["[operation]"] < [target_time]
```

## 🔧 Test Configuration

### Fixtures Needed
- [ ] `session` - Database session with rollback
- [ ] `clean_session` - Database session that commits
- [ ] `isolated_db` - Completely isolated database
- [ ] `performance_monitor` - Performance measurement
- [ ] Custom fixtures: [list any needed custom fixtures]

### Test Data
- [ ] Use factory-boy for test data generation
- [ ] Create realistic test scenarios
- [ ] Include edge case data
- [ ] Test with various data volumes

### Parallel Execution
- [ ] Tests work with pytest-xdist
- [ ] No shared state between tests
- [ ] Proper database isolation
- [ ] No race conditions

## 📊 Coverage Requirements

**Minimum coverage targets:**
- [ ] 100% line coverage for tested components
- [ ] 100% branch coverage for complex logic
- [ ] All public API methods tested
- [ ] All error conditions tested

**Coverage verification:**
```bash
pytest tests/[test_file] --cov=src/andamios_orm/[component] --cov-report=term-missing --cov-fail-under=100
```

## 🚀 Performance Targets

**Response time targets:**
- Simple operations: < 1ms
- Complex operations: < 10ms  
- Bulk operations: < 100ms for 10,000 records
- Connection acquisition: < 5ms

**Resource usage targets:**
- Memory usage: No leaks detected
- Connection count: Proper pooling behavior
- CPU usage: Reasonable for operation complexity

## 📝 Definition of Done

- [ ] All tests pass consistently
- [ ] 100% code coverage achieved
- [ ] Performance targets met
- [ ] Tests support parallel execution
- [ ] No database mocking used
- [ ] Error conditions properly tested
- [ ] Code review completed
- [ ] Tests integrated into CI pipeline