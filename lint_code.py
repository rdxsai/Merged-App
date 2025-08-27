#!/usr/bin/env python3
"""
Code Linting Script

This module provides comprehensive code quality checking for the Canvas Quiz Manager
codebase using multiple tools including Black, Flake8, and isort. It ensures
consistent code formatting, style compliance, and proper import organization.

The script supports both checking and automatic fixing of code quality issues,
providing a unified interface for maintaining high code standards.

Key Features:
- Black code formatting and checking
- Flake8 style and error checking
- Isort import sorting and organization
- Automatic fixing capabilities
- Comprehensive error reporting
- Helpful fixing guidance

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
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
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
    """Check code formatting with Black."""
    return run_command(
        "black --check --diff .",
        "Black code formatting check"
    )


def check_flake8():
    """Check code style with Flake8."""
    return run_command(
        "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
        "Flake8 error checking"
    )


def check_isort():
    """Check import sorting with isort."""
    return run_command(
        "isort --check-only --diff .",
        "Isort import sorting check"
    )


def format_code():
    """Format code with Black and isort."""
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
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Lint and format Canvas Quiz Manager code"
    )
    parser.add_argument(
        "--format",
        action="store_true",
        help="Format code in addition to linting"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check code, don't format"
    )
    
    args = parser.parse_args()
    
    print("🔍 Canvas Quiz Manager - Code Quality Check")
    print("=" * 50)
    
    # Check if we're in the right directory
    project_root = Path(__file__).parent
    if not (project_root / "main.py").exists():
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
            "💡 Run 'poetry run lint --format' to automatically fix formatting issues."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
