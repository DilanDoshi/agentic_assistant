# Agentic Assistant

## Description

An intelligent AI assistant that helps with everyday work and academic tasks. Users interact with it like GPT, but the agent is specifically equipped to handle email management, calendar operations, and other productivity tasks.

Note: This project is still in progress. This is project is being done wiht little to no AI for code generation. This is a project to help me learn fullstack development as well as langgraph, langchain, and other APIs.

**Capabilities:**

- General LLM capabilities with conversation memory
- Email management (read, analyze, and create drafts)
- Calendar integration (create meetings, manage events)
- RAG capabilities with vector database storage
- Interactive chat interface with saved conversation history

## Current Implementation Status

### ✅ Completed Features

#### **Core AI Agent System**
- **LangGraph Agent**: Implemented using LangGraph's React agent pattern
- **Claude 3.7 Sonnet Integration**: Full integration with Anthropic's Claude model
- **Conversation Memory**: Persistent conversation threads with unique IDs
- **Tool System**: Extensible tool framework for agent capabilities

#### **Email Management System**
- **Gmail API Integration**: Complete OAuth2 authentication and API access
- **Email Retrieval**: Fetch unread emails with full metadata parsing
- **Email Analysis**: AI-powered analysis to determine which emails need responses
- **Draft Creation**: Automated generation of professional email drafts
- **Draft Storage**: Automatic saving of drafts to Gmail drafts folder
- **Email Parsing**: Comprehensive parsing of email headers, content, and metadata

#### **Email Features**
- **Smart Filtering**: Automatically filters out spam, automated messages, and non-actionable emails
- **Professional Drafts**: AI-generated drafts that maintain consistent tone and style
- **Conversation History**: Maintains context across multiple draft generations
- **Multi-format Support**: Handles both plain text and HTML email content
- **Header Parsing**: Extracts sender info, recipients, dates, and all email metadata

#### **Technical Infrastructure**
- **Configuration Management**: Environment-based settings with Pydantic validation
- **Error Handling**: Comprehensive error handling for API failures and edge cases
- **Authentication**: Secure OAuth2 flow with token persistence
- **Code Documentation**: Extensive inline documentation and comments
- **Modular Architecture**: Clean separation of concerns across modules

### 🔄 In Progress

#### **Frontend Development**
- React/TypeScript frontend (planned)
- Chat interface with conversation history
- Email draft preview and editing
- Calendar integration UI

#### **Calendar Integration**
- Google Calendar API integration (planned)
- Meeting creation and management
- Event scheduling and reminders

#### **RAG System**
- AstraDB vector database integration (planned)
- Document storage and retrieval
- Semantic search capabilities

### 📋 Planned Features

#### **Enhanced Email Capabilities**
- Email signature detection and management
- User profile extraction from Gmail
- Attachment handling and processing
- Email categorization and labeling

#### **Calendar Features**
- Meeting scheduling with Zoom integration
- Calendar event management
- Availability checking and scheduling

#### **Advanced AI Features**
- Multi-modal capabilities (image, document processing)
- Personalized responses based on user history
- Advanced RAG with document understanding

## Design

### Tech Stack

**Backend:**
- **Python**: Core application logic
- **LangGraph**: Agentic framework for LLM orchestration
- **LangChain**: LLM integration and tool management
- **Pydantic**: Data validation and settings management

**APIs & Services:**
- **Gmail API**: Email management and draft creation
- **Google Calendar API**: Event and meeting management (planned)
- **Anthropic Claude**: Primary LLM for AI capabilities
- **AstraDB**: Vector database for RAG (planned)

**Frontend (Planned):**
- **TypeScript**: Type-safe frontend development
- **React**: User interface framework
- **Modern UI/UX**: Professional chat interface

### Architecture

```
agentic_assistant/
├── main.py                 # Application entry point
├── backend/
│   ├── llm/               # AI/LLM related modules
│   │   ├── agent.py       # LangGraph agent configuration
│   │   ├── init_llm.py    # Claude model initialization
│   │   ├── tools.py       # Agent tools (email, calendar)
│   │   └── prompts.py     # Prompt templates
│   ├── google/            # Google API integrations
│   │   ├── gmail_client.py # Gmail API client
│   │   └── emails.py      # Email data models
│   ├── pipelines/         # Data processing pipelines
│   │   └── chat.py        # Conversation management
│   └── config/            # Configuration management
│       └── settings.py    # Environment settings
└── README.md              # Project documentation
```

## Getting Started

### Prerequisites
- Python 3.11+
- Google Cloud Console account
- Anthropic API key

### Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up Google Cloud credentials:
   - Download `credentials.json` from Google Cloud Console
   - Place in project root
4. Create `.env` file with:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
5. Run the application: `python main.py`

### Usage
- Start interactive chat: The application will prompt for user input
- Ask about emails: "What are my unread emails?"
- Create drafts: "Create drafts for my unread emails"
- Exit: Type "exit", "quit", or "bye"

## Development Status

This project is actively under development. The core email management system is fully functional, with the AI agent capable of:
- Reading and analyzing emails
- Determining which emails need responses
- Creating professional email drafts
- Saving drafts to Gmail

The next phases will focus on frontend development, calendar integration, and RAG capabilities.

## Contributing

This is a personal project currently in active development. The codebase is well-documented and modular, making it suitable for future contributions and extensions.