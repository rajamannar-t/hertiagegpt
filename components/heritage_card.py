import streamlit as st


def show_heritage_card(title, district, category):

    with st.container(border=True):

        st.image(
            "https://placehold.co/600x300?text=Heritage",
            use_container_width=True
        )

        st.subheader(title)

        st.write(f"📍 {district}")

        st.write(f"🏷 {category}")

        st.button(
            "Explore",
            key=f"{title}"
        )