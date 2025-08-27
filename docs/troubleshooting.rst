Troubleshooting Guide
====================

This guide helps you resolve common issues when using the Canvas Quiz Manager application.

Common Issues
-------------

Azure OpenAI Configuration Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: "Azure OpenAI configuration incomplete" error

**Symptoms**:
- Error messages about missing configuration
- AI feedback generation fails
- Chat assistant doesn't work

**Solutions**:

1. **Check Environment Variables**:
   .. code-block:: bash
   
       # Verify all required variables are set
       echo $AZURE_OPENAI_ENDPOINT
       echo $AZURE_OPENAI_DEPLOYMENT_ID
       echo $AZURE_OPENAI_SUBSCRIPTION_KEY
       echo $AZURE_OPENAI_API_VERSION

2. **Set Missing Variables**:
   .. code-block:: bash
   
       export AZURE_OPENAI_ENDPOINT="https://your-endpoint.azure-api.net"
       export AZURE_OPENAI_DEPLOYMENT_ID="your-deployment-id"
       export AZURE_OPENAI_SUBSCRIPTION_KEY="your-subscription-key"
       export AZURE_OPENAI_API_VERSION="2023-12-01-preview"

3. **Test Configuration**:
   .. code-block:: bash
   
       python test_azure_openai.py

**Problem**: Azure OpenAI API errors

**Symptoms**:
- HTTP 401/403 errors
- "Invalid API key" messages
- Rate limiting errors

**Solutions**:

1. **Verify API Key**:
   - Check that your subscription key is correct
   - Ensure the key has proper permissions
   - Verify the key hasn't expired

2. **Check Endpoint URL**:
   - Ensure the endpoint URL is correct
   - Verify the deployment ID exists
   - Check API version compatibility

3. **Handle Rate Limits**:
   - Implement retry logic with exponential backoff
   - Reduce request frequency
   - Check your Azure OpenAI quota

Canvas LMS Integration Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Cannot fetch courses from Canvas

**Symptoms**:
- "Canvas configuration missing" errors
- Empty course lists
- HTTP 401/403 errors

**Solutions**:

1. **Verify Canvas Configuration**:
   .. code-block:: bash
   
       echo $CANVAS_BASE_URL
       echo $CANVAS_API_TOKEN
       echo $COURSE_ID

2. **Check API Token Permissions**:
   - Ensure the token has read access to courses
   - Verify the token hasn't expired
   - Check that the token is for the correct Canvas instance

3. **Test Canvas Connection**:
   .. code-block:: python
   
       import httpx
       import asyncio
       
       async def test_canvas():
           headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
           async with httpx.AsyncClient() as client:
               response = await client.get(
                   f"{CANVAS_BASE_URL}/api/v1/courses",
                   headers=headers
               )
               print(f"Status: {response.status_code}")
               print(f"Response: {response.text[:200]}")
       
       asyncio.run(test_canvas())

**Problem**: Quiz questions not loading

**Symptoms**:
- Empty question lists
- "Quiz not found" errors
- Missing question content

**Solutions**:

1. **Verify Quiz ID**:
   - Check that the quiz ID is correct
   - Ensure the quiz is published
   - Verify the quiz is accessible to your API token

2. **Check Question Permissions**:
   - Ensure your API token can access quiz questions
   - Verify the quiz is not draft mode
   - Check course enrollment status

Ollama Embedding Issues
~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Ollama connection errors

**Symptoms**:
- "Connection refused" errors
- Embedding generation fails
- Vector search not working

**Solutions**:

1. **Check Ollama Service**:
   .. code-block:: bash
   
       # Check if Ollama is running
       curl http://localhost:11434/api/tags
       
       # Start Ollama if not running
       ollama serve

2. **Verify Model Installation**:
   .. code-block:: bash
   
       # List installed models
       ollama list
       
       # Install nomic-embed-text if missing
       ollama pull nomic-embed-text

3. **Test Ollama Connection**:
   .. code-block:: python
   
       import httpx
       import asyncio
       
       async def test_ollama():
           async with httpx.AsyncClient() as client:
               response = await client.post(
                   "http://localhost:11434/api/embeddings",
                   json={"model": "nomic-embed-text", "prompt": "test"}
               )
               print(f"Status: {response.status_code}")
               print(f"Response: {response.text[:200]}")
       
       asyncio.run(test_ollama())

**Problem**: Slow embedding generation

**Symptoms**:
- Long delays when generating embeddings
- Timeout errors
- Poor performance

**Solutions**:

1. **Optimize Ollama Settings**:
   - Increase Ollama memory allocation
   - Use GPU acceleration if available
   - Reduce batch sizes

2. **Check System Resources**:
   - Monitor CPU and memory usage
   - Ensure adequate disk space
   - Check network connectivity

Vector Store Issues
~~~~~~~~~~~~~~~~~~

**Problem**: ChromaDB errors

**Symptoms**:
- "Collection not found" errors
- Vector search failures
- Database corruption

**Solutions**:

1. **Reset Vector Store**:
   .. code-block:: bash
   
       # Remove existing vector store
       rm -rf vector_store/
       
       # Recreate vector store
       python -c "from question_app.main import create_vector_store; import asyncio; asyncio.run(create_vector_store())"

2. **Check ChromaDB Installation**:
   .. code-block:: bash
   
       pip install --upgrade chromadb
       
       # Test ChromaDB
       python -c "import chromadb; print('ChromaDB working')"

3. **Verify Vector Store Integrity**:
   .. code-block:: python
   
       import chromadb
       
       client = chromadb.PersistentClient(path="./vector_store")
       collections = client.list_collections()
       print(f"Collections: {collections}")

Development Tool Issues
~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Code formatting fails

**Symptoms**:
- Black formatting errors
- Import sorting issues
- Linting failures

**Solutions**:

1. **Install Development Dependencies**:
   .. code-block:: bash
   
       poetry install --with dev
       
       # Or install manually
       pip install black isort flake8 mypy

2. **Check Python Version**:
   .. code-block:: bash
   
       python --version
       # Ensure you're using Python 3.8+

3. **Run Individual Tools**:
   .. code-block:: bash
   
       # Test Black
       black --check .
       
       # Test isort
       isort --check-only .
       
       # Test Flake8
       flake8 .

**Problem**: Tests failing

**Symptoms**:
- Test suite errors
- Import errors in tests
- Mock failures

**Solutions**:

1. **Install Test Dependencies**:
   .. code-block:: bash
   
       pip install pytest pytest-asyncio httpx

2. **Run Tests with Verbose Output**:
   .. code-block:: bash
   
       pytest -v --tb=short

3. **Check Test Configuration**:
   - Verify pytest.ini settings
   - Check conftest.py fixtures
   - Ensure test data files exist

Performance Issues
~~~~~~~~~~~~~~~~~

**Problem**: Slow application startup

**Symptoms**:
- Long startup times
- Memory usage spikes
- Slow first request

**Solutions**:

1. **Optimize Imports**:
   - Use lazy imports where possible
   - Remove unused dependencies
   - Profile import times

2. **Check Environment**:
   - Monitor system resources
   - Check disk I/O
   - Verify network connectivity

3. **Use Production Server**:
   .. code-block:: bash
   
       # Use uvicorn with workers
       uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

**Problem**: High memory usage

**Symptoms**:
- Memory leaks
- Slow performance
- Out of memory errors

**Solutions**:

1. **Monitor Memory Usage**:
   .. code-block:: python
   
       import psutil
       import os
       
       process = psutil.Process(os.getpid())
       print(f"Memory usage: {process.memory_info().rss / 1024 / 1024} MB")

2. **Optimize Vector Store**:
   - Limit embedding batch sizes
   - Implement pagination
   - Use streaming responses

3. **Profile Application**:
   - Use memory profilers
   - Identify memory leaks
   - Optimize data structures

Debugging Techniques
-------------------

Logging
~~~~~~~

Enable detailed logging to diagnose issues:

.. code-block:: python

    import logging
    
    # Set up detailed logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

Check the application log file:
.. code-block:: bash

    tail -f canvas_app.log

Environment Validation
~~~~~~~~~~~~~~~~~~~~~

Create a validation script to check your environment:

.. code-block:: python

    import os
    import asyncio
    import httpx
    
    async def validate_environment():
        """Validate all environment configurations"""
        
        print("🔍 Validating Environment...")
        
        # Check environment variables
        required_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT_ID", 
            "AZURE_OPENAI_SUBSCRIPTION_KEY",
            "CANVAS_BASE_URL",
            "CANVAS_API_TOKEN"
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if value:
                print(f"✅ {var}: Set")
            else:
                print(f"❌ {var}: Missing")
        
        # Test Ollama
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    print("✅ Ollama: Running")
                else:
                    print("❌ Ollama: Not responding")
        except Exception as e:
            print(f"❌ Ollama: {e}")
        
        # Test ChromaDB
        try:
            import chromadb
            client = chromadb.PersistentClient(path="./vector_store")
            collections = client.list_collections()
            print(f"✅ ChromaDB: {len(collections)} collections")
        except Exception as e:
            print(f"❌ ChromaDB: {e}")
    
    asyncio.run(validate_environment())

Getting Help
-----------

If you're still experiencing issues:

1. **Check the Logs**: Review `canvas_app.log` for detailed error messages
2. **Run Validation**: Use the environment validation script above
3. **Test Components**: Use individual test scripts for each component
4. **Check Documentation**: Review the API documentation and examples
5. **Report Issues**: Create a detailed bug report with:
   - Error messages and stack traces
   - Environment information
   - Steps to reproduce
   - Expected vs actual behavior

Common Error Messages
--------------------

.. code-block:: text

    "Azure OpenAI configuration incomplete"
    → Check AZURE_OPENAI_* environment variables
    
    "Canvas configuration missing"
    → Verify CANVAS_BASE_URL and CANVAS_API_TOKEN
    
    "Connection refused" (Ollama)
    → Start Ollama service: ollama serve
    
    "Collection not found" (ChromaDB)
    → Recreate vector store or check permissions
    
    "Import error" (Development tools)
    → Install missing dependencies: pip install -r requirements.txt
