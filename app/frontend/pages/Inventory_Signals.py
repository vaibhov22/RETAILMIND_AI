import streamlit as st
import requests

API_URL = "https://retailmind-ai-7h7v.onrender.com"

st.title("📦 Inventory Demand Signals")
st.caption("Based on units sold in the last 30 days — not live stock levels.")

with st.spinner("Analyzing recent sales..."):
    response = requests.get(f"{API_URL}/inventory-signals")

if response.status_code == 200:
    signals = response.json()

    if signals:
        st.subheader("Fastest-Moving Products (Last 30 Days)")
        for s in signals:
            st.write(f"**{s['product_name']}** — {s['units_sold_recently']} units sold recently")
        st.info("Consider keeping extra stock of these items.")
    else:
        st.info("No recent sales data available yet.")
else:
    st.error("Could not load inventory data.")