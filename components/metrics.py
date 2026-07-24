import streamlit as st


def show_metrics():

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Heritage Places",
            "150+"
        )

    with col2:
        st.metric(
            "Knowledge Chunks",
            "1800+"
        )

    with col3:
        st.metric(
            "LLM",
            "Llama 3.3"
        )