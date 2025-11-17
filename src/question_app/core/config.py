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

    def __init__(self):
        # Canvas LMS Configuration
        self.CANVAS_BASE_URL: Optional[str] = os.getenv("CANVAS_BASE_URL")
        self.CANVAS_API_TOKEN: Optional[str] = os.getenv("CANVAS_API_TOKEN")
        self.COURSE_ID: Optional[str] = os.getenv("COURSE_ID")
        self.QUIZ_ID: Optional[str] = os.getenv("QUIZ_ID")

        # Azure OpenAI Configuration
        self.AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv(
            "AZURE_OPENAI_ENDPOINT", "https://itls-openai-connect.azure-api.net"
        )
        self.AZURE_OPENAI_DEPLOYMENT_ID: Optional[str] = os.getenv(
            "AZURE_OPENAI_DEPLOYMENT_ID"
        )
        self.AZURE_OPENAI_API_VERSION: str = os.getenv(
            "AZURE_OPENAI_API_VERSION", "2023-12-01-preview"
        )
        self.AZURE_OPENAI_SUBSCRIPTION_KEY: Optional[str] = os.getenv(
            "AZURE_OPENAI_SUBSCRIPTION_KEY"
        )

        # Ollama Configuration
        self.OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.OLLAMA_EMBEDDING_MODEL: str = os.getenv(
            "OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"
        )

        # Application Configuration
        self.APP_TITLE: str = "Canvas Quiz Manager"
        self.LOG_FILE: str = "canvas_app.log"


        #ChromaDB Configuration
        self.CHROMA_HOST : str = os.getenv("CHROMA_HOST" , "localhost")
        self.CHROMA_PORT : int = int(os.getenv("CHROMA_PORT" , 8000))

    def validate_canvas_config(self) -> bool:
        """Validate that Canvas configuration is complete."""
        return all(
            [self.CANVAS_BASE_URL, self.CANVAS_API_TOKEN, self.COURSE_ID, self.QUIZ_ID]
        )

    def validate_azure_openai_config(self) -> bool:
        """Validate that Azure OpenAI configuration is complete."""
        return all(
            [
                self.AZURE_OPENAI_ENDPOINT,
                self.AZURE_OPENAI_DEPLOYMENT_ID,
                self.AZURE_OPENAI_SUBSCRIPTION_KEY,
            ]
        )

    def get_missing_canvas_configs(self) -> list[str]:
        """Get list of missing Canvas configuration variables."""
        missing = []
        if not self.CANVAS_BASE_URL:
            missing.append("CANVAS_BASE_URL")
        if not self.CANVAS_API_TOKEN:
            missing.append("CANVAS_API_TOKEN")
        if not self.COURSE_ID:
            missing.append("COURSE_ID")
        if not self.QUIZ_ID:
            missing.append("QUIZ_ID")
        return missing

    def get_missing_azure_openai_configs(self) -> list[str]:
        """Get list of missing Azure OpenAI configuration variables."""
        missing = []
        if not self.AZURE_OPENAI_ENDPOINT:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not self.AZURE_OPENAI_DEPLOYMENT_ID:
            missing.append("AZURE_OPENAI_DEPLOYMENT_ID")
        if not self.AZURE_OPENAI_SUBSCRIPTION_KEY:
            missing.append("AZURE_OPENAI_SUBSCRIPTION_KEY")
        return missing


# Create a global config instance
config = Config()
