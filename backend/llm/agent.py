"""
Agent configuration module for the LangGraph-based AI assistant.

This module creates and configures the main AI agent using LangGraph's
React agent pattern, which enables the agent to use tools and maintain
conversation state across interactions.
"""

from backend.llm.init_llm import claude
from backend.llm.tools import TOOLS
from backend.llm.prompts import test_react_agent_main_prompt
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver


# Create the main AI agent using LangGraph's React agent pattern
# This agent can use tools, maintain conversation state, and handle complex workflows
agent = create_react_agent(
    model=claude,                    # The LLM model (Claude 3.7 Sonnet)
    tools=TOOLS,                     # Available tools for the agent to use
    prompt=test_react_agent_main_prompt,  # System prompt defining agent behavior
    checkpointer=MemorySaver(),      # Memory system for maintaining conversation state
)


