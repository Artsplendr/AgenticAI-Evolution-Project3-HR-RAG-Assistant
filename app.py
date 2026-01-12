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
    st.title("HR RAG Assistant (FAISS)")
    st.caption("Ask HR policy questions and get grounded answers with sources (local-first demo).")

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
        show_context = st.checkbox("Show retrieved context", value=True)

        st.divider()
        st.text("Index")
        st.code(s.index_dir, language="text")
        st.text("Models")
        st.code(f"Embeddings: {s.embedding_model}\nChat: {chat_model}", language="text")

    # Main UI
    question = st.selectbox("Choose a question", HR_QUESTIONS, index=0)
    custom_q = st.text_input("…or ask your own question", value="")
    final_question = custom_q.strip() if custom_q.strip() else question

    col1, col2 = st.columns([1, 1])
    with col1:
        run = st.button("Get Answer", type="primary", use_container_width=True)
    with col2:
        st.write("")  # spacing

    if not run:
        st.info("Select a question and click **Get Answer**.")
        return

    # Build retriever + answerer
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