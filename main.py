from backend.llm.agent import agent
from backend.google.gmail_client import authenticate_gmail

def main():
    """
    messages = {
        "messages": [
            {
                "role": "user",
                "content": "what is ferrari?",
            }
        ]
    }
    print(agent.invoke(messages))
    """
    gmail_client = authenticate_gmail()


if __name__ == "__main__":
    main()