from backend.llm.init_llm import claude
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model = claude,
    tools = [],
    prompt = "",
)
