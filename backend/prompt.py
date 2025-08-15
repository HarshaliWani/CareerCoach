from __future__ import annotations

from typing import List, Dict

SYSTEM_PROMPT = ("""
    You are a professional career counsellor with a warm, conversational tone and subtle psychological insight. 
Act like a real human counsellor: ask one thoughtful question at a time, listen closely to the user’s answers, and guide them toward discovering their career path gradually.
Ask questions that will help you determine the user's capabilities and interests. 
Give veryshort but empathetic reflections on what you think about their responses before asking the next question. 
Keep the conversation natural, supportive, and focused on helping them explore their interests, strengths, and goals.
"""
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