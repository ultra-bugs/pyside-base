# Testing Setup - BVAUTO2

## Quick Summary

✅ **Setup Complete** - Minimal test infrastructure ready for ACK mechanism implementation.

## What Was Done

### 1. Dependencies Added (pyproject.toml)

```toml
[dependency-groups.test]
pytest> = 8.0.0          # Test framework
pytest-qt> = 4.4.0       # PySide6 testing support
pytest-mock> = 3.14.0    # Mocking utilities
pytest-cov> = 6.0.0      # Coverage reporting
pytest-asyncio> = 0.24.0 # Async test support
```

### 2. Test Structure Created

```
tests_auto/
├── README.md                              # Comprehensive testing guide
├── conftest.py                            # Shared fixtures
├── core/
│   └── ack/
│       ├── test_acknowledgment_tracker.py # Unit: Thread-safety critical
│       └── test_acknowledgment_receiver.py # Unit: Protocol tests
└── integration/
    └── test_vnd_ack_workflow.py          # E2E: Full workflow
```

### 3. Configuration Files

- **pytest.ini**: Test discovery, markers, coverage settings
- **.gitignore**: Already includes test artifacts (htmlcov/, .coverage, etc.)

### 4. Fixtures Provided (conftest.py)

**PySide6:**

- `qapp` - QApplication instance

**Mocking:**

- `mock_publisher` - Mock Publisher singleton
- `mock_subscriber` - Mock Subscriber
- `real_publisher` - Real Publisher for integration tests
- `mock_ack_tracker` - Mock AcknowledgmentTracker
- `mock_api_client` - Mock BetMateApiClient

**Utilities:**

- `event_tracker` - Track event emission order
- `thread_pool` - ThreadPoolExecutor for concurrent tests
- `helpers` - Test helper functions

## Installation

### Using Pixi (Recommended)

```bash
# Install all dependencies including test group
pixi install

# Or add test dependencies specifically
pixi add --pypi pytest pytest-qt pytest-mock pytest-cov pytest-asyncio
```

### Using pip/uv (Alternative)

```bash
pip install pytest pytest-qt pytest-mock pytest-cov pytest-asyncio
```

## Usage

### Run All Tests

```bash
pytest
```

### Run Specific Categories

```bash
pytest -m unit          # Fast unit tests only
pytest -m integration   # Integration tests only
pytest -m ack          # ACK mechanism tests
pytest -m "not slow"   # Exclude slow tests
```

### Run with Coverage

```bash
pytest --cov=core --cov=services --cov-report=html
```

Open `htmlcov/index.html` to view coverage report.

### Development Workflow

1. **Implement code** (e.g., AcknowledgmentTracker)
2. **Uncomment test template** in `test_acknowledgment_tracker.py`
3. **Run test**: `pytest tests_auto/core/ack/test_acknowledgment_tracker.py -v`
4. **Fix failures** until green
5. **Check coverage**: `pytest --cov=core.ack --cov-report=term-missing`
6. **Iterate**

## Test Templates

All test files contain TODO templates with examples:

```python
def test_register_pending_acknowledgment(self):
    """Test registering a pending acknowledgment."""
    # TODO: Implement after creating AcknowledgmentTracker
    # from core.ack.AcknowledgmentTracker import AcknowledgmentTracker
    #
    # tracker = AcknowledgmentTracker()
    # callback = MagicMock()
    #
    # tracker.register_pending('ack_001', success_callback=callback)
    #
    # assert tracker.is_pending('ack_001')
    # assert tracker.pending_count() == 1
    pass
```

Simply uncomment and implement after creating the actual classes.

## Coverage Goals

| Layer                 | Target | Focus                                  |
|-----------------------|--------|----------------------------------------|
| Layer 1 (Core ACK)    | ≥95%   | Thread-safety, timeout, all edge cases |
| Layer 2 (Application) | ≥80%   | Publisher/Subscriber integration       |
| Layer 3 (VND)         | ≥70%   | E2E workflows, critical paths          |
| Integration           | N/A    | Full workflows work correctly          |

## Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit  # Fast, isolated
@pytest.mark.integration  # Slower, may use services
@pytest.mark.slow  # > 1 second
@pytest.mark.ack  # ACK mechanism
@pytest.mark.browser  # Requires browser
@pytest.mark.api  # Requires API
```

## Example: Writing a Test

```python
import pytest
from unittest.mock import MagicMock


@pytest.mark.unit
@pytest.mark.ack
def test_my_feature(mock_publisher):
    """Test description."""
    # Arrange
    from core.Observer import Publisher
    
    # Act
    Publisher().notify('event', data='test')
    
    # Assert
    mock_publisher.notify.assert_called_once_with('event', data='test')
```

## Next Steps

1. ✅ Test infrastructure setup complete
2. ⏳ Implement Phase 1: Core ACK Protocol (Tasks 1.1-1.3)
3. ⏳ Uncomment test templates
4. ⏳ Run tests and achieve target coverage
5. ⏳ Repeat for Phase 2 & 3

## Documentation

- **Detailed Guide**: `tests_auto/README.md`
- **Implementation Plan**: `docs/tasks/task-acknowledgment-mechanism.md`
- **Fixtures Reference**: `tests_auto/conftest.py`

## Philosophy

> **Test what matters, not everything.**

Focus on:

- ✅ Thread-safety (critical for ACK tracker)
- ✅ Timeout mechanisms
- ✅ Integration between layers
- ✅ Error paths

Skip:

- ❌ Trivial getters/setters
- ❌ Framework internals
- ❌ Third-party library code

## Questions?

See `tests_auto/README.md` for comprehensive guide including:

- All available fixtures
- Writing tests best practices
- Troubleshooting common issues
- CI/CD integration (optional)

---

**Setup Date:** 2025-10-03
**Status:** Ready for implementation
