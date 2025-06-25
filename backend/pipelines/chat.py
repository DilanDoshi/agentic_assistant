import uuid


def chat_with_agent(agent, user_input: str, thread_id: str):
    if not thread_id:
        thread_id = create_chat_id()

    config = {
    "configurable": {
        "thread_id": thread_id
            }
        }
    
    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config
    )
    
    ai_response = response['messages'][-1].content
    
    return ai_response


def create_chat_id() -> str:
    return str(uuid.uuid4())


