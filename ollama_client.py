from __future__ import annotations
import subprocess
import json

def ollama_chat(
    model: str,
    messages: list[dict] | None = None,
    *,
    system: str | None = None,
    prompt: str | None = None,
    temperature: float = 0.0,
    timeout_s: int = 180,
) -> str:
    """
    Runs a local Ollama model and returns raw text output.
    Accepts either:
      - messages=[{role, content}, ...]  (old style)
      - system=..., prompt=...           (new style)
    """
    if messages is not None:
        stitched = _stitch_messages(messages)
    else:
        sys_txt = (system or "").strip()
        user_txt = (prompt or "").strip()
        stitched = ""
        if sys_txt:
            stitched += f"SYSTEM:\n{sys_txt}\n\n"
        stitched += f"USER:\n{user_txt}\n"

    cmd = ["ollama", "run", model]

    try:
        result = subprocess.run(
            cmd,
            input=stitched.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Ollama timed out after {timeout_s}s. Model={model}")

    if result.returncode != 0:
        raise RuntimeError(
            f"Ollama failed: {result.stderr.decode('utf-8', errors='ignore')}"
        )

    return result.stdout.decode("utf-8", errors="ignore").strip()


def extract_json_first(s: str) -> dict:
    """
    Extract the first JSON object from a string.
    Handles cases where the model prints extra text before/after JSON.
    """
    s = (s or "").strip()
    if not s:
        raise ValueError("Empty LLM output; expected JSON.")

    # Fast path: already valid JSON
    try:
        return json.loads(s)
    except Exception:
        pass

    # Find first JSON object by scanning braces
    start = s.find("{")
    if start == -1:
        raise ValueError(f"No '{{' found in LLM output. Output starts with:\n{s[:300]}\n\nOutput ends with:\n{s[-300:]}")

    depth = 0
    end = None
    for i in range(start, len(s)):
        ch = s[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    if end is None:
        raise ValueError(f"Unclosed JSON object in LLM output. Output starts with:\n{s[:300]}\n\nOutput ends with:\n{s[-300:]}")

    candidate = s[start:end].strip()

    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse JSON from LLM output. "
            f"Candidate starts with:\n{candidate[:300]}\n\nFull Output starts with:\n{s[:300]}\n\nOutput ends with:\n{s[-300:]}"
        ) from e


def _stitch_messages(messages: list[dict]) -> str:
    parts = []
    for m in messages:
        role = m.get("role", "user").upper()
        content = m.get("content", "")
        parts.append(f"{role}:\n{content}\n")
    return "\n".join(parts).strip()
