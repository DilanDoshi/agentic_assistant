"""
Chat pipeline module for the Agentic Assistant.

This module handles the conversation flow between users and the AI agent,
including thread management and response processing.
"""

import uuid


def chat_with_agent(agent, user_input: str, thread_id: str):
    """
    Process a user message through the AI agent and return the response.
    
    This function handles the conversation flow by invoking the agent with
    the user's input and maintaining conversation context through thread IDs.
    
    Args:
        agent: The LangGraph agent instance to use for processing
        user_input (str): The user's message to process
        thread_id (str): Unique identifier for the conversation thread
        
    Returns:
        str: The AI agent's response to the user's input
    """
    # Ensure we have a valid thread ID for conversation tracking
    if not thread_id:
        thread_id = create_chat_id()
        print ("USING CHAT ID: ", thread_id)

    # Configure the agent with the thread ID for conversation continuity
    config = {
    "configurable": {
        "thread_id": thread_id
            }
        }
    
    # Invoke the agent with the user's message and thread configuration
    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config
    )
    
    # Extract the AI's response from the last message in the conversation
    ai_response = response['messages'][-1].content
    
    return ai_response


def create_chat_id() -> str:
    """
    Generate a unique identifier for a chat session.
    
    This function creates a UUID4 string that serves as a unique identifier
    for tracking conversation threads and maintaining context across
    multiple interactions.
    
    Returns:
        str: A unique UUID4 string identifier
    """
    return str(uuid.uuid4())


