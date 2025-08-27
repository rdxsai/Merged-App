Canvas Quiz Manager Documentation
================================

A comprehensive web application for managing Canvas LMS quiz questions with AI-powered feedback generation and an intelligent chat assistant using RAG (Retrieval-Augmented Generation).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules
   api
   installation
   usage
   configuration
   development
   development_tools
   testing

Overview
--------

The Canvas Quiz Manager is a FastAPI-based web application that provides:

* **Canvas LMS Integration**: Fetch and manage quiz questions from Canvas LMS
* **AI-Powered Feedback**: Generate educational feedback using Azure OpenAI
* **Intelligent Chat Assistant**: RAG-powered chat with semantic search capabilities
* **Vector Store**: ChromaDB-based semantic search and storage
* **Learning Objectives Management**: Organize questions by learning objectives
* **System Prompt Customization**: Flexible AI prompt configuration

Key Features
-----------

* **Question Management**: Create, edit, and delete quiz questions
* **AI Feedback Generation**: Automatically generate educational feedback for questions
* **Semantic Search**: Find relevant questions using vector embeddings
* **Chat Assistant**: Interactive chat with access to question knowledge base
* **Learning Objectives**: Organize content by educational objectives
* **Topic Classification**: Automatic topic extraction and tagging
* **Canvas Integration**: Direct integration with Canvas LMS API

Architecture
-----------

The application is built with:

* **FastAPI**: Modern, fast web framework for building APIs
* **Azure OpenAI**: AI service for generating educational feedback
* **Ollama**: Local embedding generation using nomic-embed-text model
* **ChromaDB**: Vector database for semantic search
* **Canvas LMS API**: Integration with Canvas learning management system
* **Pydantic**: Data validation and serialization
* **Jinja2**: Template engine for web interface

Installation
-----------

See :doc:`installation` for detailed installation instructions.

Quick Start
----------

1. Install dependencies: ``poetry install``
2. Configure environment variables (see :doc:`configuration`)
3. Start the development server: ``poetry run dev``
4. Access the application at ``http://localhost:8080``

API Documentation
----------------

See :doc:`api` for complete API documentation.

Development
-----------

See :doc:`development` for development setup and guidelines.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
