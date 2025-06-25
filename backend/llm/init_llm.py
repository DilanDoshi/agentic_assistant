from langchain_anthropic import ChatAnthropic
from backend.config.settings import settings

claude = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    api_key=settings.ANTHROPIC_API_KEY,
)