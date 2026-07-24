import streamlit as st
from models.rag_engine import RAGEngine

# -------------------------------------
# Page Configuration
# -------------------------------------

st.set_page_config(
    page_title="Chat | HeritageGPT",
    page_icon="💬",
    layout="wide"
)

# -------------------------------------
# Load CSS
# -------------------------------------

try:
    with open("styles/style.css") as css:
        st.markdown(
            f"<style>{css.read()}</style>",
            unsafe_allow_html=True
        )
except:
    pass

# -------------------------------------
# Load RAG Engine
# -------------------------------------

@st.cache_resource
def load_rag():

    return RAGEngine()

rag = load_rag()

# -------------------------------------
# Sidebar
# -------------------------------------

with st.sidebar:

    st.title("🏛 HeritageGPT")

    st.divider()

    if st.button("🗑 Clear Chat"):

        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.subheader("Example Questions")

    st.write("🛕 Tell me about Tirumala Temple")

    st.write("🏰 History of Gandikota")

    st.write("🏛 Museums in Andhra Pradesh")

    st.write("🌊 Beaches near Visakhapatnam")

    st.write("🎉 Festivals of Srisailam")

# -------------------------------------
# Header
# -------------------------------------

st.title("💬 Heritage Assistant")

st.caption(
    "Ask anything about Andhra Pradesh Heritage."
)

st.divider()

# -------------------------------------
# Session State
# -------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []

# -------------------------------------
# Display Chat History
# -------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

       

# -------------------------------------
# Chat Input
# -------------------------------------

question = st.chat_input(
    "Ask a heritage question..."
)

# -------------------------------------
# User Message
# -------------------------------------

if question:

    st.session_state.messages.append(
        {
            "role":"user",
            "content":question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

# -------------------------------------
# AI Response
# -------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching Heritage Database..."
        ):

            try:

                result = rag.answer_question(question)

                answer = result["answer"]

                sources = result["sources"]

            except Exception as e:

                answer = f"Error : {e}"

                sources = []

        st.markdown(answer)


# -------------------------------------
# Save Chat
# -------------------------------------

        st.session_state.messages.append(

            {
                "role":"assistant",

                "content":answer,

                "sources":sources

            }

        )

# -------------------------------------
# Footer
# -------------------------------------

st.divider()

st.caption(
    "🏛 HeritageGPT • Powered by Groq + ChromaDB + Sentence Transformers"
)