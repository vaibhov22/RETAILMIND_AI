import streamlit as st
import requests
from auth import require_auth

require_auth()
API_URL = "https://retailmind-ai-7h7v.onrender.com"

st.title("👤 Customer Profile")

customer_id = st.number_input(
    "Enter Customer ID",
    min_value=1,
    step=1
)

if st.button("Load Profile"):
    with st.spinner("Fetching customer data..."):

        headers = {
            "Authorization": f"Bearer {st.session_state.access_token}"
        }

        response = requests.get(
            f"{API_URL}/customer/{customer_id}",
            headers=headers
        )

    if response.status_code == 200:
        data = response.json()

        if "error" in data:
            st.error(data["error"])

        else:
            customer = data["customer"]

            st.subheader(f"{customer['name'] or 'Unknown'}")

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Phone:** {customer['phone']}")
                st.write(
                    f"**Customer Type:** "
                    f"{customer['customer_type'] or 'Not set'}"
                )
                st.write(
                    f"**Bargains:** "
                    f"{customer['bargains'] or 'Not set'}"
                )
                st.write(
                    f"**Payment Mode:** "
                    f"{customer['payment_mode'] or 'Not set'}"
                )

            with col2:
                st.write(
                    f"**Preference Tier:** "
                    f"{customer['preference_tier'] or 'Not set'}"
                )
                st.write(
                    f"**Buying Behavior:** "
                    f"{customer['buying_behavior'] or 'Not set'}"
                )
                st.write(
                    f"**Note:** "
                    f"{customer['free_note'] or '—'}"
                )

            st.divider()

            m1, m2, m3, m4 = st.columns(4)

            m1.metric(
                "Total Orders",
                data["order_count"]
            )

            m2.metric(
                "Total Spend",
                f"₹{data['total_spend']}"
            )

            m3.metric(
                "Avg Order Value",
                f"₹{round(data['average_order_value'], 2)}"
            )

            m4.metric(
                "Outstanding Credit",
                f"₹{data['outstanding_credit']}"
            )

            st.write(
                f"**Last Purchase:** {data['last_purchase']}"
            )

            st.divider()

            st.subheader("Favorite Products")

            for product in data["favorite_products"]:
                st.write(
                    f"- {product['product_name']} — "
                    f"bought {product['total_quantity']} units"
                )

    else:
        st.error(
            f"Request failed: {response.status_code}"
        )