Core Modules
===========

This document describes the core modules that provide the foundation for the Canvas Quiz Manager application.

Overview
--------

The core modules are located in ``src/question_app/core/`` and provide centralized configuration,
logging, and application setup functionality. These modules ensure consistent behavior across
the entire application and provide a clean separation of concerns.

Core Configuration Module
------------------------

**File**: ``src/question_app/core/config.py``

The configuration module centralizes all environment variable loading and provides validation
methods for the application's configuration.

Key Features:
- Centralized environment variable loading
- Configuration validation methods
- Helper methods for checking missing configuration
- Type-safe configuration access

Example Usage:
.. code-block:: python

    from question_app.core import config
    
    # Access configuration values
    canvas_url = config.CANVAS_BASE_URL
    azure_endpoint = config.AZURE_OPENAI_ENDPOINT
    
    # Validate configuration
    if config.validate_canvas_config():
        print("Canvas configuration is complete")
    
    # Get missing configuration variables
    missing = config.get_missing_azure_openai_configs()
    if missing:
        print(f"Missing Azure OpenAI config: {missing}")

Core Logging Module
------------------

**File**: ``src/question_app/core/logging.py``

The logging module provides centralized logging configuration and setup for the application.

Key Features:
- Centralized logging configuration
- Consistent logging format across the application
- Helper functions for getting logger instances
- Configurable log levels and handlers

Example Usage:
.. code-block:: python

    from question_app.core import get_logger
    
    # Get a logger instance
    logger = get_logger(__name__)
    
    # Use the logger
    logger.info("Application started")
    logger.error("An error occurred")

Core App Setup Module
--------------------

**File**: ``src/question_app/core/app.py``

The app setup module handles FastAPI application creation and configuration.

Key Features:
- FastAPI application creation
- Router registration
- Template setup
- Static file mounting
- Middleware configuration

Example Usage:
.. code-block:: python

    from question_app.core import create_app, register_routers
    
    # Create the application
    app = create_app()
    
    # Register all routers
    register_routers(app)

Core Module Exports
------------------

**File**: ``src/question_app/core/__init__.py``

The core module exports provide a clean API for accessing core functionality.

Available Exports:
- ``config``: Configuration instance
- ``Config``: Configuration class
- ``setup_logging``: Logging setup function
- ``get_logger``: Logger getter function
- ``create_app``: App creation function
- ``register_routers``: Router registration function
- ``get_templates``: Template getter function

Example Usage:
.. code-block:: python

    from question_app.core import (
        config,
        get_logger,
        create_app,
        register_routers
    )

Benefits of Core Modules
-----------------------

1. **Centralized Configuration**: All environment variables managed in one place
2. **Consistent Validation**: Configuration validation is standardized across the app
3. **Improved Maintainability**: Changes to configuration only need to be made in one place
4. **Better Testing**: Configuration can be easily mocked and tested
5. **Clean Architecture**: Clear separation of concerns
6. **Reduced Duplication**: Eliminates duplicate configuration code across modules

Migration Guide
--------------

If you're updating existing code to use the core modules:

1. **Replace direct environment variable access**:
   .. code-block:: python

       # Old way
       import os
       canvas_url = os.getenv("CANVAS_BASE_URL")
       
       # New way
       from question_app.core import config
       canvas_url = config.CANVAS_BASE_URL

2. **Replace logging setup**:
   .. code-block:: python

       # Old way
       import logging
       logger = logging.getLogger(__name__)
       
       # New way
       from question_app.core import get_logger
       logger = get_logger(__name__)

3. **Update test patches**:
   .. code-block:: python

       # Old way
       with patch("question_app.api.canvas.CANVAS_BASE_URL", None):
       
       # New way
       with patch("question_app.core.config.Config.validate_canvas_config", return_value=False):
