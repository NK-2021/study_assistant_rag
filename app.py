import streamlit as st
import traceback

from ui_form import render_form_view
from ui_results import render_results_view
from pipeline import answer_question, index_only

st.set_page_config(page_title="AI Study Assistant (RAG)", layout="centered")

# -------- Session State Defaults --------
if "indexed" not in st.session_state:
    st.session_state["indexed"] = False

if "index_info" not in st.session_state:
    st.session_state["index_info"] = None

if "view" not in st.session_state:
    st.session_state["view"] = "form"  # "form" | "result"

if "result" not in st.session_state:
    st.session_state["result"] = None

if "error" not in st.session_state:
    st.session_state["error"] = None

# If somehow an invalid view value gets set, recover gracefully
if st.session_state["view"] not in ("form", "result"):
    st.session_state["view"] = "form"

# -------- Router --------
if st.session_state["view"] == "form":
    data = render_form_view()

    # Show any last error on the form page
    if st.session_state.get("error"):
        st.error(st.session_state["error"])

    # -------- INDEX --------
    if data.get("index_submit"):
        try:
            # Clear stale UI state BEFORE indexing
            st.session_state["error"] = None
            st.session_state["result"] = None

            with st.spinner("Indexing notes… (PDF → chunks → embeddings → Chroma)"):
                idx = index_only(
                    uploaded_file=data["uploaded_file"],
                    pasted_text=data["pasted_text"],
                )

            st.session_state["indexed"] = True
            st.session_state["index_info"] = idx

            # Clear stale error/result AFTER successful indexing too (belt + suspenders)
            st.session_state["error"] = None
            st.session_state["result"] = None

            st.success(f"Indexed ✅  notes_hash={idx['notes_hash']}  length={idx['notes_len']}")

        except Exception:
            st.session_state["indexed"] = False
            st.session_state["index_info"] = None
            st.session_state["error"] = traceback.format_exc()

    # -------- ASK --------
    if data.get("ask_submit"):
        try:
            # Clear stale error BEFORE running ask
            st.session_state["error"] = None

            # Require indexing first
            if not st.session_state.get("indexed"):
                raise ValueError("Please click 'Index Notes' first.")

            with st.spinner("Answering… (retrieve top-k → Ollama)"):
                result = answer_question(
                    uploaded_file=data["uploaded_file"],
                    pasted_text=data["pasted_text"],
                    question=data["question"],
                    mode=data["mode"],
                    model=data["model"],
                    top_k=data["top_k"],
                )

            # Success path: store result and clear error
            st.session_state["result"] = result
            st.session_state["error"] = None

            st.session_state["view"] = "result"
            st.rerun()

        except Exception:
            # Prevent old answer from showing up later
            st.session_state["result"] = None
            st.session_state["error"] = traceback.format_exc()
            st.rerun()

else:
    render_results_view()
