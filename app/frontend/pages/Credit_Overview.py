import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("💰 Credit / Udhaar Overview")

with st.spinner("Loading credit data..."):
    response = requests.get(f"{API_URL}/credit-overview")

if response.status_code == 200:
    data = response.json()

    st.metric("Total Outstanding Credit", f"₹{data['total_outstanding']}")
    st.divider()

    if data["customers"]:
        st.subheader("Customers with Outstanding Credit")
        for c in data["customers"]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{c['name']}** ({c['phone']})")
            with col2:
                st.write(f"₹{c['total_credit']}")
    else:
        st.success("No outstanding credit right now!")
else:
    st.error("Could not load credit data.")