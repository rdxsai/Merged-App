#!/usr/bin/env python3
"""
Documentation Build Script (Simple)

This module provides a Python interface for building Sphinx documentation
using sphinx-build directly, without requiring the make command. This makes
it more portable and easier to use in environments where make is not available.

The script provides a unified interface for building documentation with
proper error handling, user-friendly output formatting, and integration
with Poetry scripts.

Key Features:
- Direct sphinx-build integration (no make required)
- Enhanced error handling and reporting
- User-friendly output formatting
- Poetry script integration
- Automatic directory management
- Cross-platform compatibility

Author: Robert Fentress <learn@vt.edu>
Version: 0.1.0
"""

import os
import subprocess
import sys
from pathlib import Path


def build_documentation() -> bool:
    """
    Build the Sphinx documentation using sphinx-build directly.

    This function builds the Sphinx documentation using sphinx-build directly,
    without requiring the make command. This provides better cross-platform
    compatibility and simpler dependency requirements.

    Returns:
        bool: True if documentation was built successfully, False otherwise

    Note:
        The function requires sphinx-build to be available in the PATH.
        This is typically installed with Sphinx: pip install sphinx
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
        # Build HTML documentation using sphinx-build directly
        print("🔨 Building HTML documentation...")
        subprocess.run(
            ["sphinx-build", "-b", "html", ".", "_build/html"],
            capture_output=True,
            text=True,
            check=True,
        )

        print("✅ Documentation built successfully!")
        output_path = docs_dir / "_build" / "html" / "index.html"
        print(f"📁 Output location: {output_path}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ 'sphinx-build' command not found. Please install Sphinx:")
        print("   pip install sphinx sphinx-rtd-theme")
        return False


def main() -> None:
    """
    Main function for the simple documentation build script.

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
