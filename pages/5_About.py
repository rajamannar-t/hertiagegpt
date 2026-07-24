import streamlit as st

# ------------------------------------
# Page Configuration
# ------------------------------------

st.set_page_config(
    page_title="About | HeritageGPT",
    page_icon="ℹ️",
    layout="wide"
)

# ------------------------------------
# Load CSS
# ------------------------------------

try:
    with open("styles/style.css") as css:
        st.markdown(
            f"<style>{css.read()}</style>",
            unsafe_allow_html=True
        )
except:
    pass

# ------------------------------------
# Header
# ------------------------------------

st.title("ℹ️ About HeritageGPT")

st.caption("AI-Powered Heritage Information System")

st.divider()

# ------------------------------------
# Introduction
# ------------------------------------

st.header("🏛 Project Overview")

st.write("""
HeritageGPT is an AI-powered Retrieval-Augmented Generation (RAG)
application that helps users explore the rich cultural heritage of
Andhra Pradesh.

Instead of relying only on a Large Language Model, HeritageGPT
retrieves relevant information from a curated heritage database and
generates accurate, context-aware responses.
""")

st.divider()

# ------------------------------------
# Features
# ------------------------------------

st.header("✨ Features")

col1, col2 = st.columns(2)

with col1:

    st.success("✔ AI Chat Assistant")

    st.success("✔ Semantic Search")

    st.success("✔ Vector Database")

    st.success("✔ Heritage Explorer")

    st.success("✔ Source-based Answers")

with col2:

    st.success("✔ ChromaDB")

    st.success("✔ Sentence Transformers")

    st.success("✔ Groq Llama 3.3")

    st.success("✔ Streamlit UI")

    st.success("✔ Knowledge Dashboard")

st.divider()

# ------------------------------------
# Architecture
# ------------------------------------

st.header("🏗 System Architecture")

st.code("""
User Question
      │
      ▼
Streamlit Interface
      │
      ▼
RAG Engine
      │
      ▼
Retriever
      │
      ▼
ChromaDB
      │
      ▼
Relevant Chunks
      │
      ▼
Prompt Builder
      │
      ▼
Groq Llama 3.3
      │
      ▼
Final Answer
""")

st.divider()

# ------------------------------------
# Technology Stack
# ------------------------------------

st.header("💻 Technology Stack")

tech = {
    "Frontend": "Streamlit",
    "Backend": "Python",
    "Vector Database": "ChromaDB",
    "Embedding Model": "Sentence Transformers",
    "LLM": "Llama 3.3 (Groq)",
    "Dataset": "JSON",
    "Programming Language": "Python"
}

for key, value in tech.items():
    st.write(f"**{key}:** {value}")

st.divider()

# ------------------------------------
# Project Workflow
# ------------------------------------

st.header("⚙ Workflow")

st.markdown("""
1. Load Heritage Dataset

2. Data Cleaning

3. Text Chunking

4. Generate Embeddings

5. Store in ChromaDB

6. User asks a question

7. Retrieve relevant chunks

8. Generate answer using Groq

9. Display answer with sources
""")

st.divider()

# ------------------------------------
# Project Modules
# ------------------------------------

st.header("📂 Project Structure")

st.code("""
HeritageGPT/

app.py

pages/
components/
models/
datasets/
preprocessing/
vector_db/
styles/
assets/

requirements.txt
config.py
.env
""")

st.divider()

# ------------------------------------
# Future Improvements
# ------------------------------------

st.header("🚀 Future Enhancements")

st.write("""
• Multi-language Support

• Voice Assistant

• Heritage Image Search

• Interactive Maps

• QR Code Scanner

• User Login

• Bookmark Favorite Places

• Mobile Application

• Live Tourism Recommendations

• Cloud Deployment
""")

st.divider()

# ------------------------------------
# Developer
# ------------------------------------

st.header("👨‍💻 Developer")

st.info("""
Final Year B.Tech Artificial Intelligence Student

Passionate about Artificial Intelligence,
Machine Learning,
Natural Language Processing,
Data Science,
and Retrieval-Augmented Generation (RAG).

Built using Python, Streamlit,
ChromaDB, Sentence Transformers,
and Groq.
""")

st.divider()

# ------------------------------------
# Footer
# ------------------------------------

st.caption("🏛 HeritageGPT © 2026")