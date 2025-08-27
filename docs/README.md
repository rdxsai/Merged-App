# Canvas Quiz Manager Documentation

This directory contains the Sphinx documentation for the Canvas Quiz Manager application.

## Overview

The documentation provides comprehensive guides for using and developing the Canvas Quiz Manager application, including:

- **API Reference**: Complete API documentation with examples
- **Installation Guide**: Step-by-step setup instructions
- **Usage Guide**: How to use the application features
- **Configuration Guide**: Environment and system configuration
- **Development Guide**: Contributing and development setup
- **API Examples**: Real-world usage examples and workflows
- **Troubleshooting**: Common issues and solutions

## Quick Start

### Prerequisites

Install the required dependencies:

```bash
poetry install
```

### Build and View Documentation

```bash
# Build and serve documentation in one command (recommended)
poetry run docs-serve

# Or build and serve separately
poetry run docs-simple
poetry run serve-docs
```

## Building the Documentation

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

```bash
# Build and serve documentation in one command (recommended)
poetry run docs-serve

# Or serve existing documentation
poetry run serve-docs

# Or manually open the HTML file
open docs/_build/html/index.html
```

The `serve-docs` command will:

- Automatically build documentation if needed
- Start a local HTTP server
- Open your browser to the documentation
- Show real-time request logging

## Documentation Structure

### Core Documentation Files

- `conf.py` - Sphinx configuration
- `index.rst` - Main documentation page with navigation
- `modules.rst` - Auto-generated module documentation

### User Guides

- `api.rst` - API reference documentation
- `api_examples.rst` - Comprehensive API usage examples
- `installation.rst` - Installation and setup guide
- `usage.rst` - Usage guide and tutorials
- `configuration.rst` - Configuration and environment setup
- `troubleshooting.rst` - Common issues and solutions

### Developer Documentation

- `development.rst` - Development setup and guidelines
- `development_tools.rst` - Development tool documentation
- `testing.rst` - Testing guide and test documentation

### Auto-generated Content

The documentation automatically includes:

- All public functions and classes from `main.py`
- API endpoint documentation
- Pydantic model documentation
- Test module documentation
- Development tool documentation

## Adding Documentation

### Creating New Documentation

1. Create new `.rst` files for new sections
2. Add them to the table of contents in `index.rst`
3. Follow the existing docstring standards in the code
4. Build and test the documentation

### Docstring Standards

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

    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True

    See Also:
        :func:`related_function`: Description of related function
    """
    pass
```

### Documentation Best Practices

1. **Use Clear Headings**: Structure content with proper heading hierarchy
2. **Include Examples**: Provide practical, runnable examples
3. **Cross-Reference**: Link related functions and sections
4. **Error Handling**: Document error scenarios and solutions
5. **Keep Updated**: Maintain documentation with code changes

## Documentation Features

### Auto-generation

The documentation automatically includes:

- All public functions and classes from `main.py`
- API endpoint documentation
- Pydantic model documentation
- Test module documentation
- Development tool documentation

### Cross-references

Use Sphinx cross-references to link related content:

- `:func:`function_name`` - Link to functions
- `:class:`ClassName`` - Link to classes
- `:doc:`page_name`` - Link to documentation pages

### Code Examples

Include executable code examples:

- Use `.. code-block:: python` for Python code
- Use `.. code-block:: bash` for shell commands
- Include expected output in examples

## Theme and Styling

The documentation uses the Read the Docs theme for a clean, professional appearance with:

- Responsive design for mobile and desktop
- Search functionality
- Table of contents navigation
- Syntax highlighting for code blocks
- Professional typography

## Maintenance

### Regular Tasks

1. **Update Examples**: Keep code examples current with API changes
2. **Review Cross-references**: Ensure links remain valid
3. **Test Builds**: Verify documentation builds successfully
4. **Update Structure**: Maintain logical organization as features grow

### Quality Checks

- Build documentation regularly to catch errors
- Test all code examples for accuracy
- Verify cross-references work correctly
- Ensure navigation structure is logical

## Troubleshooting

### Common Build Issues

1. **Missing Dependencies**: Run `poetry install` to install all requirements
2. **Import Errors**: Ensure Python path includes project root
3. **Theme Issues**: Verify sphinx-rtd-theme is installed
4. **Build Failures**: Check for syntax errors in RST files

### Getting Help

- Check the main project README for general setup
- Review the troubleshooting guide in the documentation
- Verify environment configuration
- Test individual components separately
