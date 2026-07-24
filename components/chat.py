import streamlit as st
from models.rag_engine import RAGEngine

# Load RAG Engine only once
@st.cache_resource
def load_rag():
    return RAGEngine()

rag = load_rag()


def show_chat():

    st.subheader("💬 Ask HeritageGPT")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg["role"] == "assistant" and "sources" in msg:
                if msg["sources"]:
                    st.markdown("### 📚 Sources")

                    for source in msg["sources"]:
                        st.info(
                            f"📍 {source['title']} | "
                            f"{source['district']} | "
                            f"{source['category']}"
                        )

    # Chat input
    question = st.chat_input(
        "Ask about temples, forts, museums..."
    )

    if question:

        # User message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        # AI response
        with st.chat_message("assistant"):

            with st.spinner("Searching Heritage Database..."):

                response = rag.answer_question(question)

            st.markdown(response["answer"])

            if response["sources"]:

                st.markdown("### 📚 Sources")

                for source in response["sources"]:

                    st.info(
                        f"📍 {source['title']} | "
                        f"{source['district']} | "
                        f"{source['category']}"
                    )

        # Save assistant response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response["answer"],
                "sources": response["sources"]
            }
        )