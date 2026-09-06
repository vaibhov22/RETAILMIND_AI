import streamlit as st
import requests
from auth import require_auth

require_auth()
API_URL = "https://retailmind-ai-7h7v.onrender.com"

st.title("🔗 Product Bundle Suggestions")
st.write("Products that customers frequently buy together.")

with st.spinner("Analyzing purchase patterns..."):
    response = requests.get(f"{API_URL}/product-bundles")

if response.status_code == 200:
    bundles = response.json()

    if bundles:
        for b in bundles:
            st.write(f"**{b['product_1']}** + **{b['product_2']}** — bought together {b['times_bought_together']} times")
    else:
        st.info("Not enough data yet to find bundle patterns. Upload more invoices with overlapping products.")
else:
    st.error("Could not load bundle data.")