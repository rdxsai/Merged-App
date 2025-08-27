#!/usr/bin/env python3
"""
Documentation Build and Serve Script

This module provides a convenient one-command solution for building and
serving Sphinx documentation locally. It combines the functionality of
build_docs_simple.py and serve_docs.py into a single, streamlined process.

The script automatically builds the documentation if needed and then starts
a local HTTP server to serve it, providing immediate access to the documentation
in a web browser.

Key Features:
- One-command build and serve
- Automatic documentation building
- Local HTTP server with browser integration
- Real-time request logging
- Graceful error handling
- Poetry script integration

Author: Bryce Kayanuma <BrycePK@vt.edu>
Version: 0.1.0
"""

import sys
from pathlib import Path

# Add the project root to the path so we can import our scripts
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup
from build_docs_simple import build_documentation  # noqa: E402
from serve_docs import start_server  # noqa: E402


def main() -> None:
    """
    Build and serve documentation in one command.

    This function orchestrates the complete documentation workflow by first
    building the documentation and then serving it locally. It provides
    a streamlined experience for documentation development and viewing.

    Note:
        The function exits with status code 1 if either building or serving fails.
    """
    print("📚 Canvas Quiz Manager - Build and Serve Documentation")
    print("=" * 60)

    # Build documentation
    print("🔨 Step 1: Building documentation...")
    if not build_documentation():
        print("❌ Failed to build documentation")
        sys.exit(1)

    print("✅ Documentation built successfully!")
    print()

    # Serve documentation
    print("🌐 Step 2: Starting documentation server...")
    if not start_server():
        print("❌ Failed to start server")
        sys.exit(1)


if __name__ == "__main__":
    main()
