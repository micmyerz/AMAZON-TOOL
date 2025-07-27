import streamlit as st
from keyword_module import fetch_filtered_keywords, cluster_keywords
from listing_module import generate_listing  # assumes OpenAI is used in listing_module

st.set_page_config(page_title="Amazon Keyword Explorer", layout="wide")
st.title("🔍 Amazon Product Automation Tool")

# Input
seed = st.text_input("Enter a product idea keyword:", "wireless earbuds")
max_results = st.slider("Max suggestions", 5, 30, 20)
trend_min = st.slider("Min Google Trends score", 0, 100, 10)
require_intent = st.checkbox("Require high buyer intent", True)
cluster_toggle = st.checkbox("Group similar keywords", True)

if st.button("Fetch Keywords"):
    with st.spinner("Fetching and filtering keywords..."):
        keywords = fetch_filtered_keywords(
            seed_keyword=seed,
            max_results=max_results,
            trend_min=trend_min,
            require_intent=require_intent
        )

        if cluster_toggle:
            clusters = cluster_keywords(keywords, distance_threshold=0.7)
            for cid, kws in clusters.items():
                with st.expander(f"Cluster {cid} - {len(kws)} keywords"):
                    st.write(kws)
        else:
            st.write("### Filtered Keywords:")
            st.write(keywords)

        st.session_state["last_keywords"] = keywords

# Listing Generator
if "last_keywords" in st.session_state:
    st.subheader("📦 Generate Amazon Listing")
    chosen_kw = st.selectbox("Choose keyword for listing:", st.session_state["last_keywords"])
    if st.button("Generate Listing"):
        with st.spinner("Generating title, bullets, and description..."):
            listing = generate_listing(chosen_kw)
            st.write("**Title:**", listing["title"])
            st.write("**Bullets:**")
            for bullet in listing["bullets"]:
                st.markdown(f"- {bullet}")
            st.write("**Description:**")
            st.markdown(listing["description"])
