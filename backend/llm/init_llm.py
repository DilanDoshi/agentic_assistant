"""
LLM initialization module for the Agentic Assistant.

This module initializes and configures the Claude 3.7 Sonnet model
from Anthropic using the API key from environment settings.
"""

from langchain_anthropic import ChatAnthropic
from backend.config.settings import settings

# Initialize the Claude 3.7 Sonnet model with API key from settings
# This model will be used by the agent for all LLM operations
claude = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",  # Specific model version for consistency
    api_key=settings.ANTHROPIC_API_KEY,  # API key loaded from environment variables
)