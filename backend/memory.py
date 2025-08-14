from __future__ import annotations

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_core.chat_history import BaseChatMessageHistory
from typing import Tuple

from config import get_settings


def get_message_history(session_id: str) -> BaseChatMessageHistory:
    settings = get_settings()
    return SQLChatMessageHistory(session_id=session_id, connection=settings.database_url)


def get_memory(session_id: str) -> Tuple[ConversationBufferMemory, BaseChatMessageHistory]:
    history = get_message_history(session_id)
    memory = ConversationBufferMemory(memory_key="history", chat_memory=history, return_messages=True)
    return memory, history