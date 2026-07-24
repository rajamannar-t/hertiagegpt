import streamlit as st


def show_sidebar():

    with st.sidebar:

        st.title("🏛️ HeritageGPT")

        st.divider()

        st.subheader("Quick Explore")

        st.button("🛕 Temples")

        st.button("🏰 Forts")

        st.button("🏛️ Museums")

        st.button("🌊 Beaches")

        st.divider()

        st.subheader("Model")

        st.success("Llama 3.3")

        st.subheader("Embedding")

        st.info("MiniLM-L6-v2")