#!/usr/bin/env python3
"""
Documentation Server Script

This module provides a local HTTP server for serving Sphinx documentation,
making it easy to view and navigate documentation in a web browser without
manually opening HTML files.

The script includes automatic documentation building, browser integration,
and real-time request logging for a seamless documentation viewing experience.

Key Features:
- Automatic documentation building if needed
- Local HTTP server with custom request logging
- Browser auto-opening for immediate access
- Configurable port and host settings
- Graceful error handling and shutdown

Author: Robert Fentress <learn@vt.edu>
Version: 0.2.0
"""

import os
import subprocess
import sys
import time
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread


class DocumentationHandler(SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler for serving documentation.

    This class extends SimpleHTTPRequestHandler to provide custom logging
    and serve documentation files from the correct directory. It includes
    enhanced request logging with emoji indicators for better visibility.

    Attributes:
        directory (str): The directory containing the documentation files

    Methods:
        log_message: Override to provide custom logging format with emojis

    Example:
        >>> handler = DocumentationHandler(request, client_address, server)
        >>> # Handler will automatically log requests with emoji indicators
        📄 127.0.0.1 - - [01/Jan/2024 12:00:00] "GET /index.html HTTP/1.1" 200 -

    See Also:
        :func:`start_server`: Main function that uses this handler
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the documentation handler.

        Args:
            *args: Positional arguments passed to SimpleHTTPRequestHandler
            **kwargs: Keyword arguments, with 'directory' extracted for serving
        """
        super().__init__(*args, directory=str(kwargs.pop("directory")), **kwargs)

    def log_message(self, format: str, *args) -> None:
        """
        Custom logging to show requests with emoji indicators.

        Args:
            format: The log message format string
            *args: Arguments to format the message
        """
        print(f"📄 {self.address_string()} - {format % args}")


def build_documentation() -> bool:
    """
    Build the Sphinx documentation if it doesn't exist.

    This function checks if the documentation has already been built and
    builds it if necessary. It tries multiple build methods in order of
    preference: sphinx-build directly, then make.

    Returns:
        bool: True if documentation was built successfully or already exists,
              False if building failed

    Note:
        The function handles both sphinx-build and make commands, providing
        fallback options for different environments.
    """
    print("🔨 Checking if documentation needs to be built...")

    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    build_dir = docs_dir / "_build" / "html"

    # Check if documentation already exists
    if build_dir.exists() and (build_dir / "index.html").exists():
        print("✅ Documentation already exists")
        return True

    print("📚 Building documentation...")

    # Change to docs directory
    original_dir = os.getcwd()
    os.chdir(docs_dir)

    try:
        # Try using sphinx-build directly first
        subprocess.run(
            ["sphinx-build", "-b", "html", ".", "_build/html"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("✅ Documentation built successfully!")
        return True

    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Fallback to make
            subprocess.run(["make", "html"], capture_output=True, text=True, check=True)
            print("✅ Documentation built successfully!")
            return True

        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Failed to build documentation")
            print("   Please run 'poetry run docs-simple' first")
            return False

    finally:
        os.chdir(original_dir)


def start_server(port: int = 8000, host: str = "localhost") -> bool:
    """
    Start the HTTP server to serve documentation.

    This function creates and starts a local HTTP server to serve the
    Sphinx documentation. It includes browser auto-opening and graceful
    shutdown handling.

    Args:
        port: The port number to bind the server to (default: 8000)
        host: The host address to bind to (default: 'localhost')

    Returns:
        bool: True if server started successfully, False otherwise

    Raises:
        OSError: If the port is already in use or other server errors

    Note:
        The server runs in a separate thread and can be stopped with Ctrl+C.
        The function automatically opens the default browser to the documentation.
    """
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs" / "_build" / "html"

    if not docs_dir.exists():
        print(f"❌ Documentation directory not found: {docs_dir}")
        print("   Please build the documentation first:")
        print("   poetry run docs-simple")
        return False

    # Change to the documentation directory
    os.chdir(docs_dir)

    try:
        # Create server
        def handler_factory(*args, **kwargs):
            return DocumentationHandler(*args, directory=str(docs_dir), **kwargs)

        server = HTTPServer((host, port), handler_factory)

        print("🌐 Starting documentation server...")
        print(f"   URL: http://{host}:{port}")
        print(f"   Directory: {docs_dir}")
        print("   Press Ctrl+C to stop the server")
        print()

        # Start server in a separate thread
        server_thread = Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        # Wait a moment for server to start
        time.sleep(1)

        # Open browser
        url = f"http://{host}:{port}"
        print(f"🚀 Opening browser to {url}")
        webbrowser.open(url)

        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            server.shutdown()
            print("✅ Server stopped")

        return True

    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {port} is already in use")
            print("   Try a different port: poetry run serve-docs --port 8001")
        else:
            print(f"❌ Failed to start server: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main() -> None:
    """
    Main function for the documentation server.

    This function parses command line arguments and starts the documentation
    server with the specified configuration. It handles argument parsing,
    documentation building, and server startup.

    Command Line Arguments:
        --port, -p: Port number to serve on (default: 8000)
        --host, -H: Host address to bind to (default: localhost)
        --no-build: Skip building documentation
        --no-browser: Don't auto-open browser

    Note:
        The function exits with status code 1 if any errors occur during
        server startup or documentation building.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Serve Canvas Quiz Manager documentation locally"
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Port to serve documentation on (default: 8000)",
    )
    parser.add_argument(
        "--host", "-H", default="localhost", help="Host to bind to (default: localhost)"
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Skip building documentation (assume it's already built)",
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="Don't automatically open browser"
    )

    args = parser.parse_args()

    print("📚 Canvas Quiz Manager Documentation Server")
    print("=" * 50)

    # Build documentation if needed
    if not args.no_build:
        if not build_documentation():
            sys.exit(1)

    # Start server
    success = start_server(args.port, args.host)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
