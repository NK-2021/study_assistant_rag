# ui_form.py
import streamlit as st

def render_form_view():
    st.title("AI Study Assistant (RAG)")

    mode = st.selectbox("Mode", ["qa", "notes", "mcq"], index=0)
    question = st.text_input("Ask a question / topic")

    uploaded_file = st.file_uploader("Upload PDF (optional)", type=["pdf"])
    pasted_text = st.text_area("Or paste your notes (optional)", height=180)

    col1, col2 = st.columns(2)
    with col1:
        model = st.text_input("Ollama model", value="mistral:7b")
    with col2:
        top_k = st.number_input("Top-k chunks", min_value=1, max_value=12, value=5)

    ### Previous Code
    # submit = st.button("Run")
    # return {
    #     "mode": mode,
    #     "question": question,
    #     "uploaded_file": uploaded_file,
    #     "pasted_text": pasted_text,
    #     "model": model,
    #     "top_k": int(top_k),
    #     "submit": submit,
    # }

    ### New Code
    colA, colB = st.columns(2)
    with colA:
        index_submit = st.button("Index Notes")
    with colB:
        ask_submit = st.button("Ask")

    return {
        "mode": mode,
        "question": question,
        "uploaded_file": uploaded_file,
        "pasted_text": pasted_text,
        "model": model,
        "top_k": int(top_k),
        "index_submit": index_submit,
        "ask_submit": ask_submit,
    }


    
