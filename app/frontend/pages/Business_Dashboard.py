import streamlit as st
import requests
from auth import require_auth

require_auth()
API_URL = "https://retailmind-ai-7h7v.onrender.com"

st.title("📊 Business Dashboard")

if st.button("Refresh Dashboard"):
    st.rerun()

with st.spinner("Loading business data..."):
    response = requests.get(f"{API_URL}/dashboard")

if response.status_code == 200:
    data = response.json()
    summary = data["summary"]

    st.subheader("Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"₹{summary['total_revenue']}")
    c2.metric("Total Orders", summary["total_orders"])
    c3.metric("Total Customers", summary["total_customers"])
    c4.metric("Avg. Order Value", f"₹{round(summary['average_order_value'], 2)}")

    st.divider()
    col_hero, col_weak = st.columns(2)

    with col_hero:
        st.subheader("🏆 Hero Products")
        for p in data["hero_products"]:
            st.write(f"**{p['product_name']}** — ₹{p['total_revenue']} revenue")

    with col_weak:
        st.subheader("📉 Weak Products")
        for p in data["weak_products"]:
            st.write(f"**{p['product_name']}** — ₹{p['total_revenue']} revenue")
else:
    st.error("Could not load dashboard data.")