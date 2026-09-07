import streamlit as st
import requests
from auth import require_auth

require_auth()
API_URL = "https://retailmind-ai-7h7v.onrender.com"

st.title("👤 Customer Profile")

search_type = st.radio(
    "Search customer by",
    ["Phone Number", "Name"],
    horizontal=True
)

if search_type == "Phone Number":
    search_value = st.text_input(
        "Enter Customer Phone Number"
    )
else:
    search_value = st.text_input(
        "Enter Customer Name"
    )

if st.button("Search Customer"):

    if not search_value:
        st.warning("Please enter a name or phone number.")

    else:
        headers = {
            "Authorization": f"Bearer {st.session_state.access_token}"
        }

        params = (
            {"phone": search_value}
            if search_type == "Phone Number"
            else {"name": search_value}
        )

        with st.spinner("Searching customer..."):
            response = requests.get(
                f"{API_URL}/customer-search",
                params=params,
                headers=headers
            )

        if response.status_code == 200:

            results = response.json()

            if isinstance(results, dict) and "error" in results:
                st.error(results["error"])

            elif not results:
                st.warning("Customer not found.")

            elif len(results) == 1:
                st.session_state["selected_customer_id"] = (
                    results[0]["customer_id"]
                )

            else:
                st.subheader("Customers Found")

                options = {
                    f"{c['name']} ({c['phone']})": c["customer_id"]
                    for c in results
                }

                selected = st.selectbox(
                    "Select Customer",
                    list(options.keys())
                )

                st.session_state["selected_customer_id"] = (
                    options[selected]
                )

        else:
            st.error(
                f"Search failed: {response.status_code}"
            )


if "selected_customer_id" in st.session_state:

    customer_id = st.session_state["selected_customer_id"]

    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}"
    }

    with st.spinner("Fetching customer data..."):
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

            st.subheader(
                f"{customer['name'] or 'Unknown'}"
            )

            col1, col2 = st.columns(2)

            with col1:
                st.write(
                    f"**Phone:** {customer['phone']}"
                )
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