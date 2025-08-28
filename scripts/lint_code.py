#!/usr/bin/env python3
"""
Code Linting Script

This module provides comprehensive code quality checking for the Canvas Quiz 
Manager codebase using multiple tools including Black, Flake8, and isort. It 
ensures consistent code formatting, style compliance, and proper import 
organization.

The script supports both checking and automatic fixing of code quality issues,
providing a unified interface for maintaining high code standards.

Key Features:
- Black code formatting and checking
- Flake8 style and error checking
- Isort import sorting and organization
- Automatic fixing capabilities
- Comprehensive error reporting
- Helpful fixing guidance

Author: Robert Fentress <learn@vt.edu>
Version: 0.2.0
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """
    Run a command and handle the result.

    This function executes a shell command and provides formatted output
    for both success and failure cases.

    Args:
        command: The shell command to execute
        description: Human-readable description of what the command does

    Returns:
        bool: True if command succeeded, False if it failed

    Note:
        The function captures both stdout and stderr for comprehensive
        error reporting.
    """
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        print(f"✅ {description} passed")
        if result.stdout.strip():
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def check_black():
    """
    Check code formatting with Black.

    This function runs Black in check mode to verify that all Python files
    in the current directory are properly formatted according to Black's
    style guidelines. It provides detailed output showing what changes
    would be made.

    Returns:
        bool: True if all files are properly formatted, False otherwise

    Raises:
        No exceptions are raised. All errors are handled and reported.

    Note:
        This function only checks formatting without making any changes.
        Use format_code() to actually format the files. The function
        shows a diff of what changes would be made if formatting is needed.

    Example:
        >>> is_formatted = check_black()
        >>> if is_formatted:
        ...     print("All files are properly formatted")
        ... else:
        ...     print("Some files need formatting - run format_code() to fix")
        🔍 Black code formatting check...
        ✅ Black code formatting check passed
        All files are properly formatted

    See Also:
        :func:`run_command`: Helper function for executing shell commands
        :func:`format_code`: Actually format the code (in format_code.py)
    """
    return run_command("black --check --diff .", "Black code formatting check")


def check_flake8():
    """
    Check code style with Flake8.

    This function runs Flake8 to check for style violations and errors
    in Python code. It focuses on critical errors (E9, F63, F7, F82)
    that indicate syntax errors or serious code issues.

    Returns:
        bool: True if no critical errors found, False otherwise

    Note:
        The function checks for:
        - E9: Syntax errors
        - F63: Invalid syntax in f-strings
        - F7: SyntaxError in f-string
        - F82: Undefined name in f-string
    """
    return run_command(
        ("flake8 . --count --select=E9,F63,F7,F82 " "--show-source --statistics"),
        "Flake8 error checking",
    )


def check_isort():
    """
    Check import sorting with isort.

    This function runs isort in check mode to verify that all import
    statements in Python files are properly sorted and organized
    according to isort's configuration.

    Returns:
        bool: True if all imports are properly sorted, False otherwise

    Note:
        This function only checks import sorting without making changes.
        Use format_code() to actually sort the imports.
    """
    return run_command("isort --check-only --diff .", "Isort import sorting check")


def format_code():
    """
    Format code with Black and isort.

    This function automatically formats all Python files in the current
    directory using Black for code formatting and isort for import
    sorting. It modifies files in place to fix formatting issues.

    Returns:
        bool: True if formatting was successful, False otherwise

    Note:
        This function modifies files in place. Make sure you have
        committed your changes before running this function.

    Example:
        >>> format_code()
        🎨 Formatting code...
        🔍 Black code formatting...
        ✅ Black code formatting passed
        ✅ Code formatted with Black
        🔍 Isort import sorting...
        ✅ Isort import sorting passed
        ✅ Imports sorted with isort
        True
    """
    print("🎨 Formatting code...")

    # Format with Black
    if run_command("black .", "Black code formatting"):
        print("✅ Code formatted with Black")
    else:
        print("❌ Black formatting failed")
        return False

    # Sort imports with isort
    if run_command("isort .", "Isort import sorting"):
        print("✅ Imports sorted with isort")
    else:
        print("❌ Isort sorting failed")
        return False

    return True


def main():
    """
    Main function for the linting script.

    This function provides the command-line interface for the linting script.
    It supports multiple modes of operation including checking only,
    formatting only, or both checking and formatting.

    Command-line Arguments:
        --format: Enable code formatting in addition to linting
        --check-only: Only run checks, don't format code

    Exit Codes:
        0: All checks passed successfully
        1: One or more checks failed

    Examples:
        # Run all linting checks
        poetry run lint

        # Run checks and format code
        poetry run lint --format

        # Only check code quality
        poetry run lint --check-only
    """
    import argparse
    import os

    # Check if this script is being run as the 'format' command
    # This allows the same script to be used for both 'lint' and 'format'
    # commands
    script_name = os.path.basename(sys.argv[0])
    is_format_command = script_name == "format" or "format" in script_name

    parser = argparse.ArgumentParser(
        description="Lint and format Canvas Quiz Manager code"
    )
    parser.add_argument(
        "--format", action="store_true", help="Format code in addition to linting"
    )
    parser.add_argument(
        "--check-only", action="store_true", help="Only check code, don't format"
    )

    args = parser.parse_args()

    # If running as format command, automatically enable formatting
    if is_format_command:
        args.format = True

    print("🔍 Canvas Quiz Manager - Code Quality Check")
    print("=" * 50)

    # Check if we're in the right directory
    project_root = Path(__file__).parent.parent
    if not (project_root / "src" / "question_app" / "main.py").exists():
        print("❌ Error: main.py not found. Please run from project root.")
        sys.exit(1)

    success = True

    # Run linting checks
    if not check_black():
        success = False

    if not check_flake8():
        success = False

    if not check_isort():
        success = False

    # Format code if requested
    if args.format and not args.check_only:
        if format_code():
            print("✅ Code formatting completed")
        else:
            success = False

    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All code quality checks passed!")
        sys.exit(0)
    else:
        print("❌ Some code quality checks failed.")
        print(
            "💡 Run 'poetry run lint --format' to automatically fix "
            "formatting issues."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
