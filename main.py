"""
Main entry point for the Agentic Assistant application.

This module provides the main interface for interacting with the AI agent
that can help with email management, drafting responses, and other tasks.
"""

from backend.llm.agent import agent
from backend.pipelines.chat import chat_with_agent, create_chat_id
from backend.llm.tools import create_drafts_for_unread_emails
from backend.google.gmail_client import GmailClient

def test1():
    """
    Test function to demonstrate the agent's capabilities.
    
    This function invokes the agent with a specific query about unread emails
    and displays detailed information about the AI responses, tool calls,
    and tool results in a formatted output.
    """
    # Invoke the agent with a test query about unread emails
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "what are my unread emails? Max 10"}]}
    )
    
    # Extract messages from the result
    messages = result.get('messages', [])
    
    # Display AI responses with detailed formatting
    print("🤖 AI RESPONSES:")
    print("=" * 50)
    
    # Iterate through all messages and display their content
    for i, message in enumerate(messages):
        if hasattr(message, 'content'):
            # Check if message has tool calls (indicates AI used tools)
            if hasattr(message, 'tool_calls') and message.tool_calls:
                print(f"\n📋 AI Response {i+1} (with tool calls):")
                print(f"Content: {message.content}")
                print(f"Tool Calls: {message.tool_calls}")
            else:
                # Regular AI response without tool usage
                print(f"\n💬 AI Response {i+1}:")
                print(f"Content: {message.content}")
    
    # Display summary of all tool calls made by the agent
    print("\n🔧 TOOL CALLS SUMMARY:")
    print("=" * 50)
    
    for i, message in enumerate(messages):
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                print(f"Tool: {tool_call['name']}")
                print(f"Arguments: {tool_call['args']}")
                print(f"ID: {tool_call['id']}")
                print("-" * 30)
    
    # Display results returned by tools
    print("\n📧 TOOL RESULTS:")
    print("=" * 50)
    
    for i, message in enumerate(messages):
        if hasattr(message, 'name') and message.name:  # ToolMessage
            print(f"Tool: {message.name}")
            print(f"Result: {message.content}")
            print("-" * 30)

def run_chat():
    """
    Interactive chat function that allows continuous conversation with the AI agent.
    
    This function creates a chat session with a unique thread ID and runs
    an infinite loop that accepts user input and displays AI responses.
    Users can exit by typing 'exit', 'quit', or 'bye'.
    """
    print("\n\nClaude: Welcome to the Agentic Assistant! I am an AI assistant that can help you see and understand unread emails and create drafts that are ready to send. \nI can also act as a regular LLM and answer any questions you may have. Type 'exit', 'quit', or 'bye' to end the conversation.")
    # Create a unique thread ID for this chat session
    thread_id = create_chat_id()
    
    # Main chat loop
    while True:
        # Get user input
        user_input = input("\n\nYou: ")
        
        # Check for exit commands
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break

        # Get AI response using the chat pipeline
        ai_response = chat_with_agent(agent, user_input, thread_id)
        print(f"\n\nClaude: {ai_response}")

def main():
    """
    Main function that serves as the entry point for the application.
    
    Currently runs the interactive chat interface. There's also a commented
    line that can be used to test the email draft creation functionality.

    This is for testing until the full stack app is built.
    """
    # Start the interactive chat interface
    run_chat()
    
    # Alternative: Test email draft creation (currently commented out)
    #print(create_drafts_for_unread_emails(['197a47fc64229a54']))
    print('\n\n')


    

if __name__ == "__main__":
    main()