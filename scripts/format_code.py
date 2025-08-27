#!/usr/bin/env python3
"""
Code Formatting Script

This module provides code formatting for the Canvas Quiz Manager codebase
using Black and isort. It focuses solely on formatting without linting checks.

Key Features:
- Black code formatting
- Isort import sorting and organization
- Automatic fixing capabilities
- Comprehensive error reporting

Author: Bryce Kayanuma <BrycePK@vt.edu>
Version: 0.1.0
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """
    Run a command and handle the result.

    This function executes a shell command and provides formatted output
    for both success and failure cases. It captures all output streams
    and provides detailed error reporting for debugging.

    Args:
        command (str): The shell command to execute
        description (str): Human-readable description of what the command does

    Returns:
        bool: True if command succeeded, False if it failed

    Raises:
        No exceptions are raised. All errors are captured and reported.

    Note:
        The function captures both stdout and stderr for comprehensive
        error reporting. Commands are executed with shell=True for
        compatibility with complex commands.

    Example:
        >>> success = run_command("python --version", "Check Python version")
        >>> if success:
        ...     print("Python version check passed")
        ... else:
        ...     print("Python version check failed")
        🔍 Check Python version...
        ✅ Check Python version passed
        Python version check passed

    See Also:
        :func:`format_code`: Main formatting function that uses this helper
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


def format_code():
    """
    Format code with Black and isort.

    This function orchestrates the code formatting process by running Black
    for code formatting and isort for import sorting. It provides comprehensive
    error reporting and ensures both tools complete successfully.

    Returns:
        bool: True if all formatting operations succeeded, False otherwise

    Raises:
        No exceptions are raised. All errors are handled and reported.

    Note:
        The function runs Black first for code formatting, then isort for
        import organization. Both tools must succeed for the function to
        return True.

    Example:
        >>> success = format_code()
        >>> if success:
        ...     print("Code formatting completed successfully")
        ... else:
        ...     print("Code formatting failed - check output above")
        🎨 Formatting code...
        🔍 Black code formatting...
        ✅ Black code formatting passed
        🔍 Isort import sorting...
        ✅ Isort import sorting passed
        Code formatting completed successfully

    See Also:
        :func:`run_command`: Helper function for executing shell commands
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
    """Main function."""
    print("🎨 Canvas Quiz Manager - Code Formatting")
    print("=" * 50)

    # Check if we're in the right directory
    project_root = Path(__file__).parent.parent
    if not (project_root / "src" / "question_app" / "main.py").exists():
        print("❌ Error: main.py not found. Please run from project root.")
        sys.exit(1)

    # Format code
    if format_code():
        print("\n" + "=" * 50)
        print("🎉 Code formatting completed successfully!")
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("❌ Code formatting failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
