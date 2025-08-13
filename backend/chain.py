from __future__ import annotations

from typing import Dict, List, Generator
import json

from openai import OpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

from config import get_settings
from memory import get_memory
from retrieval import retrieve_relevant
from prompt import build_prompt, SYSTEM_PROMPT


def run_tavily_search(query: str, max_results: int = 3) -> List[str]:
    settings = get_settings()
    tool = TavilySearchResults(max_results=max_results, api_key=settings.tavily_api_key)
    try:
        results = tool.invoke({"query": query})
        snippets: List[str] = []
        for item in results:
            url = item.get("url")
            content = item.get("content")
            snippets.append(f"- {content}\nSource: {url}")
        return snippets
    except Exception:
        return []


def gather_context(session_id: str, user_input: str) -> Dict:
    memory, _ = get_memory(session_id)

    retrieved_docs = retrieve_relevant(user_input, k=5)
    retrieved_snippets = [f"{d.page_content}\n(Source: {d.metadata.get('dataset','kb')})" for d in retrieved_docs]

    web_snippets = run_tavily_search(user_input, max_results=3)

    history_messages = memory.chat_memory.messages
    history_tuples = [[m.type, getattr(m, 'content', '')] for m in history_messages]

    return {
        "history": history_tuples,
        "retrieved_snippets": retrieved_snippets,
        "web_snippets": web_snippets,
    }


def stream_chat(session_id: str, user_input: str, user_profile: Dict | None = None) -> Generator[str, None, None]:
    settings = get_settings()

    context = gather_context(session_id, user_input)
    retrieved_snippets = context.get("retrieved_snippets", [])
    web_snippets = context.get("web_snippets", [])

    # Build composed prompt
    prompt_text = build_prompt(
        user_input=user_input,
        user_profile=user_profile or {},
        retrieved_snippets=retrieved_snippets,
        web_snippets=web_snippets,
    )

    # Prefer OpenRouter (Grok-3), then xAI, then OpenAI
    client: OpenAI
    if settings.openrouter_api_key:
        client = OpenAI(api_key=settings.openrouter_api_key, base_url=settings.openrouter_base_url)
    elif settings.xai_api_key:
        client = OpenAI(api_key=settings.xai_api_key, base_url=settings.xai_base_url)
    else:
        client = OpenAI(api_key=settings.openai_api_key)

    # Prepend system message; include last few history lines briefly as context
    history_messages = []
    for role, content in context.get("history", [])[-10:]:
        if role == "human":
            history_messages.append({"role": "user", "content": content})
        elif role == "ai":
            history_messages.append({"role": "assistant", "content": content})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history_messages + [
        {"role": "user", "content": prompt_text}
    ]

    with client.chat.completions.stream(model=settings.llm_model_name, messages=messages) as stream:
        full_text = ""
        for event in stream:
            if event.type == "token":
                token = event.token
                full_text += token
                yield token
            elif event.type == "completed":
                # Update memory on completion
                memory, _ = get_memory(session_id)
                memory.chat_memory.add_user_message(user_input)
                memory.chat_memory.add_ai_message(full_text)
                break
            elif event.type == "error":
                err_msg = str(event.error)
                yield f"\n[Error: {err_msg}]"
                break


def chat_once(session_id: str, user_input: str, user_profile: Dict | None = None) -> str:
    chunks = []
    for token in stream_chat(session_id=session_id, user_input=user_input, user_profile=user_profile):
        chunks.append(token)
    return "".join(chunks)