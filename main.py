from backend.llm.agent import agent
from backend.pipelines.chat import chat_with_agent, create_chat_id
from backend.llm.tools import create_drafts_for_unread_emails
from backend.google.gmail_client import GmailClient

def test1():
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "what are my unread emails? Max 10"}]}
    )
    
    # Extract messages from the result
    messages = result.get('messages', [])
    
    print("🤖 AI RESPONSES:")
    print("=" * 50)
    
    for i, message in enumerate(messages):
        if hasattr(message, 'content'):
            if hasattr(message, 'tool_calls') and message.tool_calls:
                print(f"\n📋 AI Response {i+1} (with tool calls):")
                print(f"Content: {message.content}")
                print(f"Tool Calls: {message.tool_calls}")
            else:
                print(f"\n💬 AI Response {i+1}:")
                print(f"Content: {message.content}")
    
    print("\n🔧 TOOL CALLS SUMMARY:")
    print("=" * 50)
    
    for i, message in enumerate(messages):
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                print(f"Tool: {tool_call['name']}")
                print(f"Arguments: {tool_call['args']}")
                print(f"ID: {tool_call['id']}")
                print("-" * 30)
    
    print("\n📧 TOOL RESULTS:")
    print("=" * 50)
    
    for i, message in enumerate(messages):
        if hasattr(message, 'name') and message.name:  # ToolMessage
            print(f"Tool: {message.name}")
            print(f"Result: {message.content}")
            print("-" * 30)

def run_chat():
    thread_id = create_chat_id()
    while True:
        user_input = input("\n\nYou: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break

        ai_response = chat_with_agent(agent, user_input, thread_id)
        print(f"\n\nClaude: {ai_response}")

def main():
    run_chat()
    #print(create_drafts_for_unread_emails(['197a47fc64229a54']))
    print('\n\n')


    

if __name__ == "__main__":
    main()