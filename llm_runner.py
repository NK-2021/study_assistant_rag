from __future__ import annotations
from typing import Callable, Dict

from ollama_client import ollama_chat, extract_json_first
from llm_prompts import (
    SYSTEM_PROMPT,
    QA_PROMPT,
    NOTES_PROMPT,
    MCQ_PROMPT,
)

def run_study_llm(
    model: str,
    mode: str,
    context: str,
    question: str,
) -> Dict:
    """
    Runs a single LLM call for Study Assistant.
    """
    temperature = 0.0  # deterministic, exam-safe
    context = context[:8000]  # keep prompt lighter (adjust later)

    if mode == "notes":
        user_prompt = NOTES_PROMPT.format(context=context, question=question)
    elif mode == "mcq":
        user_prompt = MCQ_PROMPT.format(context=context, question=question)
    else:
        user_prompt = QA_PROMPT.format(context=context, question=question)

    print("Ollama: starting generation...", flush=True)

    raw = ollama_chat(
        model,
        prompt=user_prompt,
        system=SYSTEM_PROMPT,
        temperature=temperature,
        timeout_s=120,
    )
    print("Ollama: generation finished.", flush=True)

    return extract_json_first(raw)



