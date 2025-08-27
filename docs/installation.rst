Installation
============

Prerequisites
------------

* Python 3.11 or higher
* Poetry (for dependency management)
* Canvas LMS account with API access
* Azure OpenAI account (for AI feedback generation)
* Ollama (for local embedding generation)

Installation Steps
-----------------

1. **Clone the repository**

   .. code-block:: bash

      git clone <repository-url>
      cd questionapp

2. **Install dependencies using Poetry**

   .. code-block:: bash

      poetry install

3. **Set up environment variables**

   Create a `.env` file in the project root with the following variables:

   .. code-block:: text

      # Canvas LMS Configuration
      CANVAS_BASE_URL=https://your-institution.instructure.com
      CANVAS_API_TOKEN=your_canvas_api_token
      COURSE_ID=your_course_id
      QUIZ_ID=your_quiz_id

      # Azure OpenAI Configuration
      AZURE_OPENAI_ENDPOINT=https://your-endpoint.azure-api.net
      AZURE_OPENAI_DEPLOYMENT_ID=your_deployment_id
      AZURE_OPENAI_API_VERSION=2023-12-01-preview
      AZURE_OPENAI_SUBSCRIPTION_KEY=your_subscription_key

      # Ollama Configuration
      OLLAMA_HOST=http://localhost:11434
      OLLAMA_EMBEDDING_MODEL=nomic-embed-text

4. **Install and start Ollama**

   .. code-block:: bash

      # Install Ollama (see https://ollama.ai for platform-specific instructions)
      curl -fsSL https://ollama.ai/install.sh | sh

      # Start Ollama service
      ollama serve

      # Pull the embedding model
      ollama pull nomic-embed-text

5. **Start the application**

   .. code-block:: bash

      # Development mode with auto-reload
      poetry run dev

      # Production mode
      poetry run start

6. **Access the application**

   Open your browser and navigate to `http://localhost:8080`

7. **Build Documentation (Optional)**

   .. code-block:: bash

      # Build documentation (requires make)
      poetry run docs

      # Build documentation (no make required)
      poetry run docs-simple

      # View documentation
      open docs/_build/html/index.html

      # Or serve documentation locally
      poetry run serve-docs

Configuration Details
--------------------

Canvas LMS Configuration
~~~~~~~~~~~~~~~~~~~~~~~

* **CANVAS_BASE_URL**: Your Canvas instance URL
* **CANVAS_API_TOKEN**: API token from Canvas (generate in Account Settings)
* **COURSE_ID**: ID of the course containing the quiz
* **QUIZ_ID**: ID of the specific quiz to manage

Azure OpenAI Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

* **AZURE_OPENAI_ENDPOINT**: Your Azure OpenAI endpoint URL
* **AZURE_OPENAI_DEPLOYMENT_ID**: Deployment ID for your model
* **AZURE_OPENAI_API_VERSION**: API version (default: 2023-12-01-preview)
* **AZURE_OPENAI_SUBSCRIPTION_KEY**: Your Azure subscription key

Ollama Configuration
~~~~~~~~~~~~~~~~~~~

* **OLLAMA_HOST**: Ollama service URL (default: http://localhost:11434)
* **OLLAMA_EMBEDDING_MODEL**: Embedding model name (default: nomic-embed-text)

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

1. **Poetry not found**: Install Poetry first: `curl -sSL https://install.python-poetry.org | python3 -`

2. **Ollama connection failed**: Ensure Ollama is running and the model is installed

3. **Canvas API errors**: Verify your API token and course/quiz IDs

4. **Azure OpenAI errors**: Check your endpoint URL and subscription key

Getting Help
-----------

* Check the logs in `canvas_app.log`
* Review the configuration documentation
* Ensure all services are running and accessible
