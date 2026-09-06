import streamlit as st

st.set_page_config(page_title="RetailMind AI", page_icon="🛒", layout="wide")

st.title("🛒 RetailMind AI")
st.subheader("From Data → Decisions → Actions")

st.markdown("""
RetailMind AI turns invoices into business intelligence — automatically.

**Use the sidebar to navigate:**
- **Upload Invoice** — scan a bill, let AI extract and save it
- **Customer Profile** — see a customer's full purchase history and behavior
- **Prediction & Action** — see when a customer is likely to buy again, and get a ready-to-send message
- **Business Dashboard** — store-wide performance, hero and weak products
- **Copilot** — ask any question about your business in plain English
""")

st.info("Backend API: https://retailmind-ai-7h7v.onrender.com")