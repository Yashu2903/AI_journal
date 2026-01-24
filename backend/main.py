from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid
from datetime import datetime
from .db.chroma import collection
from .services.memory import write_memory, recall_memories
from .services.ai import generate_reply, build_prompt
from .schemas import (
    CreateSessionRequest, CreateSessionResponse, 
    AddMessageRequest, MessageOut, HistoryResponse,
    SessionsListResponse, UpdateSessionNameRequest
)
from .db.sqlite import (
    init_db, create_session as db_create_session, 
    add_message as db_add_message, get_history as db_get_history,
    get_all_sessions, update_session_name, get_session_name
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown
    pass

app = FastAPI(title="AI Memory Journal", description="A simple API for a memory journal", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/sessions", response_model=SessionsListResponse)
async def list_sessions() -> SessionsListResponse:
    """Get all sessions with their names and metadata."""
    sessions = get_all_sessions()
    return SessionsListResponse(sessions=sessions)

@app.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest = CreateSessionRequest()) -> CreateSessionResponse:
    """Create a new session with optional name."""
    session_id = str(uuid.uuid4())
    db_create_session(session_id, request.session_name)
    session_name = request.session_name or get_session_name(session_id)
    return CreateSessionResponse(session_id=session_id, session_name=session_name)

@app.patch("/sessions/{session_id}", response_model=dict)
async def rename_session(session_id: str, request: UpdateSessionNameRequest) -> dict:
    """Rename a session."""
    success = update_session_name(session_id, request.session_name)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "session_name": request.session_name}

@app.get("/sessions/{session_id}/history", response_model=HistoryResponse)
async def get_history(session_id: str) -> HistoryResponse:
    history = db_get_history(session_id)
    return HistoryResponse(session_id=session_id, messages=history)

@app.post("/chat")
async def chat(request: AddMessageRequest):

    db_create_session(request.session_id)

    message_id = db_add_message(request.session_id, "user", request.content)
    write_memory(message_id=message_id, session_id=request.session_id, role="user", content=request.content)

    history = db_get_history(request.session_id)
    
    # Auto-rename session based on first message if it's the first user message
    if len(history) == 1:  # Only the message we just added
        session_name = get_session_name(request.session_id)
        if session_name and (session_name.startswith("Chat -") or session_name == "New Conversation"):
            # This is the first user message, auto-rename to first 30 chars
            auto_name = request.content[:30].strip()
            if len(request.content) > 30:
                auto_name += "..."
            if auto_name:
                update_session_name(request.session_id, auto_name)

    # 🔽 retrieve long-term memory
    memories = recall_memories(query=request.content, session_id=request.session_id, k=5)

    prompt_messages = build_prompt(history=[{"role": m["role"], "content": m["content"]} for m in history], memories=memories)
    llm_reply = generate_reply(prompt_messages)

    msg_id =db_add_message(request.session_id, "assistant", llm_reply)
    write_memory(message_id=msg_id, session_id=request.session_id, role="assistant", content=llm_reply)

    return {"reply": llm_reply}

@app.get("/debug/memory_count")
def memory_count():
    return {"count": collection.count()}

@app.get("/debug/recall")
def debug_recall(q: str, session_id: str):
    memories = recall_memories(q, session_id)
    return {"memories": memories}




