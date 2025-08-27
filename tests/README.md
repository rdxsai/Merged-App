# Question App Test Suite

This directory contains comprehensive tests for the Question App, a FastAPI-based web application for managing Canvas LMS quiz questions with AI-powered feedback generation.

## Test Structure

### Test Files

- **`conftest.py`** - Pytest configuration and shared fixtures
- **`test_utility_functions.py`** - Unit tests for utility functions
- **`test_api_endpoints.py`** - Tests for API endpoints and HTTP responses
- **`test_ai_integration.py`** - Tests for AI integration features
- **`test_integration.py`** - Integration tests for complete workflows
- **`azure_openai_test_script.py`** - Standalone Azure OpenAI connectivity testing script

### Test Categories

#### Unit Tests (`@pytest.mark.unit`)

- Test individual functions and components in isolation
- Mock external dependencies
- Fast execution
- High code coverage

#### Integration Tests (`@pytest.mark.integration`)

- Test complete workflows and system interactions
- May use real file operations and mocked external services
- Test data consistency and error handling

#### AI Integration Tests (`@pytest.mark.ai`)

- Test AI service integrations (Azure OpenAI, Ollama)
- Mock AI service responses
- Test feedback generation and parsing

#### API Tests (`@pytest.mark.api`)

- Test HTTP endpoints and responses
- Test request/response formats
- Test error handling and status codes

#### Slow Tests (`@pytest.mark.slow`)

- Tests that take longer to execute
- Can be skipped with `--fast` flag
- Include performance and large dataset tests

## Running Tests

### Prerequisites

1. Install test dependencies:

```bash
poetry install --with dev
```

2. Ensure you have the required packages:

- pytest
- pytest-asyncio
- httpx (for async HTTP testing)

### Basic Test Commands

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_utility_functions.py

# Run specific test class
python -m pytest tests/test_api_endpoints.py::TestHomeEndpoint

# Run specific test method
python -m pytest tests/test_utility_functions.py::TestFileOperations::test_load_questions_empty_file
```

### Using the Test Runner Script

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --type unit

# Run only integration tests
python run_tests.py --type integration

# Run AI integration tests
python run_tests.py --type ai

# Run with coverage report
python run_tests.py --coverage

# Skip slow tests
python run_tests.py --fast

# Verbose output
python run_tests.py --verbose
```

### Test Markers

```bash
# Run only unit tests
python -m pytest -m unit

# Run only integration tests
python -m pytest -m integration

# Run only AI tests
python -m pytest -m ai

# Run only API tests
python -m pytest -m api

# Skip slow tests
python -m pytest -m "not slow"

# Run multiple marker combinations
python -m pytest -m "unit or api"
```

## Test Coverage

### Current Coverage Areas

1. **Utility Functions**

   - File operations (load/save questions, objectives, prompts)
   - Chat utility functions (system prompts, welcome messages)
   - Text cleaning and processing
   - Topic extraction
   - Answer feedback cleaning
   - Tag extraction

2. **API Endpoints**

   - Home page and navigation
   - Question CRUD operations
   - System prompt management
   - Chat functionality and endpoints
   - Chat system prompt management
   - Chat welcome message management
   - Learning objectives management
   - Debug endpoints (config, question, Ollama test)
   - System prompt testing page

3. **AI Integration**

   - Azure OpenAI feedback generation
   - Ollama embeddings
   - Vector store operations
   - Chat message processing

4. **Integration Workflows**
   - Complete question lifecycle
   - System prompt workflow
   - Objectives management
   - Chat workflow
   - Vector store creation

### Coverage Report

Generate a coverage report:

```bash
# Install coverage package
pip install coverage

# Run tests with coverage
python -m pytest --cov=main --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

## Test Data

### Sample Data

The tests use sample data defined in fixtures:

- **Sample Questions**: Mock quiz questions with various types and content
- **Sample Objectives**: Learning objectives with different Bloom's levels
- **Mock Environment Variables**: Test configuration values

### Temporary Files

Tests create temporary files and directories for testing file operations:

- Temporary JSON files for questions and objectives
- Temporary text files for system prompts
- Automatic cleanup after tests complete

## Mocking Strategy

### External Services

- **Canvas API**: Mocked HTTP responses for course/quiz data
- **Azure OpenAI**: Mocked API responses for feedback generation
- **Ollama**: Mocked embedding generation
- **ChromaDB**: Mocked vector store operations

### File Operations

- File I/O operations are mocked to avoid side effects
- Temporary files are used when real file operations are needed
- Automatic cleanup ensures test isolation

## Best Practices

### Writing Tests

1. **Use descriptive test names** that explain what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Test both success and failure cases**
4. **Mock external dependencies** to ensure test isolation
5. **Use appropriate markers** to categorize tests

### Test Organization

1. **Group related tests** in test classes
2. **Use fixtures** for common setup and teardown
3. **Keep tests independent** - no test should depend on another
4. **Clean up resources** after each test

### Performance

1. **Mark slow tests** with `@pytest.mark.slow`
2. **Use async tests** for async functions
3. **Mock expensive operations** like AI API calls
4. **Use appropriate timeouts** for external service calls

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the main module is in the Python path
2. **Async Test Issues**: Use `@pytest.mark.asyncio` for async tests
3. **Mock Issues**: Ensure mocks are applied to the correct module path
4. **File Permission Errors**: Use temporary files for file operations

### Debug Mode

Run tests in debug mode for more information:

```bash
python -m pytest -v --tb=long --pdb
```

### Test Isolation

If tests are interfering with each other:

```bash
# Run tests in isolation
python -m pytest --dist=no

# Run specific test in isolation
python -m pytest tests/test_specific.py -v --tb=long
```

## Continuous Integration

### GitHub Actions

The test suite is designed to work with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    python -m pytest --cov=main --cov-report=xml
    python -m pytest -m "not slow"  # Skip slow tests in CI
```

### Pre-commit Hooks

Consider adding pre-commit hooks to run tests before commits:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: python -m pytest
        language: system
        pass_filenames: false
```

## Contributing

When adding new features:

1. **Write tests first** (TDD approach)
2. **Add appropriate markers** to new tests
3. **Update this README** if adding new test categories
4. **Ensure all tests pass** before submitting PR
5. **Add integration tests** for new workflows
