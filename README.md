# IT Help Desk Assistant with LangChain and Pinecone

An intelligent IT Help Desk chatbot leveraging LangChain, Azure OpenAI, Pinecone vector database, and Tavily for comprehensive IT support assistance.

## Features

- Natural language understanding using Azure OpenAI and LangChain
- Efficient knowledge retrieval with Pinecone vector database
- Web search capabilities using Tavily API for enhanced responses
- Text-to-speech support with automatic language detection
- Conversational memory for context-aware assistance
- Interactive chat interface
- Logging and detailed conversation history

## Prerequisites

- Python 3.8+
- Azure OpenAI API access
- Pinecone API access
- Tavily API key

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment variables:

- Copy `.env.template` to `.env`
- Add your API keys and configurations:

  ```
  # Azure OpenAI
  AZURE_OPENAI_API_KEY=your_key
  AZURE_OPENAI_API_VERSION=your_version
  AZURE_OPENAI_ENDPOINT=your_endpoint
  AZURE_OPENAI_DEPLOYMENT=your_deployment
  AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment

  # Pinecone
  PINECONE_API_KEY=your_key
  PINECONE_ENVIRONMENT=your_environment
  PINECONE_INDEX_NAME=your_index_name

  # Tavily
  TAVILY_API_KEY=your_key
  ```

3. Run the application:

```bash
python src/main.py
```

The application will start on http://localhost:5000

## Project Structure

```
.
├── README.md
├── requirements.txt            # Project dependencies
├── .env                       # Environment variables
├── .env.template              # Template for environment variables
└── src/
    ├── main.py               # Flask application entry point
    ├── chatbot.py            # Core chatbot implementation with LangChain
    ├── tts_service.py        # Text-to-speech service
    ├── utils.py              # Utility functions
    ├── static/
    │   ├── script.js         # Frontend JavaScript
    │   ├── style.css         # Frontend styles
    │   └── audio/           # Generated audio files
    └── templates/
        └── index.html        # Main chat interface
```

## License

MIT License
