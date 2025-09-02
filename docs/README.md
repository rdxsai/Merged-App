# Question App Documentation

## Overview

The Question App is a comprehensive web application for managing Canvas LMS quiz questions with AI-powered feedback generation and an intelligent chat assistant using RAG (Retrieval-Augmented Generation).

## Table of Contents

- [Installation](installation.md)
- [API Reference](api.md)
- [Configuration](configuration.md)
- [Development](development.md)
- [Testing](testing.md)
- [Troubleshooting](troubleshooting.md)

## Quick Start

1. Install dependencies: `poetry install`
2. Configure environment variables
3. Run the application: `poetry run dev`
4. Access the application at `http://localhost:8080`

## Key Features

- Canvas LMS integration for quiz management
- AI-powered feedback generation using Azure OpenAI
- Intelligent chat assistant with RAG capabilities
- Vector store operations and semantic search
- Learning objectives management
- System prompt customization
- Comprehensive type safety and error handling

## Architecture

The application follows a modular architecture with clear separation of concerns:

- **Core**: Configuration, logging, and application setup
- **API**: Modular endpoints organized by functionality
- **Services**: Business logic and external integrations
- **Models**: Pydantic data models for type safety
- **Utils**: Utility functions and helpers

## Version

Current version: 0.3.0

## Support

For issues and questions, please refer to the troubleshooting guide or create an issue in the project repository.
