# Configuration Guide

## Overview

The Question App requires configuration for multiple external services and integrations. This guide covers all configuration options, environment variables, and setup procedures.

## Environment Variables

### Canvas LMS Configuration

Canvas LMS integration requires the following environment variables:

```bash
# Canvas API Configuration
CANVAS_BASE_URL=https://your-institution.instructure.com
CANVAS_API_TOKEN=your_canvas_api_token
COURSE_ID=your_course_id
QUIZ_ID=your_quiz_id
```

#### Configuration Details

- **CANVAS_BASE_URL**: Your Canvas LMS instance URL

  - Format: `https://your-institution.instructure.com`
  - Example: `https://vt.instructure.com`

- **CANVAS_API_TOKEN**: Personal access token for Canvas API

  - Generate in Canvas: Settings > Approved Integrations
  - Permissions: Read access to courses and quizzes

- **COURSE_ID**: Target course identifier

  - Found in Canvas URL: `/courses/{course_id}`
  - Numeric identifier for the course

- **QUIZ_ID**: Target quiz identifier
  - Found in Canvas URL: `/courses/{course_id}/quizzes/{quiz_id}`
  - Numeric identifier for the specific quiz

### Azure OpenAI Configuration

AI-powered features require Azure OpenAI service configuration:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_SUBSCRIPTION_KEY=your_subscription_key
AZURE_OPENAI_DEPLOYMENT_ID=your_deployment_id
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

#### Configuration Details

- **AZURE_OPENAI_ENDPOINT**: Azure OpenAI service endpoint

  - Format: `https://your-resource.openai.azure.com`
  - Found in Azure portal under your OpenAI resource

- **AZURE_OPENAI_SUBSCRIPTION_KEY**: API key for authentication

  - Generate in Azure portal: Keys and Endpoint
  - Keep secure and never commit to version control

- **AZURE_OPENAI_DEPLOYMENT_ID**: Model deployment identifier

  - Created when deploying a model in Azure OpenAI
  - Example: `gpt-4`, `gpt-35-turbo`

- **AZURE_OPENAI_API_VERSION**: API version to use
  - Current recommended: `2024-02-15-preview`
  - Check Azure documentation for latest versions

### Ollama Configuration (Optional)

Local embedding generation using Ollama:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

#### Configuration Details

- **OLLAMA_HOST**: Ollama service URL

  - Default: `http://localhost:11434`
  - Change if running Ollama on different host/port

- **OLLAMA_EMBEDDING_MODEL**: Embedding model to use
  - Recommended: `nomic-embed-text`
  - Alternative: `all-minilm` or other embedding models

## Configuration Files

### System Prompt Configuration

System prompts are stored in configuration files:

#### Main System Prompt

**File**: `config/system_prompt.txt`

**Purpose**: Guides AI feedback generation for quiz questions

**Example Content**:

```
You are an educational assistant helping with quiz feedback generation.
Your role is to provide constructive, educational feedback for quiz questions.

Guidelines:
- Provide clear, helpful feedback for correct and incorrect answers
- Explain why answers are correct or incorrect
- Include educational context and learning opportunities
- Keep feedback concise but informative
- Use appropriate educational language
```

#### Chat System Prompt

**File**: `config/chat_system_prompt.txt`

**Purpose**: Guides the RAG-based chat assistant

**Example Content**:

```
You are a helpful educational assistant for the Question App.
You have access to context from quiz questions and learning materials.

Guidelines:
- Use the provided context to answer questions accurately
- Provide educational insights and explanations
- Be helpful and supportive in your responses
- Cite relevant information from the context when appropriate
- Maintain a professional and educational tone

Context: {context}
```

#### Welcome Message

**File**: `config/chat_welcome_message.txt`

**Purpose**: Welcome message for chat interface

**Example Content**:

```
Welcome to the Question App chat assistant!

I can help you with:
- Understanding quiz questions and concepts
- Learning about accessibility and web development
- Finding relevant information from your course materials
- Answering questions about educational content

How can I help you today?
```

### Learning Objectives

**File**: `data/learning_objectives.json`

**Purpose**: Store course learning objectives

**Example Structure**:

```json
[
  {
    "text": "Understand web accessibility principles",
    "blooms_level": "understand",
    "priority": "high"
  },
  {
    "text": "Apply accessibility guidelines in practice",
    "blooms_level": "apply",
    "priority": "medium"
  }
]
```

### Quiz Questions Data

**File**: `data/quiz_questions.json`

**Purpose**: Store quiz questions and metadata

**Auto-generated**: Created when fetching questions from Canvas

## Configuration Validation

### Canvas Configuration Validation

The application validates Canvas configuration before making API calls:

```python
def validate_canvas_config() -> bool:
    """Validate Canvas configuration completeness."""
    required_configs = [
        "CANVAS_BASE_URL",
        "CANVAS_API_TOKEN",
        "COURSE_ID",
        "QUIZ_ID"
    ]

    for config_name in required_configs:
        if not getattr(config, config_name):
            return False
    return True
```

### Azure OpenAI Configuration Validation

Azure OpenAI configuration is validated for AI features:

```python
def validate_azure_openai_config() -> bool:
    """Validate Azure OpenAI configuration completeness."""
    required_configs = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_SUBSCRIPTION_KEY",
        "AZURE_OPENAI_DEPLOYMENT_ID",
        "AZURE_OPENAI_API_VERSION"
    ]

    for config_name in required_configs:
        if not getattr(config, config_name):
            return False
    return True
```

## Configuration Management

### Environment-Specific Configuration

For different environments, use separate configuration files:

#### Development Environment

```bash
# .env.development
CANVAS_BASE_URL=https://your-dev-instance.instructure.com
CANVAS_API_TOKEN=dev_token
COURSE_ID=123
QUIZ_ID=456
```

#### Production Environment

```bash
# .env.production
CANVAS_BASE_URL=https://your-prod-instance.instructure.com
CANVAS_API_TOKEN=prod_token
COURSE_ID=789
QUIZ_ID=101
```

### Configuration Loading

The application loads configuration in the following order:

1. Environment variables
2. `.env` file in project root
3. Default values (if any)

### Secure Configuration Practices

#### API Key Security

- Never commit API keys to version control
- Use environment variables for sensitive data
- Rotate API keys regularly
- Use least-privilege access for API tokens

#### Configuration Validation

- Validate all required configuration on startup
- Provide clear error messages for missing configuration
- Use configuration validation functions before API calls

## Service-Specific Setup

### Canvas LMS Setup

#### 1. API Token Generation

1. Log into your Canvas LMS account
2. Navigate to Settings > Approved Integrations
3. Click "New Access Token"
4. Set appropriate permissions:
   - `url:GET|/api/v1/courses`
   - `url:GET|/api/v1/courses/:course_id/quizzes`
   - `url:GET|/api/v1/courses/:course_id/quizzes/:quiz_id/questions`
5. Copy the generated token

#### 2. Course and Quiz Identification

1. Navigate to your target course in Canvas
2. Note the course ID from the URL: `/courses/{course_id}`
3. Navigate to the target quiz
4. Note the quiz ID from the URL: `/courses/{course_id}/quizzes/{quiz_id}`

#### 3. API Permissions

Ensure your Canvas API token has the following permissions:

- Read access to courses
- Read access to quizzes
- Read access to quiz questions
- Access to course content

### Azure OpenAI Setup

#### 1. Service Creation

1. Create an Azure OpenAI service in Azure portal
2. Deploy a GPT model (recommended: GPT-4)
3. Note the endpoint URL and deployment ID

#### 2. API Key Management

1. Navigate to Keys and Endpoint in Azure portal
2. Copy the primary or secondary key
3. Store securely in environment variables

#### 3. Model Deployment

1. Deploy a GPT model in your Azure OpenAI service
2. Note the deployment ID
3. Ensure the model supports chat completions

### Ollama Setup

#### 1. Installation

**macOS**:

```bash
brew install ollama
```

**Linux**:

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### 2. Model Download

```bash
# Download embedding model
ollama pull nomic-embed-text

# Verify installation
ollama list
```

#### 3. Service Management

```bash
# Start Ollama service
ollama serve

# Check service status
curl http://localhost:11434/api/tags
```

## Configuration Testing

### Debug Endpoints

Use the debug API endpoints to test configuration:

#### Test Configuration Status

```bash
curl http://localhost:8080/debug/config
```

#### Test Ollama Connection

```bash
curl http://localhost:8080/debug/ollama-test
```

#### Test Question Data

```bash
curl http://localhost:8080/debug/question/1
```

### Manual Testing

#### Test Canvas Integration

1. Configure Canvas environment variables
2. Test course retrieval: `GET /api/courses`
3. Test quiz retrieval: `GET /api/courses/{course_id}/quizzes`
4. Test question fetching: `POST /api/fetch-questions`

#### Test Azure OpenAI Integration

1. Configure Azure OpenAI environment variables
2. Create a test question
3. Generate AI feedback: `POST /questions/{id}/generate-feedback`
4. Verify feedback generation

#### Test Ollama Integration

1. Start Ollama service
2. Create vector store: `POST /vector-store/create`
3. Test search: `GET /vector-store/search?query=test`
4. Verify embedding generation

## Troubleshooting Configuration

### Common Issues

#### Canvas API Errors

- **401 Unauthorized**: Check API token validity
- **403 Forbidden**: Verify API token permissions
- **404 Not Found**: Check course and quiz IDs
- **429 Too Many Requests**: Implement rate limiting

#### Azure OpenAI Errors

- **401 Unauthorized**: Check subscription key
- **404 Not Found**: Verify endpoint URL and deployment ID
- **400 Bad Request**: Check API version compatibility

#### Ollama Errors

- **Connection Refused**: Ensure Ollama service is running
- **Model Not Found**: Download required embedding model
- **Timeout**: Check network connectivity and service status

### Configuration Validation

Use the debug endpoints to validate configuration:

```bash
# Check overall configuration
curl http://localhost:8080/debug/config

# Test specific services
curl http://localhost:8080/debug/ollama-test
```

### Environment Variable Issues

- Verify variable names match exactly
- Check for extra spaces or special characters
- Ensure variables are loaded in the correct environment
- Test with simple values first

## Best Practices

### Security

- Use environment variables for sensitive data
- Rotate API keys regularly
- Implement least-privilege access
- Monitor API usage and costs

### Performance

- Use appropriate API versions
- Implement caching where possible
- Monitor response times
- Optimize embedding model selection

### Maintenance

- Keep configuration documentation updated
- Test configuration changes in development first
- Monitor service availability
- Plan for configuration updates

### Backup and Recovery

- Backup configuration files
- Document configuration procedures
- Test configuration restoration
- Maintain configuration version control
