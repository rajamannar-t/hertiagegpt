import streamlit as st


def show_footer():

    st.divider()

    st.markdown(
        """
<center>

🏛 HeritageGPT

Made with ❤️ using

Python • Streamlit • ChromaDB • Groq

</center>
""",
        unsafe_allow_html=True
    )