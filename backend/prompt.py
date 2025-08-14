from __future__ import annotations

from typing import List, Dict

SYSTEM_PROMPT = (
    "You are an AI career coach specializing in the Indian education and job market. "
    "Provide personalized, practical, and empathetic guidance. Cite sources when using web results. "
    "Be specific with actionable steps, relevant courses, exams, and timelines."
)


def build_context_block(title: str, items: List[str], max_chars: int = 5000) -> str:
    if not items:
        return ""
    text = f"\n\n[{title}]\n" + "\n\n".join(items)
    return text[:max_chars]


def build_prompt(
    user_input: str,
    user_profile: Dict | None,
    retrieved_snippets: List[str],
    web_snippets: List[str],
    instructions: str | None = None,
) -> str:
    profile_text = ""
    if user_profile:
        kv = [f"{k}: {v}" for k, v in user_profile.items() if v is not None]
        profile_text = "\n".join(kv)

    blocks = [
        build_context_block("User Profile", [profile_text] if profile_text else []),
        build_context_block("Knowledge Base", retrieved_snippets),
        build_context_block("Web Results", web_snippets),
    ]

    instr = instructions or (
        "Use the context above only if relevant. If the answer may be outdated, verify via web results. "
        "Tailor recommendations to the user's background and goals."
    )

    composed = (
        f"{SYSTEM_PROMPT}\n\n"
        f"{instr}\n\n"
        f"User Message: {user_input}\n"
        + "".join(blocks)
    )
    print("---------------------------------------------------Prompt in prompt.py------------------------------------------",composed)
    return composed