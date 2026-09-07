import streamlit as st
import requests
from auth import require_auth

require_auth()
API_URL = "https://retailmind-ai-7h7v.onrender.com"

st.title("🔮 Prediction & Next Best Action")

customer_id = st.number_input(
    "Enter Customer ID",
    min_value=1,
    step=1,
    key="pred_customer_id"
)

if st.button("Get Prediction & Action"):

    with st.spinner("Analyzing purchase pattern..."):

        headers = {
            "Authorization": f"Bearer {st.session_state.access_token}"
        }

        pred_response = requests.get(
            f"{API_URL}/customer/{customer_id}/prediction",
            headers=headers
        )

        action_response = requests.get(
            f"{API_URL}/customer/{customer_id}/next-best-action",
            headers=headers
        )

    if pred_response.status_code == 200:
        pred = pred_response.json()

        if pred.get("status") == "not_enough_data":
            st.warning(
                "Not enough purchase history yet for this customer "
                "(need at least 2 invoices)."
            )
        else:
            st.subheader("Purchase Prediction")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Avg. Purchase Interval",
                f"{pred['average_interval']:.1f} days"
            )

            c2.metric(
                "Days Since Last Purchase",
                pred["days_since_last_bought"]
            )

            c3.metric(
                "Status",
                pred["status"].title()
            )

            st.info(pred["message"])

    if action_response.status_code == 200:
        action = action_response.json()

        if action.get("status") != "not_enough_data":

            st.divider()
            st.subheader("Recommended Action")
            st.write(action["action"])

            if "whatsapp_message" in action:
                st.divider()
                st.subheader("📱 Suggested WhatsApp Message")

                st.text_area(
                    "Message",
                    action["whatsapp_message"],
                    height=100
                )

                st.caption(
                    "Copy this message and send it to the customer."
                )