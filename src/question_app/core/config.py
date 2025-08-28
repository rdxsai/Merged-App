"""
Configuration management for the Question App.

This module centralizes all environment variable loading and configuration
management for the application.
"""

import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Centralized configuration management for the Question App."""
    
    # Canvas LMS Configuration
    CANVAS_BASE_URL: Optional[str] = os.getenv("CANVAS_BASE_URL")
    CANVAS_API_TOKEN: Optional[str] = os.getenv("CANVAS_API_TOKEN")
    COURSE_ID: Optional[str] = os.getenv("COURSE_ID")
    QUIZ_ID: Optional[str] = os.getenv("QUIZ_ID")
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv(
        "AZURE_OPENAI_ENDPOINT", 
        "https://itls-openai-connect.azure-api.net"
    )
    AZURE_OPENAI_DEPLOYMENT_ID: Optional[str] = os.getenv(
        "AZURE_OPENAI_DEPLOYMENT_ID"
    )
    AZURE_OPENAI_API_VERSION: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2023-12-01-preview"
    )
    AZURE_OPENAI_SUBSCRIPTION_KEY: Optional[str] = os.getenv(
        "AZURE_OPENAI_SUBSCRIPTION_KEY"
    )
    
    # Ollama Configuration
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv(
        "OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"
    )
    
    # Application Configuration
    APP_TITLE: str = "Canvas Quiz Manager"
    LOG_FILE: str = "canvas_app.log"
    
    @classmethod
    def validate_canvas_config(cls) -> bool:
        """Validate that Canvas configuration is complete."""
        return all([
            cls.CANVAS_BASE_URL,
            cls.CANVAS_API_TOKEN,
            cls.COURSE_ID,
            cls.QUIZ_ID
        ])
    
    @classmethod
    def validate_azure_openai_config(cls) -> bool:
        """Validate that Azure OpenAI configuration is complete."""
        return all([
            cls.AZURE_OPENAI_ENDPOINT,
            cls.AZURE_OPENAI_DEPLOYMENT_ID,
            cls.AZURE_OPENAI_SUBSCRIPTION_KEY
        ])
    
    @classmethod
    def get_missing_canvas_configs(cls) -> list[str]:
        """Get list of missing Canvas configuration variables."""
        missing = []
        if not cls.CANVAS_BASE_URL:
            missing.append("CANVAS_BASE_URL")
        if not cls.CANVAS_API_TOKEN:
            missing.append("CANVAS_API_TOKEN")
        if not cls.COURSE_ID:
            missing.append("COURSE_ID")
        if not cls.QUIZ_ID:
            missing.append("QUIZ_ID")
        return missing
    
    @classmethod
    def get_missing_azure_openai_configs(cls) -> list[str]:
        """Get list of missing Azure OpenAI configuration variables."""
        missing = []
        if not cls.AZURE_OPENAI_ENDPOINT:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not cls.AZURE_OPENAI_DEPLOYMENT_ID:
            missing.append("AZURE_OPENAI_DEPLOYMENT_ID")
        if not cls.AZURE_OPENAI_SUBSCRIPTION_KEY:
            missing.append("AZURE_OPENAI_SUBSCRIPTION_KEY")
        return missing


# Create a global config instance
config = Config()
