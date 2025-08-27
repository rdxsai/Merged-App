Development Guide
=================

This guide provides information for developers working on the Canvas Quiz Manager application.

Development Setup
----------------

Prerequisites
~~~~~~~~~~~~

* Python 3.11 or higher
* Poetry for dependency management
* Git for version control
* Ollama for local embedding generation
* Canvas LMS account for testing

Initial Setup
~~~~~~~~~~~~

1. **Clone the repository**

   .. code-block:: bash

      git clone <repository-url>
      cd questionapp

2. **Install dependencies**

   .. code-block:: bash

      poetry install

3. **Set up development environment**

   .. code-block:: bash

      # Create .env file for development
      cp .env.example .env
      # Edit .env with your configuration

4. **Install pre-commit hooks**

   .. code-block:: bash

      poetry run pre-commit install

Project Structure
----------------

.. code-block:: text

   questionapp/
   ├── main.py                 # Main application file
   ├── pyproject.toml          # Poetry configuration
   ├── requirements.txt        # Dependencies
   ├── pytest.ini             # Test configuration
   ├── run_tests.py           # Test runner
   ├── static/                # Static assets
   │   ├── css/
   │   └── js/
   ├── templates/             # Jinja2 templates
   ├── tests/                 # Test suite
   │   ├── conftest.py
   │   ├── test_ai_integration.py
   │   ├── test_api_endpoints.py
   │   ├── test_integration.py
   │   └── test_utility_functions.py
   ├── vector_store/          # ChromaDB storage
   └── docs/                  # Documentation
       ├── conf.py
       ├── index.rst
       └── ...

Code Style
----------

Formatting
~~~~~~~~~~

The project uses Black for code formatting:

.. code-block:: bash

   poetry run black .

Import Sorting
~~~~~~~~~~~~~

Use isort for import sorting:

.. code-block:: bash

   poetry run isort .

Linting
~~~~~~~

Use flake8 for linting:

.. code-block:: bash

   poetry run flake8 .

Pre-commit Hooks
~~~~~~~~~~~~~~~~

The project includes pre-commit hooks that run automatically:

.. code-block:: text

   - black: Code formatting
   - isort: Import sorting
   - flake8: Linting
   - trailing-whitespace: Remove trailing whitespace
   - end-of-file-fixer: Ensure files end with newline

Testing
-------

Running Tests
~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   poetry run pytest

   # Run with coverage
   poetry run pytest --cov=main

   # Run specific test file
   poetry run pytest tests/test_api_endpoints.py

   # Run with verbose output
   poetry run pytest -v

Test Structure
~~~~~~~~~~~~~

.. code-block:: text

   tests/
   ├── conftest.py                    # Test configuration and fixtures
   ├── test_ai_integration.py         # AI service integration tests
   ├── test_api_endpoints.py          # API endpoint tests
   ├── test_integration.py            # Integration tests
   └── test_utility_functions.py      # Utility function tests

Test Categories
~~~~~~~~~~~~~~

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **API Tests**: Test HTTP endpoints
4. **AI Integration Tests**: Test external AI services

Writing Tests
~~~~~~~~~~~~

Example test structure:

.. code-block:: python

   import pytest
   from main import load_questions, save_questions

   def test_load_questions_empty_file(tmp_path):
       """Test loading questions from empty file."""
       # Test implementation
       pass

   def test_save_questions_success(tmp_path):
       """Test saving questions successfully."""
       # Test implementation
       pass

Test Fixtures
~~~~~~~~~~~~

Common fixtures in `conftest.py`:

.. code-block:: python

   @pytest.fixture
   def sample_questions():
       """Provide sample question data for tests."""
       return [
           {
               "id": 1,
               "question_text": "Test question?",
               "answers": [{"id": 1, "text": "Answer 1", "weight": 100}]
           }
       ]

   @pytest.fixture
   def mock_canvas_api(httpx_mock):
       """Mock Canvas API responses."""
       # Mock implementation
       pass

Documentation
------------

Building Documentation
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install Sphinx dependencies
   pip install sphinx sphinx-rtd-theme

   # Build documentation
   cd docs
   make html

   # View documentation
   open _build/html/index.html

Documentation Structure
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   docs/
   ├── conf.py              # Sphinx configuration
   ├── index.rst            # Main documentation page
   ├── modules.rst          # Auto-generated module docs
   ├── api.rst              # API documentation
   ├── installation.rst     # Installation guide
   ├── usage.rst            # Usage guide
   ├── configuration.rst    # Configuration guide
   └── development.rst      # This development guide

Docstring Standards
~~~~~~~~~~~~~~~~~~

Follow Google-style docstrings:

.. code-block:: python

   def function_name(param1: str, param2: int = 0) -> bool:
       """Short description of function.

       Longer description if needed.

       Args:
           param1: Description of param1
           param2: Description of param2, defaults to 0

       Returns:
           Description of return value

       Raises:
           ValueError: When something goes wrong

       Note:
           Additional notes about the function
       """
       pass

Development Workflow
-------------------

Feature Development
~~~~~~~~~~~~~~~~~~

1. **Create feature branch**

   .. code-block:: bash

      git checkout -b feature/new-feature

2. **Make changes**

   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Run tests and checks**

   .. code-block:: bash

      poetry run pytest
      poetry run black .
      poetry run isort .
      poetry run flake8 .

4. **Commit changes**

   .. code-block:: bash

      git add .
      git commit -m "Add new feature: description"

5. **Push and create pull request**

   .. code-block:: bash

      git push origin feature/new-feature

Bug Fixes
~~~~~~~~~

1. **Create bug fix branch**

   .. code-block:: bash

      git checkout -b fix/bug-description

2. **Write failing test**

   - Add test that reproduces the bug
   - Ensure test fails initially

3. **Fix the bug**

   - Implement the fix
   - Ensure all tests pass

4. **Update documentation**

   - Update relevant documentation
   - Add any new configuration options

Code Review
----------

Pull Request Guidelines
~~~~~~~~~~~~~~~~~~~~~~

1. **Clear description**: Explain what the PR does and why
2. **Tests included**: All new code should have tests
3. **Documentation updated**: Update docs for new features
4. **Style compliance**: Code should pass all style checks
5. **No breaking changes**: Unless explicitly noted

Review Checklist
~~~~~~~~~~~~~~~

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security issues introduced
- [ ] Performance impact considered
- [ ] Error handling is appropriate

Debugging
---------

Logging
~~~~~~~

The application uses structured logging:

.. code-block:: python

   import logging
   logger = logging.getLogger(__name__)

   logger.info("Operation completed successfully")
   logger.warning("Non-critical issue occurred")
   logger.error("Error occurred", exc_info=True)
   logger.debug("Detailed debug information")

Debug Endpoints
~~~~~~~~~~~~~~

Use built-in debug endpoints:

- `/debug/config`: Check configuration status
- `/debug/ollama-test`: Test Ollama connection
- `/debug/question/{id}`: Debug specific question

Development Tools
----------------

IDE Configuration
~~~~~~~~~~~~~~~~

VS Code settings (`.vscode/settings.json`):

.. code-block:: json

   {
     "python.defaultInterpreterPath": "./.venv/bin/python",
     "python.formatting.provider": "black",
     "python.linting.enabled": true,
     "python.linting.flake8Enabled": true,
     "python.testing.pytestEnabled": true,
     "python.testing.pytestArgs": ["tests"]
   }

Docker Development
~~~~~~~~~~~~~~~~~

For containerized development:

.. code-block:: dockerfile

   FROM python:3.11-slim

   WORKDIR /app
   COPY pyproject.toml poetry.lock ./
   RUN pip install poetry && poetry install

   COPY . .
   CMD ["poetry", "run", "dev"]

Performance Optimization
-----------------------

Profiling
~~~~~~~~~

Use cProfile for performance analysis:

.. code-block:: bash

   python -m cProfile -o profile.stats main.py
   python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"

Memory Profiling
~~~~~~~~~~~~~~~

Use memory_profiler for memory analysis:

.. code-block:: python

   from memory_profiler import profile

   @profile
   def memory_intensive_function():
       # Function implementation
       pass

Caching
~~~~~~~

Consider caching for expensive operations:

.. code-block:: python

   from functools import lru_cache

   @lru_cache(maxsize=128)
   def expensive_operation(param):
       # Expensive computation
       pass

Security Considerations
----------------------

Input Validation
~~~~~~~~~~~~~~~

Always validate user input:

.. code-block:: python

   from pydantic import BaseModel, validator

   class UserInput(BaseModel):
       text: str

       @validator('text')
       def validate_text(cls, v):
           if len(v) > 1000:
               raise ValueError('Text too long')
           return v

API Security
~~~~~~~~~~~

- Validate all API inputs
- Use proper HTTP status codes
- Implement rate limiting
- Log security events

Dependency Management
--------------------

Updating Dependencies
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Update all dependencies
   poetry update

   # Update specific dependency
   poetry update fastapi

   # Check for security vulnerabilities
   poetry run safety check

Security Scanning
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install safety
   pip install safety

   # Check for vulnerabilities
   safety check

Deployment
----------

Development Deployment
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Development server
   poetry run dev

   # Production-like server
   poetry run start

Production Deployment
~~~~~~~~~~~~~~~~~~~~

1. **Environment setup**

   .. code-block:: bash

      export CANVAS_BASE_URL="https://your-institution.instructure.com"
      export CANVAS_API_TOKEN="your_token"
      # ... other environment variables

2. **Service configuration**

   .. code-block:: ini

      [Unit]
      Description=Canvas Quiz Manager
      After=network.target

      [Service]
      Type=simple
      User=www-data
      WorkingDirectory=/path/to/app
      ExecStart=/path/to/poetry run start
      Restart=always

      [Install]
      WantedBy=multi-user.target

Monitoring
----------

Health Checks
~~~~~~~~~~~~

Implement health check endpoints:

.. code-block:: python

   @app.get("/health")
   async def health_check():
       return {"status": "healthy", "timestamp": datetime.now()}

Metrics
~~~~~~~

Consider adding metrics collection:

.. code-block:: python

   from prometheus_client import Counter, Histogram

   request_count = Counter('http_requests_total', 'Total HTTP requests')
   request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

Contributing
------------

Contributing Guidelines
~~~~~~~~~~~~~~~~~~~~~~

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Update documentation**
6. **Submit a pull request**

Code of Conduct
~~~~~~~~~~~~~~~

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow project guidelines

Getting Help
-----------

- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the docs directory
- **Logs**: Review `canvas_app.log` for errors
