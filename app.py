
import logging
import streamlit as st
from models.rag_engine import RAGEngine

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="HeritageGPT | Discover Andhra Pradesh",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =====================================================
# ATTRACTIVE CHAT DESIGN
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

:root {
    --green: #18543b;
    --green-dark: #103b2b;
    --gold: #c49b4b;
    --ink: #27372d;
    --muted: #718074;
    --paper: #f7f8f3;
}

/* Main background */
.stApp {
    background:
        radial-gradient(ellipse at 50% 0%, #e8f0e5 0%, transparent 48%),
        var(--paper) !important;
    color: var(--ink) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Remove sidebar and navigation */
[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stDecoration"],
#MainMenu,
footer {
    display: none !important;
}

/* Hide top header without affecting chat input */
[data-testid="stHeader"] {
    background: transparent !important;
}

/* Page width */
.block-container {
    max-width: 850px !important;
    padding: 24px 22px 115px !important;
}

/* Brand */
.brand {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin: 8px 0 24px;
}

.brand-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 16px;
    background: var(--green);
    color: #f5dfaa;
    font-size: 26px;
    box-shadow: 0 5px 15px #18543b20;
}

.brand-name {
    color: var(--green-dark) !important;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 30px;
    font-weight: 700;
    letter-spacing: -0.6px;
}

.brand-caption {
    text-align: center;
    color: var(--muted) !important;
    font-size: 13px;
    margin-top: -16px;
    margin-bottom: 28px;
}

/* Welcome panel */
.welcome {
    background: linear-gradient(135deg, #123e2c, #236345);
    border: 1px solid #c5a35f;
    border-radius: 24px;
    padding: 32px 30px;
    margin: 12px 0 26px;
    box-shadow: 0 12px 32px #173f2c12;
}

.welcome-tag {
    color: #f1d394 !important;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 13px;
}

.welcome-title {
    color: #ffffff !important;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(27px, 4vw, 38px);
    line-height: 1.2;
    margin-bottom: 13px;
}

.welcome-text {
    color: #e4eee5 !important;
    font-size: 14px;
    line-height: 1.8;
    margin: 0;
}

.welcome-divider {
    width: 52px;
    height: 3px;
    border-radius: 5px;
    background: #d5b66f;
    margin-top: 20px;
}

/* Section labels */
.section-label {
    color: #365743 !important;
    font-size: 13px;
    font-weight: 700;
    margin: 18px 0 12px;
}

/* Example prompt buttons */
.stButton > button {
    background: #ffffff !important;
    color: #31533e !important;
    border: 1px solid #dce5d8 !important;
    border-radius: 14px !important;
    min-height: 58px !important;
    padding: 12px 14px !important;
    text-align: left !important;
    white-space: normal !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    box-shadow: 0 3px 12px #173f2c08;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #edf4e9 !important;
    border-color: #b9a064 !important;
    color: #123e2c !important;
    transform: translateY(-1px);
}

/* Chat bubbles */
[data-testid="stChatMessage"] {
    background: #ffffff !important;
    border: 1px solid #e2e8de !important;
    border-radius: 18px !important;
    padding: 14px 17px !important;
    margin-bottom: 13px !important;
    box-shadow: 0 3px 12px #173f2c06;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {
    color: #293b30 !important;
    font-size: 14px;
    line-height: 1.8;
}

[data-testid="stChatMessage"] a {
    color: #176543 !important;
}

/* Fixed composer area */
[data-testid="stBottom"] {
    background: linear-gradient(
        to bottom,
        #f7f8f300,
        #f7f8f3 24%
    ) !important;
}

[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
.stChatInputContainer {
    background: #f7f8f3 !important;
}

[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 1px solid #ccd9c8 !important;
    border-radius: 18px !important;
    box-shadow: 0 6px 24px #173f2c0d !important;
    overflow: hidden;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #5d896b !important;
    box-shadow: 0 0 0 2px #18543b14 !important;
}

[data-testid="stChatInput"] textarea {
    color: #27372d !important;
    -webkit-text-fill-color: #27372d !important;
    background: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #89948a !important;
    -webkit-text-fill-color: #89948a !important;
}

/* Source cards */
[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #dce5d8 !important;
    border-radius: 13px !important;
}

[data-testid="stExpander"] p {
    color: #35483b !important;
}

/* Small helper text */
.helper-text {
    color: #859084 !important;
    text-align: center;
    font-size: 11px;
    padding-top: 15px;
}

/* Mobile layout */
@media (max-width: 600px) {
    .block-container {
        padding: 15px 12px 100px !important;
    }

    .brand-name {
        font-size: 25px;
    }

    .welcome {
        padding: 25px 21px;
        border-radius: 19px;
    }
}

/* Fix headings and Markdown inside chat messages */
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] h4,
[data-testid="stChatMessage"] h5,
[data-testid="stChatMessage"] h6 {
    color: #174734 !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Fix normal answer text */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] em {
    color: #293b30 !important;
    opacity: 1 !important;
}

/* Fix text in Markdown containers */
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
    color: #293b30 !important;
}

/* Make horizontal rules visible */
[data-testid="stChatMessage"] hr {
    border-color: #dce5d8 !important;
}

/* Ensure the assistant message background remains white */
[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# LOAD RAG ENGINE
# =====================================================
@st.cache_resource
def load_rag():
    return RAGEngine()


try:
    rag = load_rag()
except Exception as e:
    st.error("HeritageGPT could not start.")
    st.exception(e)
    st.stop()


# =====================================================
# SESSION STATE
# =====================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "suggested_question" not in st.session_state:
    st.session_state.suggested_question = None


def choose_question(question):
    st.session_state.suggested_question = question


def clear_conversation():
    st.session_state.messages = []
    st.session_state.suggested_question = None


# =====================================================
# BRAND HEADER
# =====================================================
st.markdown("""
<div class="brand">
    <div class="brand-icon">🏛️</div>
    <div class="brand-name">HeritageGPT</div>
</div>
<div class="brand-caption">
    Your personal AI guide to Andhra Pradesh
</div>
""", unsafe_allow_html=True)


# =====================================================
# WELCOME SCREEN
# Show only when the conversation is empty
# =====================================================
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
        <div class="welcome-tag">Discover · Learn · Explore</div>
        <div class="welcome-title">
            Every place has a story.<br>
            Let's discover yours.
        </div>
        <p class="welcome-text">
            Explore ancient temples, historic forts, coastal destinations,
            and the rich traditions of Andhra Pradesh. Ask a question to
            begin your journey through our heritage.
        </p>
        <div class="welcome-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-label">✨ Start with a question</div>',
        unsafe_allow_html=True,
    )

    prompts = [
        ("🛕  Famous temples", "What are the famous temples in Andhra Pradesh?"),
        ("🏰  Historic forts", "Tell me about the historic forts in Andhra Pradesh."),
        ("🌊  Beautiful beaches", "What are some notable beaches in Andhra Pradesh?"),
        ("📜  Local history", "Tell me about the history and heritage of Amaravati."),
    ]

    col1, col2 = st.columns(2)

    for i, (label, prompt) in enumerate(prompts):
        with (col1 if i % 2 == 0 else col2):
            st.button(
                label,
                key=f"prompt_{i}",
                use_container_width=True,
                on_click=choose_question,
                args=(prompt,),
            )

    st.markdown(
        '<div class="helper-text">'
        'Choose a topic above or type your own question below.'
        '</div>',
        unsafe_allow_html=True,
    )


# =====================================================
# SOURCE DISPLAY
# =====================================================
def show_sources(sources):
    if not sources:
        return

    with st.expander(f"📚 Sources and references · {len(sources)}"):
        for index, source in enumerate(sources):
            title = source.get("title") or f"Heritage source {index + 1}"
            district = source.get("district")
            category = source.get("category")
            url = source.get("source_url") or source.get("url")

            st.markdown(f"**{title}**")

            details = []
            if district:
                details.append(f"District: {district}")
            if category:
                details.append(f"Category: {category}")

            if details:
                st.caption(" · ".join(details))

            if isinstance(url, str) and url.startswith(("https://", "http://")):
                st.markdown(f"[View reference ↗]({url})")

            if index < len(sources) - 1:
                st.divider()


# =====================================================
# CONVERSATION HISTORY
# =====================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            show_sources(message.get("sources", []))


# =====================================================
# CHAT INPUT
# =====================================================
typed_question = st.chat_input(
    "Ask about temples, forts, history, or culture..."
)

# Support clickable example prompts.
if st.session_state.suggested_question is not None:
    question = st.session_state.suggested_question
    st.session_state.suggested_question = None
else:
    question = typed_question


# =====================================================
# GENERATE ANSWER
# =====================================================
if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    answer = ""
    sources = []

    with st.chat_message("assistant"):
        with st.spinner("Discovering your answer..."):
            try:
                result = rag.answer_question(question)
                answer = result.get(
                    "answer",
                    "Sorry, I couldn't generate an answer.",
                )
                sources = result.get("sources", []) or []

            except Exception:
                logging.exception("HeritageGPT query failed")
                answer = (
                    "I couldn't process your question just now. "
                    "Please try again."
                )
                st.error("Please check the VS Code terminal for details.")

        st.markdown(answer)
        show_sources(sources)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })

    # Refresh to remove the welcome screen and show the conversation.
    st.rerun()


# =====================================================
# CLEAR CHAT CONTROL
# =====================================================
if st.session_state.messages:
    st.markdown("---")
    if st.button("↺ Start a new conversation", use_container_width=True):
        clear_conversation()
        st.rerun()
