import streamlit as st
import os
import json

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Heritage Explorer",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Heritage Explorer")
st.caption("Explore the cultural heritage of Andhra Pradesh")

# --------------------------------------------------
# Load Dataset (Recursive)
# --------------------------------------------------

DATASET_FOLDER = "datasets"

heritage_places = []

if os.path.exists(DATASET_FOLDER):

    for root, dirs, files in os.walk(DATASET_FOLDER):

        for file in files:

            if file.endswith(".json"):

                path = os.path.join(root, file)

                try:

                    with open(path, "r", encoding="utf-8") as f:

                        data = json.load(f)

                        if isinstance(data, list):

                            heritage_places.extend(data)

                        elif isinstance(data, dict):

                            heritage_places.append(data)

                except Exception as e:

                    st.error(f"Error loading {path}")

                    st.exception(e)

else:

    st.error("Dataset folder not found!")

st.success(f"Loaded {len(heritage_places)} heritage records")
# --------------------------------------------------
# Statistics
# --------------------------------------------------

total_places = len(heritage_places)

districts = sorted({
    place.get("location", {}).get("district", "Unknown")
    for place in heritage_places
})

categories = set()

for place in heritage_places:

    info = place.get("basic_information", {})

    category = info.get("category")

    if category:
        categories.add(category)
    else:
        st.warning(f"Missing category in record: {place.get('id', 'Unknown ID')}")

categories = sorted(categories)

active_places = sum(
    1 for place in heritage_places
    if place.get("basic_information", {}).get("status") == "Active"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("🏛 Heritage Places", total_places)
col2.metric("📍 Districts", len(districts))
col3.metric("📂 Categories", len(categories))
col4.metric("✅ Active Sites", active_places)

st.divider()

# --------------------------------------------------
# Search & Filters
# --------------------------------------------------

search = st.text_input(
    "🔍 Search Heritage Place"
)

col1, col2 = st.columns(2)

selected_category = col1.selectbox(
    "Category",
    ["All"] + categories
)

selected_district = col2.selectbox(
    "District",
    ["All"] + districts
)

# --------------------------------------------------
# Filtering
# --------------------------------------------------

filtered_places = []

for place in heritage_places:

    info = place.get("basic_information", {})
    location = place.get("location", {})

    name = info.get("name", "")
    alternate_names = info.get("alternate_names", [])

    category = info.get("category", "")
    district = location.get("district", "")

    # Search
    if search:

        text = (
            name + " " +
            " ".join(alternate_names)
        ).lower()

        if search.lower() not in text:
            continue

    # Category Filter
    if (
        selected_category != "All"
        and category != selected_category
    ):
        continue

    # District Filter
    if (
        selected_district != "All"
        and district != selected_district
    ):
        continue

    filtered_places.append(place)

st.success(f"Found {len(filtered_places)} heritage places.")
# --------------------------------------------------
# Heritage Cards
# --------------------------------------------------

st.divider()

for place in filtered_places:

    info = place.get("basic_information", {})
    location = place.get("location", {})
    history = place.get("history", {})
    tourism = place.get("tourism", {})
    media = place.get("media", {})

    name = info.get("name", "Unknown Heritage")
    category = info.get("category", "Unknown")
    subcategory = info.get("subcategory", "")
    status = info.get("status", "")

    district = location.get("district", "Unknown")
    city = location.get("village_city", "")
    address = location.get("address", "")

    significance = history.get(
        "historical_significance",
        "No description available."
    )

    images = media.get("images", [])

    col1, col2 = st.columns([1, 2])

    # ----------------------------------------
    # Image
    # ----------------------------------------

    with col1:

        if len(images) > 0:

            image_path = os.path.join(
                "assets",
                "images",
                images[0]
            )

            if os.path.exists(image_path):

                st.image(
                    image_path,
                    use_container_width=True
                )

            else:

                st.image(
                    "https://placehold.co/500x350?text=No+Image",
                    use_container_width=True
                )

        else:

            st.image(
                "https://placehold.co/500x350?text=No+Image",
                use_container_width=True
            )

    # ----------------------------------------
    # Details
    # ----------------------------------------

    with col2:

        st.subheader(name)

        st.markdown(
            f"""
**Category:** {category}

**Subcategory:** {subcategory}

**District:** {district}

**Location:** {city}

**Status:** {status}
"""
        )

        st.write(significance)

        with st.expander("📍 Address"):

            st.write(address)

        with st.expander("🕒 Timings"):

            st.write(
                tourism.get(
                    "timings",
                    "Not Available"
                )
            )

        with st.expander("🎟 Entry Fee"):

            entry = tourism.get(
                "entry_fee",
                {}
            )

            if isinstance(entry, dict):

                st.write(
                    f"Free Darshan: {entry.get('free_darshan')}"
                )

                st.write(
                    entry.get(
                        "special_entry",
                        ""
                    )
                )

            else:

                st.write(entry)

    st.divider()
    # ----------------------------------------
# History
# ----------------------------------------

with st.expander("📜 History"):

    st.write(
        history.get(
            "origin",
            "Not Available"
        )
    )

    st.write("**Built By:**", history.get("built_by", "Unknown"))

    st.write("**Built Year:**", history.get("built_year", "Unknown"))

    dynasties = history.get("dynasty", [])

    if dynasties:
        st.write("**Dynasties:**")
        for d in dynasties:
            st.write(f"• {d}")

    timeline = history.get("timeline", [])

    if timeline:

        st.write("### Timeline")

        for event in timeline:

            st.write(
                f"**{event.get('year','')}** : {event.get('event','')}"
            )

# ----------------------------------------
# Architecture
# ----------------------------------------

architecture = place.get("architecture", {})

with st.expander("🏛 Architecture"):

    st.write("**Style:**", architecture.get("style", "Unknown"))

    materials = architecture.get("materials", [])

    if materials:

        st.write("### Materials")

        st.write(", ".join(materials))

    features = architecture.get("features", [])

    if features:

        st.write("### Features")

        for feature in features:

            st.write(f"✅ {feature}")

    st.write(
        architecture.get(
            "dimensions",
            ""
        )
    )

# ----------------------------------------
# Transport
# ----------------------------------------

transport = place.get("transport", {})

with st.expander("🚗 Transport"):

    airport = transport.get("nearest_airport", {})

    railway = transport.get("nearest_railway_station", {})

    bus = transport.get("nearest_bus_station", {})

    st.write("### ✈ Airport")

    st.write(
        airport.get("name", "Unknown")
    )

    st.write(
        f"Distance : {airport.get('distance_km','-')} km"
    )

    st.write("### 🚆 Railway")

    st.write(
        railway.get("name", "Unknown")
    )

    st.write(
        f"Distance : {railway.get('distance_km','-')} km"
    )

    st.write("### 🚌 Bus")

    st.write(
        bus.get("name", "Unknown")
    )

    st.write(
        f"Distance : {bus.get('distance_km','-')} km"
    )

    st.write(
        transport.get(
            "road_connectivity",
            ""
        )
    )

# ----------------------------------------
# Nearby Places
# ----------------------------------------

nearby = place.get("nearby_places", [])

with st.expander("📍 Nearby Places"):

    if nearby:

        for item in nearby:

            st.write(
                f"🏛 {item['name']} ({item['distance_km']} km)"
            )

    else:

        st.write("No nearby places available.")

# ----------------------------------------
# Facilities
# ----------------------------------------

facilities = place.get("facilities", {})

with st.expander("🏥 Facilities"):

    for key, value in facilities.items():

        icon = "✅" if value else "❌"

        st.write(
            f"{icon} {key.replace('_',' ').title()}"
        )

# ----------------------------------------
# Festivals
# ----------------------------------------

festivals = place.get("festivals", [])

with st.expander("🎉 Festivals"):

    if festivals:

        for festival in festivals:

            st.write(f"🎊 {festival}")

# ----------------------------------------
# FAQ
# ----------------------------------------

faq = place.get("faq", [])

with st.expander("❓ Frequently Asked Questions"):

    if faq:

        for item in faq:

            st.markdown(
                f"**Q:** {item['question']}"
            )

            st.write(item["answer"])

            st.divider()

# ----------------------------------------
# Useful Links
# ----------------------------------------

references = place.get("references", [])

media = place.get("media", {})

colA, colB = st.columns(2)

with colA:

    if media.get("virtual_tour"):

        st.link_button(
            "🌐 Virtual Tour",
            media["virtual_tour"]
        )

with colB:

    if references:

        st.link_button(
            "📚 Official Website",
            references[0]["url"]
        )