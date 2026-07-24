import streamlit as st
from models.rag_engine import RAGEngine
from styles.theme import set_theme
from components.header import show_header
from components.sidebar import show_sidebar
from components.metrics import show_metrics
from components.footer import show_footer

# ----------------------------
# PAGE CONFIG
# ----------------------------
set_theme()

# ----------------------------
# LOAD CUSTOM CSS
# ----------------------------
try:
    with open("styles/style.css") as css:
        st.markdown(
            f"<style>{css.read()}</style>",
            unsafe_allow_html=True
        )
except FileNotFoundError:
    pass

# ----------------------------
# LOAD RAG ENGINE
# ----------------------------
@st.cache_resource
def load_rag():
    return RAGEngine()

rag = load_rag()

# ----------------------------
# SIDEBAR
# ----------------------------
show_sidebar()

# ----------------------------
# HEADER
# ----------------------------
show_header()

# ----------------------------
# METRICS
# ----------------------------
show_metrics()

# ----------------------------
# HERO SECTION
# ----------------------------
st.markdown("""
## 🏛 Explore the Heritage of Andhra Pradesh

Ask questions about:

- 🛕 Temples
- 🏰 Forts
- 🏛 Museums
- 🌊 Beaches
- 🎉 Festivals
- 📜 History
""")

st.divider()

# ----------------------------
# SESSION STATE
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------
# DISPLAY CHAT HISTORY
# ----------------------------
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])

        if msg["role"] == "assistant":

            sources = msg.get("sources", [])

            if sources:

                st.markdown("### 📚 Sources")

                for source in sources:

                    with st.expander(source["title"]):

                        st.write(
                            f"**District:** {source['district']}"
                        )

                        st.write(
                            f"**Category:** {source['category']}"
                        )

                        st.write(
                            f"**Similarity Score:** {round(source['score'],2)}"
                        )

# ----------------------------
# CHAT INPUT
# ----------------------------
question = st.chat_input(
    "Ask anything about Andhra Pradesh Heritage..."
)

if question:

    # Show user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Generate response
    with st.chat_message("assistant"):

        with st.spinner("Searching Heritage Database..."):

            try:

                result = rag.answer_question(question)

                answer = result["answer"]
                sources = result["sources"]

            except Exception as e:

                answer = f"❌ Error: {e}"
                sources = []

        st.markdown(answer)

        if sources:

            st.markdown("### 📚 Sources")

            for source in sources:

                with st.expander(source["title"]):

                    st.write(
                        f"📍 District : {source['district']}"
                    )

                    st.write(
                        f"🏷 Category : {source['category']}"
                    )

                    st.write(
                        f"⭐ Similarity : {round(source['score'],2)}"
                    )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources
            }
        )

# ----------------------------
# FOOTER
# ----------------------------
show_footer()