from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid
from datetime import datetime

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

@app.post("/messages", response_model=MessageOut)
async def add_message(request: AddMessageRequest) -> MessageOut:
    db_create_session(request.session_id)
    message_id = db_add_message(request.session_id, request.role, request.content)
    return MessageOut(id=message_id, session_id=request.session_id, role=request.role, content=request.content, created_at=datetime.now())

@app.get("/sessions/{session_id}/history", response_model=HistoryResponse)
async def get_history(session_id: str) -> HistoryResponse:
    history = db_get_history(session_id)
    return HistoryResponse(session_id=session_id, messages=history)



