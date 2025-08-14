from __future__ import annotations

import json
from typing import Dict

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session

from config import get_settings
from db import Base, engine, SessionLocal
from models import User
from schemas import ChatRequest, ChatResponse, UpsertUserRequest, UserResponse
from chain import stream_chat, chat_once

settings = get_settings()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Career Coach", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # Ensure user exists
    user = db.query(User).filter_by(session_id=request.session_id).first()
    traits = {}
    if user and user.traits_json:
        try:
            traits = json.loads(user.traits_json)
        except Exception:
            traits = {}
    text = chat_once(session_id=request.session_id, user_input=request.message, user_profile=traits)
    return ChatResponse(session_id=request.session_id, message=text)


@app.get("/api/chat/stream")
async def chat_stream(session_id: str, message: str, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(session_id=session_id).first()
    traits: Dict = {}
    if user and user.traits_json:
        try:
            traits = json.loads(user.traits_json)
        except Exception:
            traits = {}

    async def event_generator():
        for token in stream_chat(session_id=session_id, user_input=message, user_profile=traits):
            if await request.is_disconnected():
                break
            yield {"event": "message", "data": token}
        # Signal end-of-stream
        yield {"event": "end", "data": "END"}

    return EventSourceResponse(event_generator())


@app.post("/api/user", response_model=UserResponse)
def upsert_user(req: UpsertUserRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(session_id=req.session_id).first()
    if not user:
        user = User(session_id=req.session_id)
        db.add(user)
    user.name = req.name or user.name
    user.email = req.email or user.email
    if req.traits is not None:
        try:
            user.traits_json = json.dumps(req.traits)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid traits JSON")
    db.commit()
    return UserResponse(
        session_id=user.session_id,
        name=user.name,
        email=user.email,
        traits=json.loads(user.traits_json) if user.traits_json else None,
    )


@app.get("/api/user/{session_id}", response_model=UserResponse)
def get_user(session_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(session_id=session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        session_id=user.session_id,
        name=user.name,
        email=user.email,
        traits=json.loads(user.traits_json) if user.traits_json else None,
    )


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Career Coach backend running"}