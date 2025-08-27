Development Tools
=================

This section documents the various development tools and scripts available for
the Canvas Quiz Manager project. These tools help maintain code quality,
run tests, and manage documentation.

Code Quality Tools
-----------------

Linting and Formatting
~~~~~~~~~~~~~~~~~~~~~

The project includes comprehensive code quality tools accessible via Poetry scripts:

.. code-block:: bash

   # Run all code quality checks
   poetry run lint

   # Check code quality without fixing
   poetry run lint --check-only

   # Format code automatically
   poetry run lint --format

The linting system includes:

- **Black**: Code formatting and style consistency
- **Flake8**: Style guide enforcement and error detection
- **Isort**: Import statement organization and sorting

Type Checking
~~~~~~~~~~~~

Static type checking is available using multiple tools:

.. code-block:: bash

   # Run mypy type checking
   poetry run type-check

   # Run pyright type checking
   poetry run type-check --tool pyright

   # Run both type checkers
   poetry run type-check --tool both

   # Check for missing type annotations
   poetry run type-check --check-annotations

The type checking system provides:

- **mypy**: Industry-standard Python type checker with strict mode
- **pyright**: Microsoft's fast type checker (used by VS Code)
- **Custom Annotation Detection**: Finds functions missing type hints

Testing Tools
------------

Comprehensive Testing
~~~~~~~~~~~~~~~~~~~~

The project includes a unified test runner with multiple options:

.. code-block:: bash

   # Run all tests
   poetry run test

   # Run tests with coverage
   poetry run test --coverage

   # Run specific test types
   poetry run test --type unit
   poetry run test --type integration
   poetry run test --type ai
   poetry run test --type api

   # Advanced testing options
   poetry run test --verbose
   poetry run test --debug
   poetry run test --parallel
   poetry run test --watch
   poetry run test --fast

Test Features:

- **Multiple Test Types**: Unit, integration, AI, and API tests
- **Coverage Reporting**: HTML and terminal coverage reports
- **Parallel Execution**: Speed up test execution
- **Watch Mode**: Auto-rerun tests on file changes
- **Debug Output**: Detailed error information
- **Smart Parsing**: Enhanced test result display

Documentation Tools
------------------

Documentation Building
~~~~~~~~~~~~~~~~~~~~~

Multiple options for building and serving documentation:

.. code-block:: bash

   # Build documentation (requires make)
   poetry run docs

   # Build documentation (no make required)
   poetry run docs-simple

   # Build and serve documentation in one command
   poetry run docs-serve

   # Serve existing documentation
   poetry run serve-docs

Documentation Features:

- **Sphinx Integration**: Full Sphinx documentation system
- **Read the Docs Theme**: Professional documentation appearance
- **Auto-generation**: Automatic API and module documentation
- **Local Serving**: Easy local documentation viewing
- **Browser Integration**: Automatic browser opening

Documentation Server
~~~~~~~~~~~~~~~~~~~

The documentation server provides local hosting with enhanced features:

.. code-block:: bash

   # Basic serving
   poetry run serve-docs

   # Custom port and host
   poetry run serve-docs --port 8080 --host 0.0.0.0

   # Skip building (assume docs exist)
   poetry run serve-docs --no-build

   # Don't auto-open browser
   poetry run serve-docs --no-browser

Server Features:

- **Automatic Building**: Builds docs if they don't exist
- **Real-time Logging**: Shows request activity
- **Browser Integration**: Auto-opens default browser
- **Configurable**: Custom port and host settings
- **Graceful Shutdown**: Clean server termination

Script Details
-------------

serve_docs.py
~~~~~~~~~~~~

The documentation server script provides local HTTP serving of Sphinx documentation.

**Key Functions:**

- ``build_documentation()``: Automatically builds documentation if needed
- ``start_server()``: Starts HTTP server with browser integration
- ``DocumentationHandler``: Custom request handler with logging

**Features:**

- Multiple build method support (sphinx-build, make)
- Automatic browser opening
- Real-time request logging
- Graceful error handling
- Configurable port and host

type_check.py
~~~~~~~~~~~~

The type checking script provides comprehensive static type analysis.

**Key Functions:**

- ``run_mypy()``: Executes mypy with strict settings
- ``run_pyright()``: Executes pyright type checking
- ``check_type_annotations()``: Finds missing type hints

**Features:**

- Multiple type checker support
- Custom annotation detection
- Comprehensive error reporting
- Installation guidance
- Configurable checking options

run_tests.py
~~~~~~~~~~~

The test runner script provides unified testing interface with enhanced features.

**Key Functions:**

- ``run_command()``: Enhanced subprocess execution with parsing
- ``main()``: Command-line interface and test orchestration

**Features:**

- Multiple test type support
- Coverage integration
- Parallel execution
- Watch mode
- Smart output parsing
- Helpful error guidance

lint_code.py
~~~~~~~~~~~

The linting script provides comprehensive code quality checking.

**Key Functions:**

- ``run_command()``: Shell command execution with error handling
- ``check_black()``: Black code formatting checks
- ``check_flake8()``: Flake8 style checking
- ``check_isort()``: Import sorting verification
- ``format_code()``: Automatic code formatting

**Features:**

- Multiple linting tools
- Automatic fixing capabilities
- Comprehensive error reporting
- Installation guidance
- Configurable options

Integration
----------

CI/CD Integration
~~~~~~~~~~~~~~~~

These tools are designed to integrate seamlessly with CI/CD pipelines:

.. code-block:: bash

   # Full quality check pipeline
   poetry run lint && poetry run type-check && poetry run test

   # Fast feedback loop
   poetry run lint --format && poetry run test --fast

   # Documentation pipeline
   poetry run docs-simple && poetry run serve-docs --no-build

Development Workflow
~~~~~~~~~~~~~~~~~~~

Recommended development workflow:

1. **Code Quality**: Run linting and type checking
2. **Testing**: Execute relevant test suites
3. **Documentation**: Build and verify documentation
4. **Integration**: Run full pipeline before commits

Example workflow:

.. code-block:: bash

   # Quick development cycle
   poetry run lint --format
   poetry run type-check
   poetry run test --type unit --fast

   # Full quality assurance
   poetry run lint
   poetry run type-check --tool both
   poetry run test --coverage
   poetry run docs-simple

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

**Linting Errors:**

- Run ``poetry run lint --format`` to auto-fix formatting issues
- Check for missing dependencies with ``poetry install``
- Verify Python version compatibility

**Type Checking Issues:**

- Install missing type checkers: ``poetry add --group dev mypy pyright``
- Add type annotations to functions and variables
- Use ``poetry run type-check --check-annotations`` to find missing types

**Test Failures:**

- Check environment variables and configuration
- Run ``poetry run test --debug`` for detailed output
- Verify dependencies are installed correctly

**Documentation Issues:**

- Ensure Sphinx is installed: ``poetry add --group dev sphinx sphinx-rtd-theme``
- Check for syntax errors in RST files
- Verify all referenced modules are importable

Getting Help
~~~~~~~~~~~

For issues with development tools:

1. Check the tool's help output: ``poetry run <tool> --help``
2. Review the tool's documentation in this section
3. Check the project's issue tracker
4. Verify all dependencies are properly installed
