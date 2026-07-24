import streamlit as st


def show_source_card(source):

    with st.container(border=True):

        st.markdown(f"### 🛕 {source['title']}")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"📍 **District:** {source['district']}")
            st.write(f"🏷 **Category:** {source['category']}")

        with col2:
            score = round(source["score"], 2)
            st.write(f"⭐ Similarity: {score}")

        if "history" in source:
            st.caption(source["history"][:150] + "...")