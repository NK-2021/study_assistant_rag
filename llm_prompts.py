# llm_prompts.py
# Study Assistant prompts (RAG-grounded). Copy-paste safe.

SYSTEM_PROMPT = """You are an AI Study Assistant.

STRICT RULES (must follow):
- You are given retrieved study material as context in the user prompt.
- Use ONLY the provided context. No outside knowledge.
- If the context is insufficient, output exactly: "Insufficient context."
- Do not guess. Do not hallucinate.
- Output MUST be valid JSON exactly matching the schema requested.
- No markdown. No extra commentary.
"""

QA_PROMPT = """Context:
{context}

Question:
{question}

Return JSON in this exact schema:
{{
  "mode": "qa",
  "answer": "string",
  "key_points": ["string"],
  "evidence": ["string"],
  "missing": "string or null"
}}

Rules:
- Use ONLY the context above.
- "evidence" MUST contain 1–3 short direct quotes copied verbatim from the context that support the answer.
- If you cannot find supporting quotes in the context, treat it as insufficient context.

If context is insufficient:
  - "answer": "Insufficient context."
  - "key_points": []
  - "evidence": []
  - "missing": "one-line description of what is missing"
Otherwise:
  - "missing": null
"""

NOTES_PROMPT = """Context:
{context}

Topic / Question:
{question}

Create exam-focused revision notes using ONLY the context.

Return JSON in this exact schema:
{{
  "mode": "notes",
  "topic": "string",
  "revision_notes": ["string"],
  "definitions": [{{"term":"string","definition":"string"}}],
  "common_mistakes": ["string"],
  "evidence": ["string"],
  "missing": "string or null"
}}

Rules:
- Use ONLY the context above.
- "evidence" MUST contain 1–3 short direct quotes copied verbatim from the context that support the notes/definitions.
- If you cannot find supporting quotes in the context, treat it as insufficient context.

If context is insufficient:
  - "revision_notes": []
  - "definitions": []
  - "common_mistakes": []
  - "evidence": []
  - "missing": "Insufficient context."
Otherwise:
  - "missing": null
- Keep revision_notes short, bullet-like, exam-oriented.
"""

MCQ_PROMPT = """Context:
{context}

Topic / Question:
{question}

Generate 5 MCQs using ONLY the context.

Return JSON in this exact schema:
{{
  "mode": "mcq",
  "topic": "string",
  "mcqs": [
    {{
      "q": "string",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "A|B|C|D",
      "explanation": "string",
      "evidence": ["string"]
    }}
  ],
  "missing": "string or null"
}}

Rules:
- Use ONLY the context above.
- For EACH MCQ, "evidence" MUST include 1 short direct quote copied verbatim from the context that supports the correct answer/explanation.
- If you cannot support the MCQs with quotes from the context, treat it as insufficient context.

If context is insufficient:
  - "mcqs": []
  - "missing": "Insufficient context."
Otherwise:
  - "missing": null
- Explanations must be directly supported by context.
"""
