# AI Memory Journal

A simple learning project that demonstrates a chat application with long-term memory capabilities.

## What it does

This is a chat application where an AI assistant can remember past conversations. It uses:
- **FastAPI** for the backend API
- **Streamlit** for the web interface
- **ChromaDB** for storing and retrieving memories using vector embeddings
- **Ollama** for the LLM (using llama3.1 model)
- **SQLite** for storing conversation history

When you chat with the assistant, it can recall relevant past conversations to provide more contextual responses.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the backend:
   ```bash
   uvicorn backend.main:app --reload
   ```

3. Start the frontend (in a new terminal):
   ```bash
   streamlit run Frontend/app.py
   ```

## Project Structure

```
backend/          # FastAPI backend
  ├── db/         # Database operations (SQLite & ChromaDB)
  └── services/   # AI and memory services
Frontend/         # Streamlit frontend
data/             # Database files
```
