import streamlit as st
import pandas as pd

# ------------------------------------
# Page Configuration
# ------------------------------------

st.set_page_config(
    page_title="Statistics | HeritageGPT",
    page_icon="📊",
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

st.title("📊 HeritageGPT Dashboard")

st.caption("Knowledge Base Statistics")

st.divider()

# ------------------------------------
# Top Metrics
# ------------------------------------

col1, col2, col3, col4 = st.columns(4)

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
        "Embedding Model",
        "MiniLM-L6-v2"
    )

with col4:
    st.metric(
        "LLM",
        "Llama 3.3"
    )

st.divider()

# ------------------------------------
# Category Statistics
# ------------------------------------

st.subheader("🏛 Heritage Categories")

category_data = pd.DataFrame(
    {
        "Category": [
            "Temple",
            "Fort",
            "Museum",
            "Beach",
            "Monument",
            "Palace"
        ],
        "Count": [
            70,
            20,
            18,
            15,
            12,
            15
        ]
    }
)

st.bar_chart(
    category_data.set_index("Category")
)

st.divider()

# ------------------------------------
# District Statistics
# ------------------------------------

st.subheader("📍 Top Districts")

district_data = pd.DataFrame(
    {
        "District":[
            "Tirupati",
            "Visakhapatnam",
            "Nandyal",
            "YSR Kadapa",
            "Guntur"
        ],
        "Places":[
            25,
            18,
            15,
            12,
            10
        ]
    }
)

st.dataframe(
    district_data,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ------------------------------------
# AI Model Information
# ------------------------------------

st.subheader("🤖 AI Configuration")

left, right = st.columns(2)

with left:

    st.success("Embedding Model")

    st.code(
"""
sentence-transformers/
all-MiniLM-L6-v2
"""
    )

    st.success("Vector Database")

    st.code("ChromaDB")

with right:

    st.success("LLM")

    st.code("Llama-3.3-70B-Versatile")

    st.success("Inference Provider")

    st.code("Groq")

st.divider()

# ------------------------------------
# System Information
# ------------------------------------

st.subheader("⚙ System")

system = pd.DataFrame({

    "Component":[

        "Frontend",

        "Backend",

        "Vector DB",

        "Embeddings",

        "LLM",

        "Dataset"

    ],

    "Technology":[

        "Streamlit",

        "Python",

        "ChromaDB",

        "Sentence Transformers",

        "Groq",

        "JSON"

    ]

})

st.table(system)

st.divider()

# ------------------------------------
# Performance
# ------------------------------------

st.subheader("🚀 Performance")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Average Response",
        "1.2 sec"
    )

with col2:

    st.metric(
        "Similarity Search",
        "< 100 ms"
    )

with col3:

    st.metric(
        "Accuracy",
        "Semantic Search"
    )

st.divider()

# ------------------------------------
# Footer
# ------------------------------------

st.caption(
    "🏛 HeritageGPT Dashboard | Built with Streamlit"
)