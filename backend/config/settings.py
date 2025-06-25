"""
Configuration settings module for the Agentic Assistant.

This module handles application configuration using Pydantic Settings,
which automatically loads environment variables and provides type safety.
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings class that defines all configuration parameters.
    
    This class uses Pydantic's BaseSettings to automatically load
    environment variables and provide type validation. All settings
    are loaded from the .env file or environment variables.
    """
    # API key for Anthropic Claude model
    ANTHROPIC_API_KEY: str

    class Config:
        """
        Pydantic configuration for settings loading.
        
        Specifies that settings should be loaded from a .env file
        with UTF-8 encoding.
        """
        env_file = ".env"  # Load environment variables from .env file
        env_file_encoding = "utf-8"  # Use UTF-8 encoding for the .env file

# Global settings instance that can be imported throughout the application
settings = Settings()