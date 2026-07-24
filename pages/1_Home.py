import streamlit as st

# ------------------------------------
# Page Configuration
# ------------------------------------
st.set_page_config(
    page_title="Home | HeritageGPT",
    page_icon="🏛️",
    layout="wide"
)

# ------------------------------------
# Load CSS
# ------------------------------------
try:
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# ------------------------------------
# Hero Section
# ------------------------------------
st.markdown(
    """
    <div style="
        background: linear-gradient(90deg,#8B4513,#C19A6B);
        padding:40px;
        border-radius:15px;
        color:white;
        text-align:center;
    ">
        <h1>🏛️ HeritageGPT</h1>
        <h3>Explore the Rich Heritage of Andhra Pradesh</h3>
        <p>
        AI-powered heritage assistant built using RAG,
        ChromaDB, Sentence Transformers and Groq.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# ------------------------------------
# Search
# ------------------------------------
st.subheader("🔍 Search Heritage Places")

search = st.text_input(
    "",
    placeholder="Search temples, forts, museums..."
)

if search:
    st.success(f"Searching for: {search}")

st.divider()

# ------------------------------------
# Quick Explore
# ------------------------------------
st.subheader("🧭 Quick Explore")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.button("🛕 Temples", use_container_width=True)

with col2:
    st.button("🏰 Forts", use_container_width=True)

with col3:
    st.button("🏛 Museums", use_container_width=True)

with col4:
    st.button("🌊 Beaches", use_container_width=True)

st.divider()

# ------------------------------------
# Featured Heritage
# ------------------------------------
st.subheader("⭐ Featured Heritage Places")

col1, col2, col3 = st.columns(3)

with col1:
    st.image(
        "https://placehold.co/600x350?text=Tirumala+Temple",
        use_container_width=True
    )
    st.markdown("### 🛕 Tirumala Temple")
    st.write("📍 Tirupati")
    st.write(
        "One of the world's most visited Hindu temples."
    )

with col2:
    st.image(
        "https://placehold.co/600x350?text=Lepakshi",
        use_container_width=True
    )
    st.markdown("### 🏛 Lepakshi")
    st.write("📍 Sri Sathya Sai")
    st.write(
        "Famous for hanging pillar and Vijayanagara architecture."
    )

with col3:
    st.image(
        "https://placehold.co/600x350?text=Gandikota",
        use_container_width=True
    )
    st.markdown("### 🏰 Gandikota Fort")
    st.write("📍 YSR Kadapa")
    st.write(
        "Known as the Grand Canyon of India."
    )

st.divider()

# ------------------------------------
# Categories
# ------------------------------------
st.subheader("📚 Heritage Categories")

c1, c2 = st.columns(2)

with c1:
    st.info("""
🛕 Temples

- Tirumala
- Srisailam
- Simhachalam
- Kanaka Durga
""")

    st.info("""
🏰 Forts

- Gandikota
- Kondapalli
- Chandragiri
""")

with c2:
    st.info("""
🏛 Museums

- Amaravati Museum
- Visakha Museum
- Tribal Museum
""")

    st.info("""
🌊 Beaches

- RK Beach
- Rushikonda
- Yarada Beach
""")

st.divider()

# ------------------------------------
# Statistics
# ------------------------------------
st.subheader("📊 Knowledge Base")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Heritage Places", "150+")

with m2:
    st.metric("Knowledge Chunks", "1800+")

with m3:
    st.metric("Embedding Model", "MiniLM")

with m4:
    st.metric("LLM", "Llama 3.3")

st.divider()

# ------------------------------------
# Why HeritageGPT?
# ------------------------------------
st.subheader("💡 Why HeritageGPT?")

st.markdown("""
- 🤖 AI-powered heritage assistant
- 🧠 Retrieval-Augmented Generation (RAG)
- 🗂 ChromaDB vector database
- 🔍 Semantic search using Sentence Transformers
- ⚡ Groq Llama 3.3 for fast responses
- 📚 Provides answers with retrieved sources
""")

st.divider()

# ------------------------------------
# Footer
# ------------------------------------
st.markdown(
    """
    <center>
    <h4>🏛 HeritageGPT</h4>
    <p>
    Built with ❤️ using Python, Streamlit, ChromaDB,
    Sentence Transformers and Groq.
    </p>
    </center>
    """,
    unsafe_allow_html=True,
)