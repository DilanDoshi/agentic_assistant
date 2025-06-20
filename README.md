### Agent Assitant  
### Description

User will interact with this like GPT except the agent will be better equipped to help you with your every day work or academic tasks.

**Capabilities:**

- The agent will have general LLM capabilities, RAG capabilities with whatever you store, and be able to read your emails, create meetings on calendar
- Create a general GPT like frontend with saved chat history

### Design:

**Tech Stack:**

- Langgraph and langflow → deals with LLMs, agentic frameworks, msg history
- Typescript → frontend
- React → backend
- APIs:
    - Google Calendar
    - gmail
    - astraDB (Vector DB for RAG)
    - Zoom if needed to create meeting