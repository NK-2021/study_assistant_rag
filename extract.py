from __future__ import annotations
from typing import Optional
from io import BytesIO

from pypdf import PdfReader
from docx import Document


def extract_text_from_uploaded_file(uploaded_file) -> str:
    """
    uploaded_file is Streamlit's UploadedFile.
    Supports .pdf and .docx.
    """
    if uploaded_file is None:
        return ""

    name = (uploaded_file.name or "").lower()

    # Streamlit UploadedFile provides .getvalue() -> bytes
    file_bytes = uploaded_file.getvalue()

    if name.endswith(".pdf"):
        return _extract_pdf_bytes(file_bytes)
    if name.endswith(".docx"):
        return _extract_docx_bytes(file_bytes)

    return ""


def _extract_pdf_bytes(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    parts = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        if txt.strip():
            parts.append(txt)
    return "\n".join(parts).strip()


def _extract_docx_bytes(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    parts = []
    for p in doc.paragraphs:
        t = (p.text or "").strip()
        if t:
            parts.append(t)
    return "\n".join(parts).strip()


def clean_text(text: Optional[str]) -> str:
    t = (text or "").replace("\r", "\n")
    # normalize whitespace a bit
    lines = [ln.strip() for ln in t.split("\n")]
    lines = [ln for ln in lines if ln]  # drop empty
    return "\n".join(lines).strip()
