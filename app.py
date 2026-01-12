from __future__ import annotations

import os
import streamlit as st

from hr_rag_assistant.config import get_settings
from hr_rag_assistant.retrieval.retriever import HRRetriever
from hr_rag_assistant.generation.answerer import HRAnswerer
from hr_rag_assistant.generation.citations import format_sources_block

HR_QUESTIONS = [
    "How many days per week am I allowed to work remotely?",
    "Do I need manager approval for remote work?",
    "Can my remote work privileges be revoked? If so, why?",
    "How many days of annual leave do employees receive per year?",
    "How far in advance do I need to request annual leave?",
    "Do I need a medical certificate if I am sick for several days?",
    "Can I carry unused leave days into the next year?",
    "What health insurance benefits are provided to employees?",
    "Does the company contribute to a pension plan?",
    "Is there a budget for training or professional development?",
    "How long is the probation period for new employees?",
    "What training must be completed during onboarding?",
    "Is there a buddy assigned to new employees?",
    "What happens if an employee violates the code of conduct?",
    "Under what conditions can disciplinary action lead to termination?",
]


def main() -> None:
    st.set_page_config(page_title="HR RAG Assistant (FAISS)", layout="wide")
    # UI tweaks: reduce top margin by ~50% and bump body font sizes by ~20% (keep h1 unchanged)
    st.markdown(
        """
        <style>
        /* tighten top padding above the main container */
        .block-container { padding-top: 2rem; }
        /* enlarge general body text without affecting the main title */
        p, li, label, input, textarea, select, button, code, pre,
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li {
            font-size: 1.2rem;
        }
        /* caption under the title */
        div[data-testid="stCaptionContainer"] * {
            font-size: 1.2rem !important;
        }
        /* selectbox/combobox text */
        div[role="combobox"] * {
            font-size: 1.2rem !important;
        }
        /* selectbox container + dropdown options (questions list) */
        div[data-testid="stSelectbox"] * {
            font-size: 1.2rem !important;
        }
        div[data-baseweb="select"] * {
            font-size: 1.2rem !important;
        }
        div[role="listbox"] * {
            font-size: 1.2rem !important;
        }
        /* increase input field heights and line-height so descenders (y,g,p) are not clipped */
        div[data-testid="stSelectbox"] div[role="combobox"] {
            min-height: 4.2rem;                 /* taller control */
            display: flex;
            align-items: center;                 /* vertical centering */
            padding-top: 1.0rem;
            padding-bottom: 1.0rem;
            overflow: visible !important;        /* avoid clipping */
        }
        /* ensure the baseweb inner container also centers children */
        div[data-baseweb="select"] > div {
            display: flex !important;
            align-items: center !important;
        }
        /* center any immediate child containers inside the combobox */
        div[data-testid="stSelectbox"] div[role="combobox"] > div {
            display: flex;
            align-items: center;
        }
        /* increase line-height so descenders like 'y','g','p' are fully visible */
        div[data-testid="stSelectbox"] div[role="combobox"] * {
            line-height: 2.2rem !important;
        }
        /* ensure the hidden input doesn't force a smaller height */
        div[data-testid="stSelectbox"] div[role="combobox"] input {
            height: auto !important;
        }
        /* text input for custom question + its placeholder */
        .stTextInput input[type="text"],
        input[type="text"] {
            font-size: 1.2rem !important;
            height: 3.4rem;
            line-height: 2.0rem;
            padding-top: 0.7rem;
            padding-bottom: 0.7rem;
        }
        .stTextInput input::placeholder,
        input::placeholder {
            font-size: 1.2rem !important;
        }
        /* code blocks (e.g., Index/Models in the sidebar) */
        div[data-testid="stCodeBlock"] pre,
        div[data-testid="stCodeBlock"] code {
            font-size: 1.2rem !important;
            line-height: 1.4;
        }
        /* ensure sidebar contents also scale */
        section[data-testid="stSidebar"] * {
            font-size: 1.2rem;
        }
        h1 { font-size: 2.0rem !important; }
        /* make primary button half-width, left-aligned (no centering) */
        .block-container .stButton > button {
            width: 25% !important;  /* 50% smaller than before */
            display: inline-block !important;
            margin: 0 !important;
        }
        /* blue style for Refresh button wrapper */
        .refresh-wrap .stButton > button {
            background-color: #1e90ff !important;   /* ocean blue */
            border-color: #1e90ff !important;
            color: #ffffff !important;
        }
        .refresh-wrap .stButton > button:hover {
            background-color: #187bcd !important;
            border-color: #187bcd !important;
        }
        /* reduce width of grey input fields (select + text input) to 50% */
        div[data-testid="stSelectbox"],
        div[data-testid="stTextInput"] {
            width: 50% !important;
            margin: 0 !important;              /* keep left-aligned */
        }
        /* ensure inner controls fit the reduced container */
        div[data-testid="stSelectbox"] div[role="combobox"],
        .stTextInput input[type="text"] {
            width: 100% !important;
        }
        /* reduce width of info alert (bottom hint) to match inputs */
        div[data-testid="stAlert"] {
            width: 50% !important;
            margin: 0 !important;              /* keep left-aligned */
        }
        div[data-testid="stAlert"] > div {
            width: 100% !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("HR RAG Assistant (FAISS)")
    st.caption("Ask HR policy questions and get grounded answers with sources")

    # Load settings (.env)
    try:
        s = get_settings()
    except Exception as e:
        st.error(f"Config error: {e}")
        st.stop()

    chat_model = os.getenv("CHAT_MODEL", "gpt-4.1-mini")

    # Sidebar controls
    with st.sidebar:
        st.header("Controls")
        top_k = st.slider("Top-K retrieved chunks", min_value=1, max_value=12, value=5, step=1)
        max_context_chars = st.slider("Max context characters", min_value=1000, max_value=12000, value=6000, step=500)
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
        show_context = st.checkbox("Show retrieved context", value=False)

        st.divider()
        st.text("Index")
        st.code(s.index_dir, language="text")
        st.text("Models")
        st.code(f"Embeddings: {s.embedding_model}\nChat: {chat_model}", language="text")

    # Handle Refresh BEFORE creating widgets (safe state clear)
    if st.session_state.get("refresh_trigger"):
        st.session_state.pop("custom_q", None)
        st.session_state.pop("preset_q", None)
        st.session_state.pop("refresh_trigger", None)

    # Main UI
    # Disable the preset question select when the user provides a custom question
    custom_q_existing = st.session_state.get("custom_q", "")
    disable_preset = bool(custom_q_existing.strip())
    question = st.selectbox(
        "Choose a question",
        HR_QUESTIONS,
        index=0,
        key="preset_q",
        disabled=disable_preset,
    )
    custom_q = st.text_input("…or ask your own question", value="", key="custom_q")
    final_question = custom_q.strip() or question

    # Buttons stacked: Refresh below, same width as Get Answer
    run = st.button("Get Answer", type="primary", use_container_width=True)
    st.markdown('<div class="refresh-wrap">', unsafe_allow_html=True)
    refresh = st.button("Refresh", type="secondary", use_container_width=True, key="refresh_btn")
    st.markdown('</div>', unsafe_allow_html=True)

    if refresh:
        st.session_state["refresh_trigger"] = True
        st.rerun()

    if not run:
        st.info("Select a question and click **Get Answer**.")
        return

    # Build retriever + answerer
    # Echo the exact question used, to remove ambiguity between preset/custom
    st.markdown(f"_Question used_: **{final_question}**")
    try:
        retriever = HRRetriever(
            index_dir=s.index_dir,
            openai_api_key=s.openai_api_key,
            embedding_model=s.embedding_model,
        )
    except Exception as e:
        st.error(f"Could not load FAISS index. Did you run ingestion?\n\n{e}")
        st.stop()

    answerer = HRAnswerer(openai_api_key=s.openai_api_key, chat_model=chat_model)

    # Retrieve
    with st.spinner("Retrieving relevant HR policy context..."):
        retrieval = retriever.retrieve(final_question, top_k=top_k)

    # Optionally show retrieval details
    if show_context:
        st.subheader("Retrieved context")
        if not retrieval.results:
            st.warning("No chunks retrieved.")
        else:
            for i, hit in enumerate(retrieval.results, start=1):
                c = hit.chunk
                with st.expander(f"[{i}] {c.source} — chunk_{c.chunk_index:04d} — score={hit.score:.4f}", expanded=(i <= 2)):
                    st.write(c.text)

    # Generate answer
    with st.spinner("Generating grounded answer..."):
        ans = answerer.answer(
            question=final_question,
            hits=retrieval.results,
            max_context_chars=max_context_chars,
            temperature=temperature,
        )

    st.subheader("Answer")
    st.write(ans.answer)

    st.subheader("Sources")
    st.code(format_sources_block(retrieval.results), language="text")


if __name__ == "__main__":
    main()