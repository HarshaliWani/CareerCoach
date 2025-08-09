from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, Dict


class ChatRequest(BaseModel):
    session_id: str = Field(...)
    message: str = Field(...)
    user_profile: Optional[Dict] = None


class ChatResponse(BaseModel):
    session_id: str
    message: str


class UpsertUserRequest(BaseModel):
    session_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    traits: Optional[Dict] = None


class UserResponse(BaseModel):
    session_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    traits: Optional[Dict] = None