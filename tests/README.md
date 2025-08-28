# Test Structure Documentation

This document describes the modular test structure for the Canvas Quiz Manager application.

## Overview

The tests have been reorganized from a flat structure to a modular structure that mirrors the application's code organization. This provides better organization, easier navigation, and improved maintainability.

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── unit/                          # Unit tests
│   ├── __init__.py
│   ├── test_core/                 # Core application tests
│   │   ├── __init__.py
│   │   ├── test_app.py           # App creation and configuration
│   │   └── test_config.py        # Configuration validation
│   ├── test_utils/               # Utility function tests
│   │   ├── __init__.py
│   │   ├── test_file_utils.py    # File I/O operations
│   │   └── test_text_utils.py    # Text processing functions
│   ├── test_services/            # Service layer tests
│   │   ├── __init__.py
│   │   └── test_ai_service.py    # AI service functionality
│   └── test_models/              # Data model tests
│       ├── __init__.py
│       ├── test_objective.py     # Learning objective model
│       └── test_question.py      # Question model
├── integration/                   # Integration tests
│   ├── __init__.py
│   ├── test_api/                 # API endpoint tests
│   │   ├── __init__.py
│   │   ├── test_canvas.py        # Canvas API integration
│   │   ├── test_chat.py          # Chat API endpoints
│   │   ├── test_questions.py     # Questions API endpoints
│   │   ├── test_objectives.py    # Objectives API endpoints
│   │   ├── test_system_prompt.py # System prompt API
│   │   └── test_vector_store.py  # Vector store API
│   └── test_workflows.py         # End-to-end workflows
└── e2e/                          # End-to-end tests
    ├── __init__.py
    └── test_full_app.py          # Full application workflows
```

## Test Categories

### Unit Tests (`tests/unit/`)

- **Purpose**: Test individual functions and classes in isolation
- **Scope**: Single module or function
- **Dependencies**: Mocked external dependencies
- **Speed**: Fast execution
- **Markers**: `@pytest.mark.unit`

### Integration Tests (`tests/integration/`)

- **Purpose**: Test interactions between modules and external services
- **Scope**: Multiple modules working together
- **Dependencies**: Mocked external APIs, real internal interactions
- **Speed**: Medium execution time
- **Markers**: `@pytest.mark.integration`

### End-to-End Tests (`tests/e2e/`)

- **Purpose**: Test complete user workflows
- **Scope**: Full application stack
- **Dependencies**: Mocked external services, real application flow
- **Speed**: Slower execution
- **Markers**: `@pytest.mark.e2e`

## Running Tests

### Run all tests

```bash
poetry run pytest
```

### Run specific test categories

```bash
# Unit tests only
poetry run pytest -m unit

# Integration tests only
poetry run pytest -m integration

# End-to-end tests only
poetry run pytest -m e2e
```

### Run tests for specific modules

```bash
# All utility tests
poetry run pytest tests/unit/test_utils/

# All API tests
poetry run pytest tests/integration/test_api/

# Specific test file
poetry run pytest tests/unit/test_utils/test_file_utils.py
```

### Run specific test functions

```bash
poetry run pytest tests/unit/test_utils/test_file_utils.py::TestFileOperations::test_load_questions_empty_file
```

## Test Organization Principles

1. **Mirror Source Structure**: Test directories mirror the source code structure
2. **Single Responsibility**: Each test file focuses on one module or feature
3. **Clear Naming**: Test files and classes have descriptive names
4. **Appropriate Scope**: Tests are categorized by their scope and purpose
5. **Shared Fixtures**: Common test data and mocks are in `conftest.py`

## Benefits of This Structure

1. **Easier Navigation**: Find tests for specific functionality quickly
2. **Better Maintainability**: Changes to a module only affect its test file
3. **Faster Execution**: Run only the tests you need
4. **Clear Separation**: Unit, integration, and e2e tests are clearly separated
5. **Improved Discoverability**: New developers can easily understand the test structure

## Migration from Old Structure

The original flat test structure has been preserved in the following files:

- `tests/test_utility_functions.py` → Split into `tests/unit/test_utils/`
- `tests/test_api_endpoints.py` → Split into `tests/integration/test_api/`
- `tests/test_ai_integration.py` → Split into `tests/unit/test_services/` and `tests/integration/test_api/`
- `tests/test_integration.py` → Moved to `tests/e2e/`

## Adding New Tests

When adding new tests:

1. **Identify the test type**: Unit, integration, or e2e
2. **Choose the appropriate directory**: Based on what's being tested
3. **Follow naming conventions**: `test_<module_name>.py`
4. **Use appropriate markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, or `@pytest.mark.e2e`
5. **Add to conftest.py**: If new fixtures are needed across multiple test files

## Example Test Structure

```python
"""
Unit tests for file utility functions
"""
import pytest
from question_app.utils import load_questions


class TestFileOperations:
    """Test file loading and saving operations."""

    @pytest.mark.unit
    def test_load_questions_empty_file(self):
        """Test loading questions from empty file"""
        # Test implementation
        pass
```

This modular structure makes the test suite more organized, maintainable, and easier to work with as the application grows.
