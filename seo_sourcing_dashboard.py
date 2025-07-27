import streamlit as st
import pandas as pd
from keyword_module import fetch_keywords
from sourcing_module import get_alibaba_products, get_temu_products
from listing_module import generate_listing

st.set_page_config(page_title="SEO Product Research Dashboard", layout="wide")
st.title("🔍 Amazon SEO → Sourcing → Listing Dashboard")

# --- Input ---
seed_input = st.text_input("Enter seed keywords (comma-separated):", "fitness, led, pet, kitchen")
trend_min = st.slider("Min Google Trend Score", 0, 100, 20)
vol_min = st.slider("Min Search Volume", 0, 100000, 1000)
comp_max = st.slider("Max Competition", 0.0, 1.0, 0.3)
filter_intent = st.checkbox("Only show high-intent keywords", True)

if st.button("Generate Keywords"):
    seed_keywords = [kw.strip() for kw in seed_input.split(",") if kw.strip()]
    with st.spinner("🔄 Fetching keyword data..."):
        df_keywords = fetch_keywords(seed_keywords, trend_min, vol_min, comp_max, filter_intent)
    if df_keywords.empty:
        st.warning("No keywords met your criteria.")
    else:
        st.success(f"Found {len(df_keywords)} viable keywords.")
        st.dataframe(df_keywords)

        if st.button("🔗 Fetch Supplier Info"):
            all_rows = []
            with st.spinner("Searching Alibaba and Temu..."):
                for _, row in df_keywords.iterrows():
                    keyword = row['keyword']
                    ali_data = get_alibaba_products(keyword)
                    temu_data = get_temu_products(keyword)
                    all_rows.append({
                        **row,
                        **ali_data,
                        **temu_data
                    })
            df_combined = pd.DataFrame(all_rows)
            st.success("✅ Sourcing data added!")
            st.dataframe(df_combined)

            if st.button("📝 Generate Listings"):
                with st.spinner("Creating optimized Amazon listings..."):
                    listings = df_combined.apply(lambda r: generate_listing(r['keyword'], r.get('ali_title') or r.get('temu_title')), axis=1)
                    df_combined["title"] = [l["title"] for l in listings]
                    df_combined["bullets"] = ["\n".join(l["bullets"]) for l in listings]
                    df_combined["description"] = [l["description"] for l in listings]
                    df_combined["backend_keywords"] = [l["backend_keywords"] for l in listings]
                st.success("Listings generated!")
                st.dataframe(df_combined[["keyword", "title", "bullets", "description", "backend_keywords"]])

                csv = df_combined.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download Results as CSV", data=csv, file_name="product_research_results.csv")
