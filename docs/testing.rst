Testing Guide
============

This guide covers testing procedures and tools for the Canvas Quiz Manager application.

Test Suite
---------

The application includes a comprehensive test suite located in the `tests/` directory:

.. code-block:: text

   tests/
   ├── conftest.py                    # Test configuration and fixtures
   ├── test_ai_integration.py         # AI service integration tests
   ├── test_api_endpoints.py          # API endpoint tests
   ├── test_integration.py            # Integration tests
   └── test_utility_functions.py      # Utility function tests

Running Tests
------------

.. code-block:: bash

   # Run all tests
   poetry run pytest

   # Run with coverage
   poetry run pytest --cov=question_app

   # Run specific test file
   poetry run pytest tests/test_api_endpoints.py

   # Run with verbose output
   poetry run pytest -v

Azure OpenAI Testing
-------------------

The `test_azure_openai.py` script provides comprehensive testing for Azure OpenAI
service connectivity and functionality.

Purpose
~~~~~~~

This standalone script is designed to:

- Validate Azure OpenAI configuration
- Test basic connectivity to the service
- Verify API functionality with simple requests
- Simulate realistic quiz feedback generation scenarios
- Provide detailed error reporting and debugging information

Usage
~~~~~

.. code-block:: bash

   # Run the Azure OpenAI test script
   python test_azure_openai.py

   # Or with Poetry
   poetry run python test_azure_openai.py

Test Functions
~~~~~~~~~~~~~

.. automodule:: test_azure_openai
   :members:
   :undoc-members:
   :show-inheritance:

Configuration Validation
~~~~~~~~~~~~~~~~~~~~~~~

The script validates the following environment variables:

- **AZURE_OPENAI_ENDPOINT**: Azure OpenAI service endpoint URL
- **AZURE_OPENAI_DEPLOYMENT_ID**: Model deployment ID
- **AZURE_OPENAI_API_VERSION**: API version (optional, defaults to 2023-12-01-preview)
- **AZURE_OPENAI_SUBSCRIPTION_KEY**: Azure subscription key

Test Scenarios
~~~~~~~~~~~~~

1. **Basic Connection Test**
   - Tests HTTP connectivity to the endpoint
   - Verifies the service is reachable
   - Handles expected 404 responses for base URLs

2. **API Endpoint Test**
   - Sends a simple chat completion request
   - Validates API authentication and functionality
   - Displays the AI response for verification

3. **Quiz Feedback Scenario Test**
   - Simulates realistic quiz feedback generation
   - Tests the same prompt format used by the main application
   - Validates response parsing and structure

Example Output
~~~~~~~~~~~~~

.. code-block:: text

   🧪 Azure OpenAI Connection Test
   ==================================================

   🔧 Configuration:
      Endpoint: https://your-endpoint.azure-api.net
      Deployment ID: gpt-4-deployment
      API Version: 2023-12-01-preview
      Subscription Key: ****************abcd

   ✅ All required configuration present

   🌐 Testing basic connection...
      Status: 404
      Headers: {'content-type': 'application/json', ...}
      ✅ Endpoint is reachable (404 is expected for base URL)

   🤖 Testing Azure OpenAI API endpoint...
      API URL: https://your-endpoint.azure-api.net/us-east/deployments/...
      ✅ API call successful!
      🤖 AI Response: 'Hello, this is a test!'

   📝 Testing quiz feedback generation scenario...
      ✅ Quiz feedback generation successful!
      🤖 Generated feedback:
      Correct feedback: Excellent! You correctly identified Paris as the capital of France.
      Incorrect feedback: The correct answer is Paris, the capital of France.
      General feedback: Understanding world capitals is important for geography.

   🎉 All tests passed! Azure OpenAI is working correctly.

Troubleshooting
~~~~~~~~~~~~~~

Common Issues
^^^^^^^^^^^^

1. **Missing Environment Variables**
   - Ensure all required environment variables are set
   - Check the `.env` file or system environment

2. **Connection Failures**
   - Verify the endpoint URL is correct
   - Check network connectivity
   - Ensure the service is available

3. **Authentication Errors**
   - Verify the subscription key is correct
   - Check API permissions and quotas
   - Ensure the deployment ID exists

4. **API Errors**
   - Review the error response details
   - Check API version compatibility
   - Verify request format and parameters

Debugging Steps
^^^^^^^^^^^^^^

1. **Check Configuration**
   - Review the displayed configuration
   - Verify environment variables are loaded

2. **Test Connectivity**
   - Run the basic connection test first
   - Check for network or firewall issues

3. **Review API Responses**
   - Examine error messages and status codes
   - Check Azure OpenAI service status

4. **Validate Credentials**
   - Test with Azure CLI or other tools
   - Verify subscription and deployment access

Integration with Main Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The test script validates the same configuration and API calls used by the main
application, ensuring compatibility and reliability.

Key Integration Points:

- **Configuration Loading**: Uses the same environment variable names
- **API Endpoints**: Tests the same URL construction logic
- **Request Format**: Validates the same payload structure
- **Response Handling**: Tests the same parsing logic

Development Testing
------------------

Unit Tests
~~~~~~~~~~

The test suite includes comprehensive unit tests for all major components:

.. code-block:: bash

   # Run unit tests only
   poetry run pytest tests/test_utility_functions.py

   # Run with coverage report
   poetry run pytest --cov=question_app --cov-report=html

Integration Tests
~~~~~~~~~~~~~~~~

Integration tests verify component interactions:

.. code-block:: bash

   # Run integration tests
   poetry run pytest tests/test_integration.py

API Tests
~~~~~~~~~

API endpoint tests validate HTTP functionality:

.. code-block:: bash

   # Run API tests
   poetry run pytest tests/test_api_endpoints.py

Test Fixtures
------------

Common test fixtures are defined in `tests/conftest.py`:

.. automodule:: tests.conftest
   :members:
   :undoc-members:
   :show-inheritance:

Mock Services
~~~~~~~~~~~~

The test suite includes mocks for external services:

- **Canvas API**: Mocked Canvas LMS API responses
- **Azure OpenAI**: Mocked AI service responses
- **Ollama**: Mocked embedding service responses

Continuous Integration
---------------------

The test suite is designed to run in CI/CD environments:

.. code-block:: yaml

   # Example GitHub Actions configuration
   - name: Run tests
     run: |
       poetry install
       poetry run pytest --cov=question_app --cov-report=xml

   - name: Upload coverage
     uses: codecov/codecov-action@v3
     with:
       file: ./coverage.xml

Test Coverage
------------

The test suite aims for comprehensive coverage of:

- **Core Functions**: All utility and business logic functions
- **API Endpoints**: All HTTP endpoints and request/response handling
- **Error Handling**: Exception scenarios and error responses
- **Integration**: Component interactions and data flow
- **Configuration**: Environment variable handling and validation

Best Practices
-------------

Writing Tests
~~~~~~~~~~~~

1. **Test Structure**
   - Use descriptive test names
   - Follow the Arrange-Act-Assert pattern
   - Include both positive and negative test cases

2. **Test Data**
   - Use realistic test data
   - Create reusable fixtures
   - Avoid hardcoded values

3. **Mocking**
   - Mock external dependencies
   - Use appropriate mock responses
   - Verify mock interactions

4. **Assertions**
   - Test specific outcomes
   - Include meaningful error messages
   - Verify both success and failure scenarios

Maintaining Tests
~~~~~~~~~~~~~~~~

1. **Keep Tests Updated**
   - Update tests when functionality changes
   - Maintain test data consistency
   - Review test coverage regularly

2. **Test Documentation**
   - Document complex test scenarios
   - Explain test data requirements
   - Provide troubleshooting guidance

3. **Performance**
   - Keep tests fast and efficient
   - Use appropriate timeouts
   - Avoid unnecessary external calls
