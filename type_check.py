#!/usr/bin/env python3
"""
Type Checking Script

This module provides comprehensive static type checking for the Canvas Quiz Manager
codebase using multiple tools including mypy and pyright. It ensures type safety
and helps catch potential type-related issues before runtime.

The script supports multiple type checking tools, custom annotation detection,
and provides helpful guidance for fixing type issues.

Key Features:
- Multiple type checker support (mypy, pyright)
- Custom annotation detection
- Comprehensive error reporting
- Helpful fixing suggestions
- Configurable checking options

Author: Bryce Kayanuma <BrycePK@vt.edu>
Version: 0.1.0
"""

import subprocess
import sys
from pathlib import Path


def run_mypy() -> bool:
    """
    Run mypy type checking.

    This function executes mypy with strict settings to perform comprehensive
    static type checking on the codebase. It uses strict mode for maximum
    type safety detection.

    Returns:
        bool: True if mypy check passed, False if it failed or mypy not found

    Note:
        The function provides detailed error output and installation guidance
        if mypy is not available.
    """
    print("🔍 Running mypy type checking...")

    try:
        # Run mypy with strict settings
        result = subprocess.run(
            [
                "mypy",
                "--strict",
                "--ignore-missing-imports",
                "--show-error-codes",
                "--show-column-numbers",
                "--pretty",
                ".",
            ],
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception, we'll handle the output
        )

        if result.returncode == 0:
            print("✅ Type checking passed!")
            if result.stdout.strip():
                print(result.stdout)
            return True
        else:
            print("❌ Type checking failed!")
            if result.stdout.strip():
                print("STDOUT:", result.stdout)
            if result.stderr.strip():
                print("STDERR:", result.stderr)
            return False

    except FileNotFoundError:
        print("❌ mypy not found. Please install it with:")
        print("   pip install mypy")
        print("   or")
        print("   poetry add --group dev mypy")
        return False
    except Exception as e:
        print(f"❌ Error running mypy: {e}")
        return False


def run_pyright() -> bool:
    """
    Run pyright type checking (alternative to mypy).

    This function executes pyright to perform static type checking on the
    codebase. Pyright is Microsoft's fast type checker used by VS Code.

    Returns:
        bool: True if pyright check passed, False if it failed or pyright not found

    Note:
        The function provides detailed error output and installation guidance
        if pyright is not available.
    """
    print("🔍 Running pyright type checking...")

    try:
        # Run pyright
        result = subprocess.run(
            ["pyright", "--outputformat=text", "."],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            print("✅ Pyright type checking passed!")
            if result.stdout.strip():
                print(result.stdout)
            return True
        else:
            print("❌ Pyright type checking failed!")
            if result.stdout.strip():
                print("STDOUT:", result.stdout)
            if result.stderr.strip():
                print("STDERR:", result.stderr)
            return False

    except FileNotFoundError:
        print("❌ pyright not found. Please install it with:")
        print("   pip install pyright")
        print("   or")
        print("   poetry add --group dev pyright")
        return False
    except Exception as e:
        print(f"❌ Error running pyright: {e}")
        return False


def check_type_annotations():
    """Check for missing type annotations using custom script."""
    print("🔍 Checking for missing type annotations...")

    try:
        # Use a simple grep-based approach to find functions without type hints
        result = subprocess.run(
            ["grep", "-r", "--include=*.py", "-n", "def [^(]*([^)]*):", "."],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            missing_annotations = []

            for line in lines:
                if line and not any(
                    skip in line
                    for skip in [
                        "__pycache__",
                        ".venv",
                        "tests/",
                        "docs/",
                        "def __init__",
                        "def __str__",
                        "def __repr__",
                    ]
                ):
                    missing_annotations.append(line)

            if missing_annotations:
                print("⚠️  Found functions that may be missing type annotations:")
                for annotation in missing_annotations[:10]:  # Show first 10
                    print(f"   {annotation}")
                if len(missing_annotations) > 10:
                    print(f"   ... and {len(missing_annotations) - 10} more")
                return False
            else:
                print("✅ No obvious missing type annotations found")
                return True
        else:
            print("⚠️  Could not check for missing annotations")
            return True

    except Exception as e:
        print(f"⚠️  Error checking annotations: {e}")
        return True


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Type check Canvas Quiz Manager code")
    parser.add_argument(
        "--tool",
        choices=["mypy", "pyright", "both"],
        default="mypy",
        help="Type checking tool to use (default: mypy)",
    )
    parser.add_argument(
        "--check-annotations",
        action="store_true",
        help="Also check for missing type annotations",
    )

    args = parser.parse_args()

    print("🔍 Canvas Quiz Manager - Type Checking")
    print("=" * 50)

    # Check if we're in the right directory
    project_root = Path(__file__).parent
    if not (project_root / "main.py").exists():
        print("❌ Error: main.py not found. Please run from project root.")
        sys.exit(1)

    success = True

    # Run type checking based on tool choice
    if args.tool in ["mypy", "both"]:
        if not run_mypy():
            success = False

    if args.tool in ["pyright", "both"]:
        if not run_pyright():
            success = False

    # Check for missing annotations if requested
    if args.check_annotations:
        if not check_type_annotations():
            success = False

    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All type checking passed!")
        sys.exit(0)
    else:
        print("❌ Some type checking failed.")
        print("💡 Tips for fixing type issues:")
        print("   - Add type hints to function parameters and return values")
        print("   - Use Optional[Type] for parameters that can be None")
        print("   - Import types from typing module when needed")
        print(
            "   - Run 'poetry run type-check --check-annotations' "
            "to find missing annotations"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
