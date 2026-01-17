# ui_results.py
import streamlit as st
import json
from datetime import datetime

def _build_export_text(result: dict) -> str:
    mode = result.get("mode", "")
    lines = []
    lines.append("AI Study Assistant (RAG) — Export")
    lines.append(f"Mode: {mode}")
    lines.append("")

    missing = result.get("missing")
    if missing:
        lines.append(f"Missing: {missing}")
        lines.append("")

    # QA
    if mode == "qa":
        lines.append("Answer:")
        lines.append(result.get("answer", ""))
        lines.append("")

        kps = result.get("key_points", [])
        if kps:
            lines.append("Key Points:")
            for kp in kps:
                lines.append(f"- {kp}")
            lines.append("")

        ev = result.get("evidence", [])
        if ev:
            lines.append("Evidence (quotes from notes):")
            for e in ev:
                lines.append(f"- {e}")
            lines.append("")

    # NOTES
    elif mode == "notes":
        topic = result.get("topic")
        if topic:
            lines.append(f"Topic: {topic}")
            lines.append("")

        rn = result.get("revision_notes", [])
        if rn:
            lines.append("Revision Notes:")
            for r in rn:
                lines.append(f"- {r}")
            lines.append("")

        defs = result.get("definitions", [])
        if defs:
            lines.append("Definitions:")
            for d in defs:
                term = d.get("term", "")
                definition = d.get("definition", "")
                lines.append(f"- {term}: {definition}")
            lines.append("")

        cm = result.get("common_mistakes", [])
        if cm:
            lines.append("Common Mistakes:")
            for m in cm:
                lines.append(f"- {m}")
            lines.append("")

        ev = result.get("evidence", [])
        if ev:
            lines.append("Evidence (quotes from notes):")
            for e in ev:
                lines.append(f"- {e}")
            lines.append("")

    # MCQ
    elif mode == "mcq":
        topic = result.get("topic")
        if topic:
            lines.append(f"Topic: {topic}")
            lines.append("")

        mcqs = result.get("mcqs", [])
        if mcqs:
            lines.append("MCQs:")
            for i, q in enumerate(mcqs, start=1):
                lines.append(f"Q{i}. {q.get('q','')}")
                for opt in q.get("options", []):
                    lines.append(f"  {opt}")
                lines.append(f"Answer: {q.get('answer','')}")
                exp = q.get("explanation")
                if exp:
                    lines.append(f"Explanation: {exp}")
                ev = q.get("evidence", [])
                if ev:
                    lines.append("Evidence:")
                    for e in ev:
                        lines.append(f"- {e}")
                lines.append("")
        else:
            lines.append("No MCQs generated.")
            lines.append("")

    else:
        lines.append("Unknown mode.")
        lines.append("")

    # Sources
    sources = result.get("sources", [])
    if sources:
        lines.append("Sources (Top-k retrieved chunks):")
        for s in sources:
            rank = s.get("rank")
            chunk_id = s.get("chunk_id")
            dist = s.get("distance")
            header = f"#{rank}"
            if chunk_id is not None:
                header += f" chunk_id={chunk_id}"
            if dist is not None:
                header += f" distance={dist}"
            lines.append(header)
            chunk = (s.get("chunk") or "").strip()
            lines.append(chunk)
            lines.append("-" * 40)
        lines.append("")

    return "\n".join(lines)


def render_results_view():
    st.title("AI Study Assistant (RAG) — Result")

    result = st.session_state.get("result")
    error = st.session_state.get("error")

    if error:
        st.error(error)

    if result is None:
        st.info("No result yet. Go back and run a question.")
        if st.button("← Back"):
            st.session_state["view"] = "form"
            st.rerun()
        return

    # -------- Export buttons --------
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_bytes = json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")
    txt_bytes = _build_export_text(result).encode("utf-8")

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="Download JSON",
            data=json_bytes,
            file_name=f"study_assistant_result_{ts}.json",
            mime="application/json",
        )
    with c2:
        st.download_button(
            label="Download TXT",
            data=txt_bytes,
            file_name=f"study_assistant_result_{ts}.txt",
            mime="text/plain",
        )

    # Pretty JSON viewer
    st.subheader("Output (JSON)")
    st.json(result)

    # Quick View
    st.subheader("Quick View")
    mode = result.get("mode", "")

    if result.get("answer") == "Insufficient context." or result.get("missing") == "Insufficient context.":
        st.warning("Insufficient context found in the provided notes.")

    if result.get("missing") and result.get("missing") != "Insufficient context.":
        st.caption(f"Missing info: {result['missing']}")

    if mode == "qa":
        st.write(result.get("answer", ""))

        if result.get("evidence"):
            st.caption("Evidence from notes:")
            for e in result["evidence"]:
                st.write(f"• {e}")

        if result.get("key_points"):
            st.write("Key points:")
            for kp in result["key_points"]:
                st.write(f"- {kp}")

    elif mode == "notes":
        topic = result.get("topic")
        if topic:
            st.write(f"**Topic:** {topic}")

        if result.get("revision_notes"):
            st.write("**Revision notes:**")
            for line in result.get("revision_notes", []):
                st.write(f"- {line}")

        if result.get("definitions"):
            st.write("**Definitions:**")
            for d in result.get("definitions", []):
                term = d.get("term", "")
                definition = d.get("definition", "")
                if term or definition:
                    st.write(f"- **{term}**: {definition}")

        if result.get("common_mistakes"):
            st.write("**Common mistakes:**")
            for m in result.get("common_mistakes", []):
                st.write(f"- {m}")

        if result.get("evidence"):
            st.caption("Evidence from notes:")
            for e in result["evidence"]:
                st.write(f"• {e}")

    elif mode == "mcq":
        topic = result.get("topic")
        if topic:
            st.write(f"**Topic:** {topic}")

        mcqs = result.get("mcqs", [])
        if not mcqs:
            st.info("No MCQs generated.")
        else:
            for i, q in enumerate(mcqs, start=1):
                st.write(f"**Q{i}. {q.get('q','')}**")
                for opt in q.get("options", []):
                    st.write(opt)

                st.write(f"**Answer:** {q.get('answer','')}")
                if q.get("explanation"):
                    st.write(q.get("explanation", ""))

                if q.get("evidence"):
                    st.caption("Evidence:")
                    for e in q["evidence"]:
                        st.write(f"• {e}")

                st.divider()

    else:
        st.info("Unknown mode. Showing raw JSON above.")

    # -------- Sources (Top-k Retrieved Chunks) --------
    sources = result.get("sources", [])
    if sources:
        st.subheader("Sources (Top-k retrieved chunks)")
        for s in sources:
            rank = s.get("rank")
            chunk_id = s.get("chunk_id")
            dist = s.get("distance")
            chunk_text = (s.get("chunk") or "").strip()

            header = f"#{rank}"
            if chunk_id is not None:
                header += f" • chunk_id={chunk_id}"
            if dist is not None:
                header += f" • distance={dist:.4f}" if isinstance(dist, (int, float)) else f" • distance={dist}"

            with st.expander(header, expanded=(rank == 1)):
                st.write(chunk_text)
    else:
        st.caption("No sources available.")

    # Back button at the end
    if st.button("← Back"):
        st.session_state["view"] = "form"
        st.rerun()
