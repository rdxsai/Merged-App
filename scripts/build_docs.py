#!/usr/bin/env python3
"""
Documentation Build Script

This module provides a Python interface for building Sphinx documentation
using the traditional make-based approach. It serves as a wrapper around
the standard Sphinx build process with enhanced error handling and output.

The script provides a unified interface for building documentation with
proper error handling, user-friendly output formatting, and integration
with Poetry scripts.

Key Features:
- Make-based documentation building
- Enhanced error handling and reporting
- User-friendly output formatting
- Poetry script integration
- Automatic directory management

Author: Bryce Kayanuma <BrycePK@vt.edu>
Version: 0.1.0
"""

import os
import subprocess
import sys
from pathlib import Path


def build_documentation() -> bool:
    """
    Build the Sphinx documentation using make.

    This function builds the Sphinx documentation using the traditional
    make-based approach. It handles directory management, error handling,
    and provides user-friendly output.

    Returns:
        bool: True if documentation was built successfully, False otherwise

    Note:
        The function requires the 'make' command to be available on the system.
        If make is not available, consider using build_docs_simple.py instead.
    """
    print("📚 Building Canvas Quiz Manager Documentation")
    print("=" * 50)

    # Get the project root directory
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"

    if not docs_dir.exists():
        print("❌ Documentation directory not found!")
        return False

    # Change to docs directory
    os.chdir(docs_dir)

    try:
        # Build HTML documentation
        print("🔨 Building HTML documentation...")
        subprocess.run(["make", "html"], capture_output=True, text=True, check=True)

        print("✅ Documentation built successfully!")
        output_path = docs_dir / "_build" / "html" / "index.html"
        print(f"📁 Output location: {output_path}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print(
            "❌ 'make' command not found. Please install make or use "
            "sphinx-build directly."
        )
        return False


def main() -> None:
    """
    Main function for the documentation build script.

    This function orchestrates the documentation building process and
    provides appropriate exit codes and user feedback.

    Note:
        The function exits with status code 1 if documentation building fails.
    """
    success = build_documentation()

    if success:
        print("\n🎉 Documentation build completed successfully!")
        print(
            "📖 Open docs/_build/html/index.html in your browser to "
            "view the documentation."
        )
    else:
        print("\n❌ Documentation build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
