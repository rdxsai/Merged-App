# Canvas Quiz Manager

**Creator: Bryce Kayanuma (BrycePK@vt.edu)**

A comprehensive web application for managing Canvas LMS quiz questions with AI-powered feedback generation and an intelligent chat assistant using RAG (Retrieval-Augmented Generation).

## 🌟 Features

### Core Functionality

- **Canvas Integration**: Fetch quiz questions directly from Canvas LMS API
- **AI Feedback Generation**: Generate educational feedback using Azure OpenAI
- **Question Editor**: Edit questions, answers, and feedback with WYSIWYG markdown editors
- **Answer Management**: Toggle correct/incorrect answers with visual True/False buttons
- **Real-time Preview**: Live preview updates when answer correctness changes

### Advanced Features

- **Vector Store**: Create local ChromaDB vector store with Ollama embeddings
- **RAG Chat Assistant**: Intelligent chat interface with context-aware responses
- **Comprehensive Search**: Semantic search through quiz content using embeddings
- **Token Usage Tracking**: Monitor AI API costs with detailed token usage logging

### User Interface

- **Responsive Design**: Works on desktop and mobile devices
- **Sticky Headers**: Always accessible navigation and controls
- **Real-time Updates**: Auto-save functionality and live preview updates
- **Professional Styling**: Clean, modern interface with Bootstrap 5

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Canvas LMS    │    │  Azure OpenAI   │    │     Ollama      │
│     API         │    │   (Chat/GPT)    │    │  (Embeddings)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ Fetch Questions       │ Generate Feedback     │ Create Embeddings
         │                       │ & Chat Responses      │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Canvas    │  │    Chat     │  │      Vector Store       │ │
│  │ Integration │  │   System    │  │    (ChromaDB)           │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Web Interface                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Question   │  │    Chat     │  │     System Prompt       │ │
│  │   Editor    │  │ Assistant   │  │       Editor            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

### Required Services

- **Python 3.11+**
- **Canvas LMS** account with API access
- **Azure OpenAI** subscription
- **Ollama** (for local embeddings)

### API Keys & Configuration

- Canvas API token
- Azure OpenAI subscription key and endpoint
- Course ID and Quiz ID from Canvas

## 🚀 Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd question_app
```

### 2. Install Poetry (Package Manager)

Poetry is the recommended package manager for this project.

#### macOS (using Homebrew):

```bash
brew install poetry
```

#### Other platforms:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. Install Dependencies with Poetry

```bash
# Install all dependencies and create virtual environment
poetry install

# Activate the virtual environment
poetry shell
```

### 3a. Alternative: Using pip (Legacy)

```bash
# If you prefer pip, first create a virtual environment:
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Install and Setup Ollama

#### On macOS/Linux:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

#### On Windows:

1. Download Ollama from [https://ollama.ai/download](https://ollama.ai/download)
2. Run the installer
3. Open Command Prompt/PowerShell and start Ollama:

```cmd
ollama serve
```

#### Pull Required Model:

```bash
# Pull the embedding model (required for vector store)
ollama pull nomic-embed-text

# Verify installation
ollama list
```

**Note**: Keep Ollama running in a separate terminal window throughout usage.

### 5. Environment Configuration

Create a `.env` file in the project root:

```env
# Canvas Configuration
CANVAS_BASE_URL=https://your-canvas-instance.instructure.com
CANVAS_API_TOKEN=your_canvas_api_token
COURSE_ID=your_course_id
QUIZ_ID=your_quiz_id

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_ID=your-deployment-name
AZURE_OPENAI_SUBSCRIPTION_KEY=your_subscription_key
AZURE_OPENAI_API_VERSION=2023-12-01-preview

# Ollama Configuration (Optional - defaults shown)
OLLAMA_HOST=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### 6. Start Application

#### Using Poetry (Recommended):

```bash
# Development mode with auto-reload
poetry run dev

# OR production mode
poetry run start
```

#### Using uvicorn directly:

```bash
# If using Poetry virtual environment
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# OR if using traditional virtual environment
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Access the application at: `http://localhost:8000`

## 🔨 Poetry Commands (Recommended)

This project includes convenient Poetry scripts for common tasks:

### Development

```bash
# Start in development mode (auto-reload)
poetry run dev

# Start in production mode
poetry run start
```

### Code Quality

```bash
# Format code with Black
poetry run format

# Lint code with flake8
poetry run lint

# Type checking with mypy
poetry run type-check

# Check for missing type annotations
poetry run type-check --check-annotations

# Run tests
poetry run test

# Run tests with coverage
poetry run test --coverage

# Run specific test types
poetry run test --type unit
poetry run test --type integration
poetry run test --type ai
poetry run test --type api
```

### Documentation

```bash
# Build documentation (requires make)
poetry run docs

# Build documentation (no make required)
poetry run docs-simple

# Build and serve documentation in one command
poetry run docs-serve

# Or serve existing documentation
poetry run serve-docs
```

### Dependency Management

```bash
# Show installed packages
poetry show

# Show dependency tree
poetry show --tree

# Add a new package
poetry add package-name

# Add a development package
poetry add --group dev package-name

# Update dependencies
poetry update

# Remove a package
poetry remove package-name
```

### Virtual Environment

```bash
# Show environment info
poetry env info

# Activate shell
poetry shell

# Run a command in the environment
poetry run python script.py
```

## 📖 Usage Guide

For detailed usage instructions, see the [Documentation](docs/).

### Documentation Sections

- **[API Reference](docs/api.rst)** - Complete API documentation
- **[API Examples](docs/api_examples.rst)** - Real-world usage examples and workflows
- **[Installation Guide](docs/installation.rst)** - Step-by-step setup instructions
- **[Usage Guide](docs/usage.rst)** - How to use application features
- **[Configuration Guide](docs/configuration.rst)** - Environment and system setup
- **[Troubleshooting Guide](docs/troubleshooting.rst)** - Common issues and solutions
- **[Development Guide](docs/development.rst)** - Contributing and development setup

### Initial Setup

1. **Configure System Prompt**

   - Click "Feedback System Prompt" to set up AI feedback generation
   - Customize the prompt for your specific educational context

2. **Fetch Questions from Canvas**

   - Click "Fetch Questions" to import quiz questions from Canvas LMS
   - Questions are automatically cleaned of HTML tags and stored locally

3. **Create Vector Store**
   - Click "Create Vector Store" to build the searchable knowledge base
   - This enables the RAG chat assistant functionality

### Question Management

#### Editing Questions

- Click on any question card to open the editor
- Edit question text using the WYSIWYG markdown editor
- Modify answer options and feedback

#### Managing Answer Correctness

- Use True/False buttons to set correct answers
- **Multiple Choice/True-False**: Only one answer can be correct
- **Multiple Answer**: Multiple answers can be correct
- Preview updates automatically

#### AI Feedback Generation

- Click "Generate AI Feedback" to create educational explanations
- Reviews answer correctness and provides context-aware feedback
- Token usage is logged to browser console

### Chat Assistant

#### Accessing the Chat

- Click "Chat Assistant" from the main page
- View the Azure OpenAI model being used in the header

#### Using RAG Features

- Ask questions about quiz content, accessibility, or best practices
- **Left Panel**: Chat conversation
- **Right Panel**: Retrieved context chunks used for responses
- Context is automatically found using semantic search

#### Example Queries

```
"What are the best practices for alt text?"
"How should forms be made accessible?"
"Tell me about color contrast requirements"
"What makes a good accessibility quiz question?"
```

## 🛠️ Configuration

### Canvas Setup

1. Generate API token in Canvas: Account → Settings → Approved Integrations → New Access Token
2. Find Course ID: URL when viewing course (e.g., `/courses/123456`)
3. Find Quiz ID: URL when viewing quiz (e.g., `/quizzes/789012`)

### Azure OpenAI Setup

1. Add endpoint details to .env file

### Ollama Models

- **nomic-embed-text**: High-quality embedding model for RAG (Suggested model)
- **Alternative models**: `all-MiniLM-L6-v2`, `sentence-transformers/all-mpnet-base-v2`

## 🔧 API Endpoints

For complete API documentation, see the [API Reference](docs/api.rst).

For practical examples and workflows, see [API Examples](docs/api_examples.rst).

| Endpoint                            | Method   | Description                   |
| ----------------------------------- | -------- | ----------------------------- |
| `/`                                 | GET      | Main question list page       |
| `/chat`                             | GET      | Chat assistant interface      |
| `/questions/{id}`                   | GET      | Question editor page          |
| `/questions/{id}`                   | PUT      | Update question data          |
| `/questions/{id}/generate-feedback` | POST     | Generate AI feedback          |
| `/chat/message`                     | POST     | Process chat message with RAG |
| `/create-vector-store`              | POST     | Build ChromaDB vector store   |
| `/fetch-questions`                  | POST     | Import questions from Canvas  |
| `/system-prompt`                    | GET/POST | System prompt management      |
| `/debug/config`                     | GET      | Configuration status          |
| `/debug/ollama-test`                | GET      | Test Ollama connectivity      |

## 📁 Project Structure

```
question_app/
├── main.py                 # FastAPI application
├── templates/
│   ├── index.html          # Question list page
│   ├── edit_question.html  # Question editor
│   ├── chat.html          # Chat assistant
│   └── system_prompt_edit.html
├── docs/                   # Documentation
│   ├── api.rst            # API reference
│   ├── api_examples.rst   # API usage examples
│   ├── troubleshooting.rst # Troubleshooting guide
│   └── ...                # Other documentation files
├── tests/                  # Test suite
├── quiz_questions.json     # Question data storage
├── system_prompt.txt      # AI feedback prompt
├── vector_store/          # ChromaDB database
├── .env                   # Environment configuration
└── README.md              # This file
```

## 🔍 Troubleshooting

For comprehensive troubleshooting guidance, see the [Troubleshooting Guide](docs/troubleshooting.rst).

### Common Issues

#### Ollama Connection Errors

```bash
# Check if Ollama is running
ollama list

# Restart Ollama service
ollama serve

# Test connectivity
curl http://localhost:11434/api/tags
```

#### Vector Store Creation Fails

1. Ensure Ollama is running and nomic-embed-text is installed
2. Check vector store permissions in project directory
3. Verify questions are loaded (`quiz_questions.json` exists)

#### Azure OpenAI Errors

1. Verify endpoint URL format: `https://your-resource.openai.azure.com`
2. Check subscription key and deployment ID
3. Ensure model is deployed and available
4. Run `python test_azure_openai.py` for comprehensive testing

#### Canvas API Issues

1. Verify API token has appropriate permissions
2. Check Course ID and Quiz ID are correct
3. Ensure Canvas instance URL is correct

### Debug Endpoints

- `/debug/config` - Check all configuration status
- `/debug/ollama-test` - Test Ollama connectivity and models

### Testing Tools

- `test_azure_openai.py` - Comprehensive Azure OpenAI connectivity and functionality testing
- `poetry run pytest` - Run the full test suite

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support or questions:

1. Check the [Troubleshooting Guide](docs/troubleshooting.rst) for common issues
2. Review the [API Examples](docs/api_examples.rst) for usage patterns
3. Check debug endpoints for configuration issues
4. Ensure all prerequisites are properly installed
5. Verify environment variables are correctly set

## 🎯 Future Enhancements

- [ ] Multiple quiz support
- [ ] Batch question processing
- [ ] Export functionality
- [ ] Advanced analytics
- [ ] Custom embedding models
- [ ] Multi-language support
- [ ] Question templates
- [ ] Automated testing framework

---

Built with ❤️ using FastAPI, Azure OpenAI, Ollama, and ChromaDB
