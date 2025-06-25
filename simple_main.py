from backend.llm.agent import agent

def main():
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "what are my unread emails? Max 10"}]}
    )
    
    messages = result.get('messages', [])
    
    # Get the final AI response (last message)
    final_response = None
    tool_calls = []
    
    for message in messages:
        if hasattr(message, 'content') and not hasattr(message, 'name'):
            final_response = message.content
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_calls.extend(message.tool_calls)
    
    print("🎯 FINAL AI RESPONSE:")
    print("=" * 50)
    print(final_response)
    
    print("\n🔧 TOOL CALLS MADE:")
    print("=" * 50)
    for tool_call in tool_calls:
        print(f"• {tool_call['name']}({tool_call['args']})")

if __name__ == "__main__":
    main() 