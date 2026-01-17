from __future__ import annotations
from typing import Optional

from extract import extract_text_from_uploaded_file, clean_text
from llm_runner import run_study_llm
from rag import retrieve_sources

DEFAULT_OLLAMA_MODEL = "mistral:7b"

def answer_question(
    uploaded_file,
    pasted_text: str,
    question: str,
    mode: str = "qa",
    top_k: int = 5,
    ui_log=None,
    model: str = DEFAULT_OLLAMA_MODEL,
) -> dict:

    """
    Orchestrates: extract -> clean -> retrieve -> LLM -> JSON.
    Returns: dict (parsed JSON).
    """

    def log(msg: str):
        print(msg, flush=True)
        if ui_log is not None:
            try:
                ui_log.write(msg)
            except Exception:
                pass

    log("STEP 1/3: Extracting + cleaning study text...")

    extracted = extract_text_from_uploaded_file(uploaded_file) if uploaded_file is not None else ""
    raw = pasted_text.strip() if (pasted_text and pasted_text.strip()) else extracted
    notes_text = clean_text(raw)

    log(f"Notes length: {len(notes_text)} chars. top_k={top_k}")

    if not notes_text:
        raise ValueError("No study text found. Upload a PDF or paste your notes.")

    if not question or not question.strip():
        raise ValueError("Question is empty.")

    log("STEP 2/3: Retrieving context (Chroma top-k)...")
    # context = retrieve_context(notes_text=notes_text, question=question)
    retr = retrieve_sources(notes_text=notes_text, question=question, top_k=top_k)
    context = retr["context"]
    sources = retr["sources"]


    if not context or not context.strip():
        return {
            "mode": mode,
            "answer": "Insufficient context.",
            "key_points": [],
            "evidence": [],
            "missing": "No relevant chunks were retrieved from the provided notes.",
        }

    log("STEP 3/3: Generating answer (Ollama)...")
    context = context[:8000]
    # result = run_study_llm(
    #     model=model,
    #     mode=mode,
    #     context=context,
    #     question=question,
    # )
    result = run_study_llm(mode=mode, question=question, context=context, model=model)

    # Attach sources for UI (top-k retrieved chunks)
    result["sources"] = sources

    return result

def index_only(uploaded_file, pasted_text: str, ui_log=None) -> dict:
    """
    Extract -> clean -> index into Chroma.
    Returns a small status dict for UI.
    """
    def log(msg: str):
        print(msg, flush=True)
        if ui_log is not None:
            try:
                ui_log.write(msg)
            except Exception:
                pass

    log("INDEX: Extracting + cleaning study text...")

    extracted = extract_text_from_uploaded_file(uploaded_file) if uploaded_file is not None else ""
    raw = pasted_text.strip() if (pasted_text and pasted_text.strip()) else extracted
    notes_text = clean_text(raw)

    if not notes_text:
        raise ValueError("No study text found. Upload a PDF or paste your notes.")

    # ✅ index explicitly
    from rag import index_notes
    notes_hash = index_notes(notes_text)

    return {
        "status": "indexed",
        "notes_hash": notes_hash,
        "notes_len": len(notes_text),
    }
