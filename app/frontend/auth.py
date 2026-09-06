import streamlit as st
import httpx


SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

st.write("DEBUG URL:", repr(SUPABASE_URL))
def supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json",
    }


def send_otp(email):
    url = f"{SUPABASE_URL}/auth/v1/otp"

    response = httpx.post(
        url,
        headers=supabase_headers(),
        json={
            "email": email,
            "create_user": True,
        },
        timeout=20,
    )

    return response


def verify_otp(email, token):
    url = f"{SUPABASE_URL}/auth/v1/verify"

    response = httpx.post(
        url,
        headers=supabase_headers(),
        json={
            "email": email,
            "token": token,
            "type": "email",
        },
        timeout=20,
    )

    return response


def login_page():

    st.title("🛒 RetailMind AI")
    st.subheader("Login to continue")

    email = st.text_input(
        "Email address",
        placeholder="Enter your email"
    )

    if st.button("📧 Send OTP", use_container_width=True):

        if not email:
            st.warning("Please enter your email address.")
            return

        try:
            response = send_otp(email)

            if response.status_code in (200, 201):
                st.session_state.otp_email = email
                st.success("OTP sent! Check your email.")
            else:
                st.error(
                    f"Failed to send OTP: {response.json().get('msg', response.text)}"
                )

        except Exception as e:
            st.error(f"Connection error: {e}")

    if "otp_email" in st.session_state:

        otp = st.text_input(
            "Enter 6-digit OTP",
            max_chars=6,
            placeholder="123456"
        )

        if st.button("✅ Verify OTP", use_container_width=True):

            try:
                response = verify_otp(
                    st.session_state.otp_email,
                    otp
                )

                if response.status_code == 200:

                    data = response.json()

                    st.session_state.user = data.get("user")
                    st.session_state.access_token = data.get(
                        "access_token"
                    )

                    st.session_state.pop("otp_email", None)

                    st.rerun()

                else:
                    st.error(
                        f"Invalid or expired OTP: "
                        f"{response.json().get('msg', response.text)}"
                    )

            except Exception as e:
                st.error(f"Verification error: {e}")


def require_auth():

    if "user" not in st.session_state:
        login_page()
        st.stop()


def logout():

    st.session_state.clear()
    st.rerun()