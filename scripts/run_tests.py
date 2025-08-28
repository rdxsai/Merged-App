#!/usr/bin/env python3
"""
Test Runner Script

This module provides a comprehensive test runner for the Canvas Quiz Manager
application, supporting different test types, coverage reporting, and various
testing options.

The script integrates with pytest to provide a unified testing interface with
enhanced output parsing, error reporting, and helpful guidance for fixing
test issues.

Key Features:
- Multiple test type support (unit, integration, AI, API)
- Coverage reporting integration
- Parallel test execution
- Watch mode for development
- Debug output options
- Smart result parsing

Author: Robert Fentress <learn@vt.edu>
Version: 0.2.0
"""

import argparse
import subprocess
import sys
from typing import List, Optional


def run_command(cmd: List[str], description: str) -> bool:
    """
    Run a command and handle errors with enhanced output parsing.

    This function executes a subprocess command and provides enhanced output
    parsing for test results, including automatic summary extraction and
    formatted error reporting.

    Args:
        cmd: List of command arguments to execute
        description: Human-readable description of the command being run

    Returns:
        bool: True if command succeeded (return code 0), False otherwise

    Note:
        The function automatically parses test output to extract summary
        information and provides formatted error messages for debugging.
    """
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        # Parse test results
        has_passed = "passed" in result.stdout
        has_failed = "failed" in result.stdout
        if has_passed and has_failed:
            # Extract summary information
            lines = result.stdout.split("\n")
            summary_line = None
            for line in lines:
                if "passed" in line and ("failed" in line or "error" in line):
                    summary_line = line
                    break

            if summary_line:
                print(f"📊 Test Summary: {summary_line.strip()}")

        if result.returncode == 0:
            print("✅ SUCCESS")
            if result.stdout:
                print("Output:")
                print(result.stdout)
            return True
        else:
            print("❌ FAILED")
            print(f"Return code: {result.returncode}")
            if result.stdout:
                print("Stdout:")
                print(result.stdout)
            if result.stderr:
                print("Stderr:")
                print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main() -> int:
    """
    Main test runner function.

    This function parses command line arguments and executes the appropriate
    test suite based on the specified options. It supports multiple test
    types, coverage reporting, and various execution modes.

    Command Line Arguments:
        --type: Test type to run (unit, integration, all, ai, api)
        --coverage: Enable coverage reporting
        --verbose: Enable verbose output
        --fast: Skip slow tests
        --parallel: Run tests in parallel
        --watch: Watch for file changes
        --debug: Enable debug output

    Returns:
        int: Exit code (0 for success, 1 for failure)

    Note:
        The function provides helpful tips for fixing test issues when
        tests fail.
    """
    parser = argparse.ArgumentParser(
        description="Run tests for Canvas Quiz Manager application"
    )
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "all", "ai", "api"],
        default="all",
        help="Type of tests to run",
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage report"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel (requires pytest-xdist)",
    )
    parser.add_argument(
        "--watch", action="store_true", help="Watch for file changes and re-run tests"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Run tests with debug output"
    )

    args = parser.parse_args()

    print("🧪 Canvas Quiz Manager - Test Runner")
    print("=" * 50)

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add coverage if requested
    if args.coverage:
        cmd.extend(["--cov=main", "--cov-report=html", "--cov-report=term"])

    # Add verbose flag
    if args.verbose:
        cmd.append("-v")

    # Add debug flag
    if args.debug:
        cmd.extend(["-s", "--tb=long"])

    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", "auto"])

    # Add watch mode
    if args.watch:
        cmd.append("--f")

    # Add test type filters
    if args.type == "unit":
        cmd.extend(["-m", "unit"])
    elif args.type == "integration":
        cmd.extend(["-m", "integration"])
    elif args.type == "ai":
        cmd.extend(["-m", "ai"])
    elif args.type == "api":
        cmd.extend(["-m", "api"])

    # Skip slow tests if requested
    if args.fast:
        cmd.extend(["-m", "not slow"])

    # Run the tests
    success = run_command(cmd, f"Running {args.type} tests")

    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        print("\n💡 Tips for fixing test issues:")
        print("   - Check that all dependencies are installed")
        print("   - Verify environment variables are set correctly")
        print("   - Run 'poetry run test --debug' for detailed output")
        print("   - Run 'poetry run test --type unit' to test specific areas")
        return 1


if __name__ == "__main__":
    sys.exit(main())
