# Troubleshooting Guide

## Overview

This guide provides solutions for common issues encountered when using the Question App. Each section covers specific problems, their causes, and step-by-step solutions.

## Installation Issues

### Poetry Installation Problems

#### Issue: Poetry not found

**Symptoms:**

- `poetry: command not found`
- `poetry install` fails

**Causes:**

- Poetry not installed
- Poetry not in PATH
- Installation incomplete

**Solutions:**

1. **Install Poetry**:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Add to PATH** (if needed):

   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. **Verify installation**:
   ```bash
   poetry --version
   ```

#### Issue: Dependency conflicts

**Symptoms:**

- `poetry install` fails with dependency errors
- Package version conflicts

**Solutions:**

1. **Clear Poetry cache**:

   ```bash
   poetry cache clear . --all
   ```

2. **Reinstall dependencies**:

   ```bash
   poetry install --sync
   ```

3. **Update Poetry**:
   ```bash
   poetry self update
   ```

### Python Version Issues

#### Issue: Wrong Python version

**Symptoms:**

- `Python 3.11+ required` error
- Poetry uses wrong Python version

**Solutions:**

1. **Check Python version**:

   ```bash
   python3 --version
   ```

2. **Configure Poetry Python**:

   ```bash
   poetry env use python3.11
   ```

3. **Install correct Python version**:

   ```bash
   # macOS
   brew install python@3.11

   # Ubuntu
   sudo apt install python3.11
   ```

## Configuration Issues

### Environment Variables

#### Issue: Missing environment variables

**Symptoms:**

- `Configuration incomplete` errors
- API calls fail with configuration errors

**Solutions:**

1. **Check .env file**:

   ```bash
   cat .env
   ```

2. **Verify all required variables**:

   ```bash
   # Canvas Configuration
   CANVAS_BASE_URL=https://your-institution.instructure.com
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

3. **Test configuration**:
   ```bash
   curl http://localhost:8080/debug/config
   ```

#### Issue: Invalid environment variables

**Symptoms:**

- API calls fail with authentication errors
- Invalid URL errors

**Solutions:**

1. **Validate Canvas URL**:

   - Ensure URL format: `https://your-institution.instructure.com`
   - Check for typos and extra spaces

2. **Validate API tokens**:

   - Regenerate Canvas API token if expired
   - Verify Azure OpenAI subscription key

3. **Check course and quiz IDs**:
   - Navigate to Canvas course/quiz
   - Extract IDs from URL: `/courses/{course_id}/quizzes/{quiz_id}`

### Canvas LMS Issues

#### Issue: Canvas API authentication failed

**Symptoms:**

- `401 Unauthorized` errors
- `Canvas API error` messages

**Solutions:**

1. **Regenerate API token**:

   - Log into Canvas
   - Go to Settings > Approved Integrations
   - Generate new access token
   - Update `.env` file

2. **Check token permissions**:

   - Ensure token has read access to courses
   - Verify token has access to quizzes
   - Check token expiration

3. **Verify Canvas URL**:
   - Ensure correct Canvas instance URL
   - Check for HTTPS requirement

#### Issue: Course or quiz not found

**Symptoms:**

- `404 Not Found` errors
- Empty course/quiz lists

**Solutions:**

1. **Verify course access**:

   - Ensure user has access to the course
   - Check course enrollment status
   - Verify course is published

2. **Check quiz visibility**:

   - Ensure quiz is published
   - Check quiz availability dates
   - Verify quiz permissions

3. **Validate IDs**:
   - Double-check course and quiz IDs
   - Extract IDs from Canvas URLs

### Azure OpenAI Issues

#### Issue: Azure OpenAI authentication failed

**Symptoms:**

- `401 Unauthorized` errors
- `Azure OpenAI configuration incomplete` messages

**Solutions:**

1. **Verify subscription key**:

   - Check Azure portal for correct key
   - Ensure key is not expired
   - Copy key without extra spaces

2. **Check endpoint URL**:

   - Verify endpoint format: `https://your-resource.openai.azure.com`
   - Ensure correct resource name
   - Check for typos

3. **Validate deployment**:
   - Ensure model is deployed
   - Check deployment ID
   - Verify API version compatibility

#### Issue: Model deployment not found

**Symptoms:**

- `404 Not Found` errors
- `Deployment not found` messages

**Solutions:**

1. **Check deployment status**:

   - Log into Azure portal
   - Navigate to OpenAI resource
   - Verify model deployment exists

2. **Deploy model if needed**:

   - Create new deployment
   - Note deployment ID
   - Update configuration

3. **Verify API version**:
   - Use supported API version
   - Check Azure documentation

### Ollama Issues

#### Issue: Ollama service not running

**Symptoms:**

- `Connection refused` errors
- Vector store creation fails

**Solutions:**

1. **Start Ollama service**:

   ```bash
   ollama serve
   ```

2. **Check service status**:

   ```bash
   curl http://localhost:11434/api/tags
   ```

3. **Verify installation**:
   ```bash
   ollama --version
   ```

#### Issue: Embedding model not found

**Symptoms:**

- `Model not found` errors
- Vector store creation fails

**Solutions:**

1. **Download model**:

   ```bash
   ollama pull nomic-embed-text
   ```

2. **List available models**:

   ```bash
   ollama list
   ```

3. **Check model name**:
   - Verify model name in configuration
   - Use exact model name

## Application Issues

### Server Startup Problems

#### Issue: Port already in use

**Symptoms:**

- `Address already in use` error
- Server fails to start

**Solutions:**

1. **Check port usage**:

   ```bash
   lsof -i :8080
   ```

2. **Kill existing process**:

   ```bash
   kill -9 <PID>
   ```

3. **Use different port**:
   ```bash
   poetry run dev --port 8081
   ```

#### Issue: Module import errors

**Symptoms:**

- `ModuleNotFoundError` messages
- Import path issues

**Solutions:**

1. **Check Python path**:

   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Reinstall package**:

   ```bash
   poetry install
   ```

3. **Verify virtual environment**:
   ```bash
   poetry shell
   which python
   ```

### API Endpoint Issues

#### Issue: API endpoints not responding

**Symptoms:**

- `404 Not Found` for API endpoints
- Endpoints return errors

**Solutions:**

1. **Check server status**:

   ```bash
   curl http://localhost:8080/
   ```

2. **Verify router registration**:

   - Check `src/question_app/core/app.py`
   - Ensure all routers are included

3. **Check endpoint paths**:
   - Verify URL paths in requests
   - Check router prefixes

#### Issue: CORS errors

**Symptoms:**

- Browser CORS errors
- API calls blocked

**Solutions:**

1. **Add CORS middleware** (if needed):

   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Check request headers**:
   - Ensure proper Content-Type
   - Verify Authorization headers

### Data Management Issues

#### Issue: Questions not loading

**Symptoms:**

- Empty question list
- File not found errors

**Solutions:**

1. **Check data file**:

   ```bash
   ls -la data/quiz_questions.json
   ```

2. **Verify file permissions**:

   ```bash
   chmod 644 data/quiz_questions.json
   ```

3. **Check file format**:
   ```bash
   python -m json.tool data/quiz_questions.json
   ```

#### Issue: Questions not saving

**Symptoms:**

- Save operations fail
- Data not persisted

**Solutions:**

1. **Check directory permissions**:

   ```bash
   ls -la data/
   chmod 755 data/
   ```

2. **Verify disk space**:

   ```bash
   df -h
   ```

3. **Check file locks**:
   - Ensure no other processes are writing
   - Restart application if needed

### AI Service Issues

#### Issue: AI feedback generation fails

**Symptoms:**

- `500 Internal Server Error` for feedback generation
- AI service errors

**Solutions:**

1. **Check Azure OpenAI configuration**:

   ```bash
   curl http://localhost:8080/debug/config
   ```

2. **Verify system prompt**:

   ```bash
   cat config/system_prompt.txt
   ```

3. **Test AI service directly**:
   ```bash
   curl -X POST http://localhost:8080/questions/1/generate-feedback
   ```

#### Issue: Chat functionality not working

**Symptoms:**

- Chat responses fail
- Vector store errors

**Solutions:**

1. **Check vector store status**:

   ```bash
   curl http://localhost:8080/vector-store/status
   ```

2. **Recreate vector store**:

   ```bash
   curl -X POST http://localhost:8080/vector-store/create
   ```

3. **Verify Ollama service**:
   ```bash
   curl http://localhost:8080/debug/ollama-test
   ```

## Performance Issues

### Slow Response Times

#### Issue: API calls are slow

**Symptoms:**

- Long response times
- Timeout errors

**Solutions:**

1. **Check network connectivity**:

   ```bash
   ping your-canvas-instance.instructure.com
   ```

2. **Monitor resource usage**:

   ```bash
   top
   htop
   ```

3. **Optimize configuration**:
   - Increase timeout values
   - Use connection pooling
   - Implement caching

#### Issue: Vector store operations are slow

**Symptoms:**

- Slow search responses
- Long embedding generation times

**Solutions:**

1. **Check Ollama performance**:

   ```bash
   ollama list
   ```

2. **Optimize embedding model**:

   - Use smaller model if available
   - Reduce chunk size
   - Implement caching

3. **Monitor system resources**:
   - Check CPU and memory usage
   - Ensure adequate resources

### Memory Issues

#### Issue: High memory usage

**Symptoms:**

- Application crashes
- Out of memory errors

**Solutions:**

1. **Monitor memory usage**:

   ```bash
   ps aux | grep python
   ```

2. **Optimize data loading**:

   - Implement pagination
   - Use streaming for large files
   - Clear unused data

3. **Check for memory leaks**:
   - Monitor memory over time
   - Restart application periodically

## Debugging Tools

### Debug Endpoints

Use built-in debug endpoints to diagnose issues:

```bash
# Check configuration
curl http://localhost:8080/debug/config

# Test Ollama connection
curl http://localhost:8080/debug/ollama-test

# Inspect specific question
curl http://localhost:8080/debug/question/1
```

### Logging

#### Enable Debug Logging

1. **Set log level**:

   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check log files**:

   ```bash
   tail -f canvas_app.log
   ```

3. **Add custom logging**:
   ```python
   logger = get_logger(__name__)
   logger.debug("Debug message")
   logger.error("Error message", extra={"context": "additional info"})
   ```

### Testing

#### Run Tests to Verify Functionality

```bash
# Run all tests
poetry run test

# Run specific test
poetry run pytest tests/unit/test_core/test_config.py -v

# Run with coverage
poetry run test --coverage
```

## Common Error Messages

### Canvas API Errors

| Error                   | Cause                    | Solution                      |
| ----------------------- | ------------------------ | ----------------------------- |
| `401 Unauthorized`      | Invalid API token        | Regenerate Canvas API token   |
| `403 Forbidden`         | Insufficient permissions | Check token permissions       |
| `404 Not Found`         | Invalid course/quiz ID   | Verify IDs from Canvas URLs   |
| `429 Too Many Requests` | Rate limiting            | Implement exponential backoff |

### Azure OpenAI Errors

| Error              | Cause                       | Solution                              |
| ------------------ | --------------------------- | ------------------------------------- |
| `401 Unauthorized` | Invalid subscription key    | Check Azure portal for correct key    |
| `404 Not Found`    | Invalid endpoint/deployment | Verify endpoint URL and deployment ID |
| `400 Bad Request`  | Invalid API version         | Use supported API version             |

### Application Errors

| Error                    | Cause                | Solution                                    |
| ------------------------ | -------------------- | ------------------------------------------- |
| `ModuleNotFoundError`    | Missing dependencies | Run `poetry install`                        |
| `Address already in use` | Port conflict        | Kill existing process or use different port |
| `File not found`         | Missing data files   | Check file paths and permissions            |

## Getting Help

### Self-Diagnosis

1. **Check application logs**:

   ```bash
   tail -f canvas_app.log
   ```

2. **Verify configuration**:

   ```bash
   curl http://localhost:8080/debug/config
   ```

3. **Test individual components**:
   - Test Canvas API directly
   - Test Azure OpenAI directly
   - Test Ollama service

### External Resources

- **Canvas API Documentation**: [Canvas API Docs](https://canvas.instructure.com/doc/api/)
- **Azure OpenAI Documentation**: [Azure OpenAI Docs](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- **Ollama Documentation**: [Ollama Docs](https://ollama.ai/docs)
- **FastAPI Documentation**: [FastAPI Docs](https://fastapi.tiangolo.com/)

### Support Channels

- **GitHub Issues**: Create issue in project repository
- **Documentation**: Check this troubleshooting guide
- **Community**: Check project discussions

## Prevention

### Best Practices

1. **Regular maintenance**:

   - Update dependencies regularly
   - Monitor application logs
   - Test functionality periodically

2. **Configuration management**:

   - Use environment variables
   - Backup configuration files
   - Document configuration changes

3. **Monitoring**:

   - Set up health checks
   - Monitor resource usage
   - Track error rates

4. **Testing**:
   - Run tests regularly
   - Test in staging environment
   - Validate configuration changes

### Proactive Measures

1. **Set up monitoring**:

   - Application health endpoints
   - Resource usage monitoring
   - Error tracking

2. **Implement logging**:

   - Structured logging
   - Error tracking
   - Performance monitoring

3. **Create backups**:

   - Configuration backups
   - Data backups
   - Documentation backups

4. **Document procedures**:
   - Installation procedures
   - Configuration procedures
   - Troubleshooting procedures
