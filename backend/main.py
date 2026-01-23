from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid
from datetime import datetime
from .db.chroma import collection
from .services.memory_writer import write_memory
from .services.memory_reader import recall_memories
from .services.prompt_builder import build_prompt

from .services.llm import generate_reply
from .schemas import CreateSessionResponse, AddMessageRequest, MessageOut, HistoryResponse
from .db.sqlite import init_db, create_session as db_create_session, add_message as db_add_message, get_history as db_get_history

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

@app.post("/sessions", response_model=CreateSessionResponse)
async def create_session() -> CreateSessionResponse:
    session_id = str(uuid.uuid4())
    db_create_session(session_id)
    return CreateSessionResponse(session_id=session_id)

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




