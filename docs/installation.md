# Installation Guide

## Prerequisites

### System Requirements

- Python 3.11 or higher
- Poetry for dependency management
- Git for version control
- Modern web browser

### Required Services

- Canvas LMS account with API access
- Azure OpenAI service account
- Ollama for local embedding generation (optional)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd questionapp
```

### 2. Install Dependencies

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

### 3. Environment Configuration

Create a `.env` file in the project root with the following variables:

```bash
# Canvas LMS Configuration
CANVAS_BASE_URL=https://canvas.vt.edu
CANVAS_API_TOKEN=your_canvas_api_token
COURSE_ID=your_course_id
QUIZ_ID=your_quiz_id

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_SUBSCRIPTION_KEY=your_subscription_key
AZURE_OPENAI_DEPLOYMENT_ID=your_deployment_id
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Ollama Configuration (Optional)
OLLAMA_HOST=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### 4. Verify Installation

```bash
# Activate the virtual environment
poetry shell

# Run tests to verify installation
poetry run test

# Start the development server
poetry run dev
```

### 5. Access the Application

Open your web browser and navigate to:

```
http://localhost:8080
```

## Configuration Details

### Canvas LMS Setup

1. **API Token Generation**:

   - Log into your Canvas LMS account
   - Go to Settings > Approved Integrations
   - Generate a new access token
   - Copy the token to your `.env` file

2. **Course and Quiz IDs**:
   - Navigate to your course in Canvas
   - The course ID is in the URL: `/courses/{course_id}`
   - Navigate to a quiz to get the quiz ID: `/courses/{course_id}/quizzes/{quiz_id}`

### Azure OpenAI Setup

1. **Service Creation**:

   - Create an Azure OpenAI service in the Azure portal
   - Deploy a GPT model (e.g., GPT-4)
   - Note the endpoint URL and deployment ID

2. **API Key Management**:
   - Generate an API key from the Azure OpenAI service
   - Store it securely in your `.env` file

### Ollama Setup (Optional)

1. **Install Ollama**:

   ```bash
   # macOS
   brew install ollama

   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Start Ollama Service** (new terminal):

   Open a new terminal window or tab and start the Ollama service. Leave this running while you use the app.

   ```bash
   ollama serve
   ```

3. **Download Embedding Model** (original terminal):

   With the service running, pull the embedding model in your original terminal.

   ```bash
   ollama pull nomic-embed-text
   ```

## Development Setup

### VS Code Configuration

The project includes comprehensive VS Code configuration:

1. **Extensions**: Install recommended extensions
2. **Tasks**: Use pre-configured development tasks
3. **Debugging**: Configure debugging for FastAPI and tests
4. **Type Checking**: Integrated Pyright and Mypy support

### Development Commands

```bash
# Start development server with auto-reload
poetry run dev

# Run tests
poetry run test

# Type checking
poetry run type-check

# Code formatting
poetry run format

# Linting
poetry run lint

# Build documentation
poetry run docs-serve
```

## Troubleshooting

### Common Issues

1. **Poetry Installation**:

   - Ensure Python 3.11+ is installed
   - Use the official Poetry installation script

2. **Dependency Conflicts**:

   - Clear Poetry cache: `poetry cache clear . --all`
   - Reinstall dependencies: `poetry install --sync`

3. **Environment Variables**:

   - Verify all required variables are set
   - Check for typos in variable names
   - Ensure no extra spaces in values

4. **Port Conflicts**:
   - Change the port in `src/question_app/main.py`
   - Or use a different port: `poetry run dev --port 8081`

### Getting Help

- Check the troubleshooting guide for detailed solutions
- Review the configuration documentation
- Verify all prerequisites are met
- Test individual components separately

## Next Steps

After successful installation:

1. **Configure Canvas Integration**: Set up course and quiz IDs
2. **Test AI Features**: Verify Azure OpenAI integration
3. **Explore Features**: Try the chat assistant and feedback generation
4. **Customize Prompts**: Adjust system prompts for your needs
5. **Add Questions**: Import or create quiz questions

## Production Deployment

For production deployment, consider:

- Using a production WSGI server (Gunicorn, uvicorn)
- Setting up proper logging and monitoring
- Configuring HTTPS and security headers
- Using environment-specific configuration files
- Setting up database persistence for questions
