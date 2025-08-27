Configuration
=============

This document describes all configuration options for the Canvas Quiz Manager application.

Environment Variables
--------------------

Canvas LMS Configuration
~~~~~~~~~~~~~~~~~~~~~~~

.. envvar:: CANVAS_BASE_URL

   The base URL of your Canvas LMS instance.

   **Example**: ``https://your-institution.instructure.com``

   **Required**: Yes

.. envvar:: CANVAS_API_TOKEN

   Your Canvas API token for authentication.

   **Example**: ``1234~abcdefghijklmnopqrstuvwxyz``

   **Required**: Yes

   **Note**: Generate this token in Canvas Account Settings > API Access Tokens

.. envvar:: COURSE_ID

   The ID of the Canvas course containing the quiz.

   **Example**: ``12345``

   **Required**: Yes

   **Note**: This can be found in the course URL or course settings

.. envvar:: QUIZ_ID

   The ID of the specific quiz to manage.

   **Example**: ``67890``

   **Required**: Yes

   **Note**: This can be found in the quiz URL or quiz settings

Azure OpenAI Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. envvar:: AZURE_OPENAI_ENDPOINT

   The Azure OpenAI service endpoint URL.

   **Example**: ``https://your-resource.openai.azure.com``

   **Required**: Yes

   **Default**: ``https://itls-openai-connect.azure-api.net``

.. envvar:: AZURE_OPENAI_DEPLOYMENT_ID

   The deployment ID of your Azure OpenAI model.

   **Example**: ``gpt-4-deployment``

   **Required**: Yes

.. envvar:: AZURE_OPENAI_API_VERSION

   The Azure OpenAI API version to use.

   **Example**: ``2023-12-01-preview``

   **Required**: No

   **Default**: ``2023-12-01-preview``

.. envvar:: AZURE_OPENAI_SUBSCRIPTION_KEY

   Your Azure subscription key for API access.

   **Example**: ``abcdef1234567890abcdef1234567890``

   **Required**: Yes

Ollama Configuration
~~~~~~~~~~~~~~~~~~~

.. envvar:: OLLAMA_HOST

   The host URL for the Ollama service.

   **Example**: ``http://localhost:11434``

   **Required**: No

   **Default**: ``http://localhost:11434``

.. envvar:: OLLAMA_EMBEDDING_MODEL

   The name of the embedding model to use with Ollama.

   **Example**: ``nomic-embed-text``

   **Required**: No

   **Default**: ``nomic-embed-text``

File Configuration
-----------------

Data Files
~~~~~~~~~~

The application uses several JSON and text files for data storage:

.. code-block:: text

   data/quiz_questions.json          # Main questions database
   data/learning_objectives.json     # Learning objectives storage
   config/system_prompt.txt           # AI system prompt
   config/chat_system_prompt.txt      # Chat assistant system prompt
   config/chat_welcome_message.txt    # Chat welcome message

Vector Store
~~~~~~~~~~~

The vector store is stored in the `vector_store/` directory:

.. code-block:: text

   vector_store/
   ├── chroma.sqlite3          # ChromaDB database
   └── [collection-id]/        # Collection data files

Logging Configuration
--------------------

Log File
~~~~~~~~

The application logs to `canvas_app.log` with the following format:

.. code-block:: text

   %(asctime)s - %(levelname)s - %(message)s

Log Levels
~~~~~~~~~~

- **INFO**: General application information
- **WARNING**: Non-critical issues (e.g., rate limiting)
- **ERROR**: Errors that need attention
- **DEBUG**: Detailed debugging information

Configuration Validation
-----------------------

The application validates configuration on startup:

1. **Required Variables**: Checks that all required environment variables are set
2. **Service Connectivity**: Tests connections to external services
3. **File Permissions**: Verifies write access to data directories

Debug Endpoints
--------------

Configuration Status
~~~~~~~~~~~~~~~~~~~

Visit `/debug/config` to check configuration status:

.. code-block:: json

   {
     "canvas_configured": true,
     "azure_configured": true,
     "has_system_prompt": true,
     "data_file_exists": true,
     "questions_count": 25,
     "azure_endpoint": "https://...",
     "azure_deployment_id": "gpt-4",
     "ollama_host": "http://localhost:11434"
   }

Ollama Connection Test
~~~~~~~~~~~~~~~~~~~~~

Visit `/debug/ollama-test` to test Ollama connectivity:

.. code-block:: json

   {
     "ollama_connected": true,
     "ollama_host": "http://localhost:11434",
     "available_models": ["nomic-embed-text", "llama2"],
     "embedding_model_available": true,
     "configured_model": "nomic-embed-text"
   }

Configuration Best Practices
---------------------------

Security
~~~~~~~~

1. **API Tokens**: Store API tokens securely, never commit them to version control
2. **Environment Files**: Use `.env` files for local development
3. **Production**: Use secure environment variable management in production

Performance
~~~~~~~~~~~

1. **Ollama**: Run Ollama on the same machine for better performance
2. **ChromaDB**: Ensure adequate disk space for vector store
3. **Azure OpenAI**: Monitor API usage and costs

Reliability
~~~~~~~~~~~

1. **Backup**: Regularly backup data files and vector store
2. **Monitoring**: Set up logging and monitoring for production use
3. **Error Handling**: Configure appropriate timeouts and retry logic

Development Configuration
-------------------------

Local Development
~~~~~~~~~~~~~~~~

For local development, create a `.env` file:

.. code-block:: text

   # Canvas Configuration
   CANVAS_BASE_URL=https://your-institution.instructure.com
   CANVAS_API_TOKEN=your_token_here
   COURSE_ID=12345
   QUIZ_ID=67890

   # Azure OpenAI Configuration
   AZURE_OPENAI_ENDPOINT=https://your-endpoint.azure-api.net
   AZURE_OPENAI_DEPLOYMENT_ID=your_deployment_id
   AZURE_OPENAI_SUBSCRIPTION_KEY=your_key_here

   # Ollama Configuration
   OLLAMA_HOST=http://localhost:11434
   OLLAMA_EMBEDDING_MODEL=nomic-embed-text

Testing Configuration
~~~~~~~~~~~~~~~~~~~~

For testing, you can use mock services or test accounts:

1. **Canvas**: Use a test course with sample questions
2. **Azure OpenAI**: Use a test deployment or mock responses
3. **Ollama**: Use a local instance with test models

Production Configuration
-----------------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~

In production, set environment variables securely:

.. code-block:: bash

   export CANVAS_BASE_URL="https://your-institution.instructure.com"
   export CANVAS_API_TOKEN="your_production_token"
   export COURSE_ID="12345"
   export QUIZ_ID="67890"
   export AZURE_OPENAI_ENDPOINT="https://your-production-endpoint.azure-api.net"
   export AZURE_OPENAI_DEPLOYMENT_ID="your_production_deployment"
   export AZURE_OPENAI_SUBSCRIPTION_KEY="your_production_key"

Service Configuration
~~~~~~~~~~~~~~~~~~~~

1. **Web Server**: Use a production WSGI server like Gunicorn
2. **Process Management**: Use systemd or similar for process management
3. **Logging**: Configure centralized logging
4. **Monitoring**: Set up health checks and monitoring

Security Considerations
~~~~~~~~~~~~~~~~~~~~~~

1. **HTTPS**: Always use HTTPS in production
2. **Firewall**: Restrict access to necessary ports only
3. **Updates**: Keep dependencies updated
4. **Backups**: Implement regular backup procedures

Troubleshooting Configuration
----------------------------

Common Issues
~~~~~~~~~~~~

1. **Missing Environment Variables**

   .. code-block:: text

      Error: Missing Canvas configuration
      Solution: Set all required environment variables

2. **Invalid API Tokens**

   .. code-block:: text

      Error: Canvas API error: 401 Unauthorized
      Solution: Verify API token is valid and has correct permissions

3. **Service Connection Issues**

   .. code-block:: text

      Error: Cannot connect to Ollama
      Solution: Ensure Ollama is running and accessible

4. **File Permission Issues**

   .. code-block:: text

      Error: Permission denied writing to data file
      Solution: Check file and directory permissions

Debugging Steps
~~~~~~~~~~~~~~

1. **Check Configuration Status**

   .. code-block:: bash

      curl http://localhost:8080/debug/config

2. **Test Ollama Connection**

   .. code-block:: bash

      curl http://localhost:8080/debug/ollama-test

3. **Review Logs**

   .. code-block:: bash

      tail -f canvas_app.log

4. **Verify Environment Variables**

   .. code-block:: bash

      env | grep -E "(CANVAS|AZURE|OLLAMA)"
