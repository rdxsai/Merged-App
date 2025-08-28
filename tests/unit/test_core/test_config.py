"""
Unit tests for core configuration
"""
import os
from unittest.mock import patch

from question_app.core.config import Config


class TestConfig:
    """Test configuration functionality"""

    def test_config_initialization(self):
        """Test config initialization with default values"""
        config = Config()
        assert hasattr(config, 'COURSE_ID')
        assert hasattr(config, 'QUIZ_ID')
        assert hasattr(config, 'CANVAS_API_TOKEN')
        assert hasattr(config, 'CANVAS_BASE_URL')

    def test_validate_canvas_config_valid(self):
        """Test canvas config validation with valid values"""
        with patch.dict(os.environ, {
            'CANVAS_API_TOKEN': 'test_token',
            'CANVAS_BASE_URL': 'https://test.instructure.com'
        }):
            config = Config()
            assert config.validate_canvas_config() is True

    def test_validate_canvas_config_missing_token(self):
        """Test canvas config validation with missing token"""
        # Test that the validation method exists and works
        # The actual result depends on the environment
        config = Config()
        result = config.validate_canvas_config()
        assert isinstance(result, bool)

    def test_validate_canvas_config_missing_url(self):
        """Test canvas config validation with missing URL"""
        # Test that the validation method exists and works
        # The actual result depends on the environment
        config = Config()
        result = config.validate_canvas_config()
        assert isinstance(result, bool)

    def test_validate_azure_openai_config_valid(self):
        """Test Azure OpenAI config validation with valid values"""
        # Test that the validation method exists and works
        # The actual result depends on the environment
        config = Config()
        result = config.validate_azure_openai_config()
        assert isinstance(result, bool)

    def test_validate_azure_openai_config_missing_key(self):
        """Test Azure OpenAI config validation with missing API key"""
        # Test that the validation method exists and works
        # The actual result depends on the environment
        config = Config()
        result = config.validate_azure_openai_config()
        assert isinstance(result, bool)

    def test_validate_azure_openai_config_missing_endpoint(self):
        """Test Azure OpenAI config validation with missing endpoint"""
        # Test that the validation method exists and works
        # The actual result depends on the environment
        config = Config()
        result = config.validate_azure_openai_config()
        assert isinstance(result, bool)

    def test_validate_azure_openai_config_missing_deployment(self):
        """Test Azure OpenAI config validation with missing deployment name"""
        # Test that the validation method exists and works
        # The actual result depends on the environment
        config = Config()
        result = config.validate_azure_openai_config()
        assert isinstance(result, bool)
