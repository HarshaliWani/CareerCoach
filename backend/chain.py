from __future__ import annotations

from typing import Dict, List, Generator
import json

from openai import OpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

from config import get_settings
from memory import get_memory
from retrieval import retrieve_relevant
from prompt import build_prompt, SYSTEM_PROMPT

MAX_SNIPPETS = 3
MAX_SNIPPET_CHARS = 100


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
    retrieved_snippets = [
        d.page_content[:MAX_SNIPPET_CHARS] + ("..." if len(d.page_content) > MAX_SNIPPET_CHARS else "")
        + f"\n(Source: {d.metadata.get('dataset','kb')})"
        for d in retrieved_docs[:MAX_SNIPPETS]
    ]

    web_snippets = run_tavily_search(user_input, max_results=3)[:MAX_SNIPPETS]

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

    #print("---------------------Composed prompt sent for LLM:--------------------------",prompt_text)

    # Prefer OpenRouter, then GitHub Models, then xAI, then OpenAI
    client = OpenAI(api_key=settings.github_models_api_key, base_url=settings.github_models_base_url)
    

    # Prepend system message; include last few history lines briefly as context
    history_messages = []
    for role, content in context.get("history", [])[-10:]:
        if role == "human":
            history_messages.append({"role": "user", "content": content})
        elif role == "ai":
            history_messages.append({"role": "assistant", "content": content})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history_messages + [
        {"role": "user", "content": user_input}
    ]

    print("Sending to LLM with model:", settings.llm_model_name)
    print("Messages:", json.dumps(messages, indent=2))
    # -----------------

    with client.chat.completions.stream(model=settings.llm_model_name, messages=messages) as stream:
        full_text = ""
        for event in stream:
            # print("Model Stream event-------------------------", event)
            if event.type == "token":
                token = event.token
                print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------Model stream event(response):", repr(token))  # Debugging line
                full_text += token
                yield token
            elif event.type == "completed":
                print("Full model response:", full_text)
                # Update memory on completion
                memory, _ = get_memory(session_id)
                memory.chat_memory.add_user_message(user_input)
                memory.chat_memory.add_ai_message(full_text)
                break
            elif event.type == "error":
                err_msg = str(event.error)
                print("Model error:", err_msg) 
                yield f"\n[Error: {err_msg}]"
                break


def chat_once(session_id: str, user_input: str, user_profile: Dict | None = None) -> str:
    chunks = []
    for token in stream_chat(session_id=session_id, user_input=user_input, user_profile=user_profile):
        chunks.append(token)
    return "".join(chunks)


def build_prompt(user_input, user_profile, retrieved_snippets, web_snippets):
    # Only add context if user_input is a career-related question
    context = ""
    if "career" in user_input.lower() or "job" in user_input.lower() or "study" in user_input.lower():
        if user_profile:
            context += f"[User Profile]\n" + "\n".join(f"{k}: {v}" for k, v in user_profile.items()) + "\n"
        if retrieved_snippets:
            context += "[Knowledge Base]\n" + "\n".join(retrieved_snippets) + "\n"
        if web_snippets:
            context += "[Web Results]\n" + "\n".join(web_snippets) + "\n"
    return f"{context}User Message: {user_input}"