# Canvas Quiz Manager Documentation

This directory contains the Sphinx documentation for the Canvas Quiz Manager application.

## Building the Documentation

### Prerequisites

Install the required dependencies:

```bash
poetry install
```

### Build Commands

From the project root:

```bash
# Build HTML documentation (requires make)
poetry run docs

# Build HTML documentation (no make required)
poetry run docs-simple

# Or manually from the docs directory
cd docs
make html

# Or using sphinx-build directly
cd docs
sphinx-build -b html . _build/html
```

### Viewing the Documentation

After building, you can view the documentation in several ways:

````bash
# Build and serve documentation in one command (recommended)
poetry run docs-serve

# Or serve existing documentation
poetry run serve-docs

# Or manually open the HTML file
open docs/_build/html/index.html

## Code Quality Tools

```bash
# Format code (recommended)
poetry run format

# Run linting and formatting checks
poetry run lint

# Run type checking
poetry run type-check

# Check for missing type annotations
poetry run type-check --check-annotations

# Run tests
poetry run test

# Run tests with coverage
poetry run test --coverage

# Run specific test types
poetry run test --type unit
poetry run test --type integration
poetry run test --type ai
poetry run test --type api
````

````

The `serve-docs` command will:

- Automatically build documentation if needed
- Start a local HTTP server
- Open your browser to the documentation
- Show real-time request logging

## Documentation Structure

- `conf.py` - Sphinx configuration
- `index.rst` - Main documentation page
- `modules.rst` - Auto-generated module documentation
- `api.rst` - API reference
- `installation.rst` - Installation guide
- `usage.rst` - Usage guide
- `configuration.rst` - Configuration guide
- `development.rst` - Development guide

## Adding Documentation

1. Create new `.rst` files for new sections
2. Add them to the table of contents in `index.rst`
3. Follow the existing docstring standards in the code
4. Build and test the documentation

## Docstring Standards

Follow Google-style docstrings in the code:

```python
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
````

## Auto-generating Documentation

The documentation automatically includes:

- All public functions and classes from `main.py`
- API endpoint documentation
- Pydantic model documentation
- Test module documentation

## Theme

The documentation uses the Read the Docs theme for a clean, professional appearance.
