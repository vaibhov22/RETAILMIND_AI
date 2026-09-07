import streamlit as st
import requests
from auth import require_auth

require_auth()
API_URL = "https://retailmind-ai-7h7v.onrender.com"

st.title("📤 Upload Invoice")
st.write("Upload a photo of an invoice — RetailMind will read it and save it automatically.")

uploaded_file = st.file_uploader("Choose an invoice image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded invoice", width=350)

    if st.button("Process Invoice"):
        with st.spinner("Reading invoice with AI..."):
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(f"{API_URL}/upload-invoice", files=files, headers=headers)

        if response.status_code == 200:
            result = response.json()

            if "error" in result:
                st.error(f"Something went wrong: {result['error']}")
            else:
                st.success(result["message"])
                st.write(f"**Invoice ID:** {result['invoice_id']}")
                st.write(f"**Customer ID:** {result['customer_id']}")

                if result.get("needs_profile_questions"):
                    st.warning("This is a new customer! Please answer a few quick questions.")
                    st.session_state["new_customer_id"] = result["customer_id"]
        else:
            st.error(f"Request failed: {response.status_code}")

# New customer questionnaire — appears only when needed
if "new_customer_id" in st.session_state:
    st.divider()
    st.subheader("New Customer — Quick Profile")

    with st.form("customer_profile_form"):
        customer_type = st.selectbox("Customer type", ["Regular", "Occasional", "New"])
        bargains = st.selectbox("How often do they bargain?", ["Never", "Sometimes", "Often"])
        payment_mode = st.selectbox("Preferred payment method", ["Cash", "UPI", "Credit", "Mixed"])
        preference_tier = st.selectbox("Preferred product range", ["Budget", "Mid-range", "Premium", "Not sure"])
        buying_behavior = st.selectbox("Buying behavior", ["Planned purchases", "Impulse purchases", "Mix of both", "Not sure"])
        free_note = st.text_area("Anything else important? (optional)")

        submitted = st.form_submit_button("Save Profile")

        if submitted:
            payload = {
                "customer_id": st.session_state["new_customer_id"],
                "customer_type": customer_type,
                "bargains": bargains,
                "payment_mode": payment_mode,
                "preference_tier": preference_tier,
                "buying_behavior": buying_behavior,
                "free_note": free_note
            }
            resp = requests.post(f"{API_URL}/update-customer-profile", json=payload)
            if resp.status_code == 200:
                st.success("Customer profile saved!")
                del st.session_state["new_customer_id"]
            else:
                st.error("Failed to save profile.")