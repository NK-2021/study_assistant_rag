# rag.py
from __future__ import annotations

from typing import List
import hashlib
from functools import lru_cache

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# LOCKED CHOICES (match your project)
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "study_notes"

# Keeps track of which notes_text is currently indexed in this Streamlit session
_INDEXED_HASH: str | None = None


@lru_cache(maxsize=1)
def get_embedder() -> SentenceTransformer:
    return SentenceTransformer(EMBED_MODEL_NAME)


def _chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    """
    Minimal chunker.
    If you already have a chunking function, replace ONLY this function body with your existing one.
    """
    text = text.strip()
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    n = len(text)

    while start < n:
        end = min(n, start + chunk_size)
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0:
            start = 0
        if end == n:
            break

    return [c for c in chunks if c.strip()]


def _get_collection():
    client = chromadb.PersistentClient(
        path=PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(name=COLLECTION_NAME)


def index_notes(notes_text: str) -> str:
    """
    Builds embeddings and persists to local Chroma.
    Returns notes_hash.
    """
    col = _get_collection()

    notes_hash = hashlib.sha256(notes_text.encode("utf-8")).hexdigest()[:12]
    chunks = _chunk_text(notes_text)

    if not chunks:
        return notes_hash

    # ✅ Remove previous chunks for this same notes_hash to avoid duplicates
    try:
        col.delete(where={"notes_hash": notes_hash})
    except Exception:
        pass

    ids = [f"{notes_hash}_{i}" for i in range(len(chunks))]
    embeddings = get_embedder().encode(chunks, normalize_embeddings=True).tolist()
    metadatas = [{"notes_hash": notes_hash, "chunk_id": i} for i in range(len(chunks))]

    print(f"Indexing {len(chunks)} chunks into Chroma (notes_hash={notes_hash})...", flush=True)

    col.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return notes_hash


def retrieve_context(notes_text: str, question: str, top_k: int = 5) -> str:
    """
    Indexes notes only once per unique notes_text (per Streamlit session),
    then retrieves top-k chunks.
    """
    global _INDEXED_HASH

    notes_hash = hashlib.sha256(notes_text.encode("utf-8")).hexdigest()[:12]

    # ✅ Only index when notes change
    if _INDEXED_HASH != notes_hash:
        print("Indexing notes into Chroma...", flush=True)
        _INDEXED_HASH = index_notes(notes_text)


    col = _get_collection()
    q_emb = get_embedder().encode([question], normalize_embeddings=True).tolist()

    res = col.query(
        query_embeddings=q_emb,
        n_results=top_k,
        include=["documents"],
    )

    docs = res.get("documents", [[]])[0]
    if not docs:
        return ""

    return "\n\n---\n\n".join(docs)

def retrieve_sources(notes_text: str, question: str, top_k: int = 5) -> dict:
    """
    Returns retrieved chunks + metadata for UI display.
    Keeps existing retrieval behavior, just returns richer data.
    """
    global _INDEXED_HASH

    notes_hash = hashlib.sha256(notes_text.encode("utf-8")).hexdigest()[:12]

    if _INDEXED_HASH != notes_hash:
        print("Indexing notes into Chroma...", flush=True)
        _INDEXED_HASH = index_notes(notes_text)

    col = _get_collection()
    q_emb = get_embedder().encode([question], normalize_embeddings=True).tolist()

    res = col.query(
        query_embeddings=q_emb,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]

    sources = []
    for i in range(len(docs)):
        sources.append({
            "rank": i + 1,
            "chunk": docs[i],
            "notes_hash": (metas[i] or {}).get("notes_hash"),
            "chunk_id": (metas[i] or {}).get("chunk_id"),
            "distance": dists[i] if i < len(dists) else None,
        })

    context = "\n\n---\n\n".join(docs) if docs else ""
    return {"context": context, "sources": sources}

