from backend.llm.init_llm import claude
from backend.llm.tools import TOOLS
from backend.llm.prompts import test_react_agent_main_prompt
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver


agent = create_react_agent(
    model=claude,
    tools=TOOLS,
    prompt=test_react_agent_main_prompt,
    checkpointer=MemorySaver(),
)


