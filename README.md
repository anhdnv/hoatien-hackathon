# IT Technical Support

An intelligent IT Help Desk chatbot leveraging LangChain, Azure OpenAI, and ChromaDB for comprehensive IT support assistance.

## Features

- Natural language understanding using Azure OpenAI and LangChain
- Efficient knowledge retrieval with a local ChromaDB vector database
- Conversational memory for context-aware assistance
- Interactive chat interface with language selection (English/Vietnamese)
- Logging and detailed conversation history

## Prerequisites

- Python 3.8+
- Azure OpenAI API access

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment variables:

- Create a `.env` file in the root directory (or copy from `.env.template`).
- Add your API keys and configurations:

  ```
  # Azure OpenAI
  AZURE_OPENAI_API_KEY=your_key
  AZURE_OPENAI_API_VERSION=your_version
  AZURE_OPENAI_ENDPOINT=your_endpoint
  AZURE_OPENAI_DEPLOYMENT=your_deployment
  AZURE_OPENAI_EMBEDDING_KEY=your_embedding_key
  AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment
  ```

3. Run the application:

```bash
python src/main.py
```

The application will start on http://localhost:5000

## Updating Knowledge Base

When you modify `src/docs/Project_Documents.md`, update ChromaDB:

```bash
cd src
python tools/refresh_chromadb.py
```

The script will:

- Delete old ChromaDB collection
- Read updated Project_Documents.md
- Generate new embeddings with Azure OpenAI
- Save to local ChromaDB

**Time required:** < 1 minute

## Project Structure

```
.
├── README.md
├── requirements.txt            # Project dependencies
├── .env                       # Environment variables
├── .env.template              # Environment template
└── src/
    ├── main.py               # Flask application entry point
    ├── chatbot.py            # Core chatbot implementation with LangChain and ChromaDB
    ├── utils.py              # Utility functions
    ├── local_chromadb/       # Local ChromaDB storage
    ├── docs/
    │   └── Project_Documents.md # Knowledge base file
    ├── tools/
    │   └── refresh_chromadb.py  # Script to update ChromaDB
    ├── test/
    │   ├── test_chatbot_contact.py
    │   └── test_chromadb_insert.py
    ├── static/
    │   ├── script.js         # Frontend JavaScript
    │   ├── style.css         # Frontend styles
    │   └── audio/            # Directory for audio files
    ├── templates/
    │   └── index.html        # Main chat interface
    └── src/
        └── static/           # Additional static assets
```

## License

MIT License
