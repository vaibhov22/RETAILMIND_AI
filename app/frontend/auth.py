import streamlit as st
from supabase import create_client


SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


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
            supabase.auth.sign_in_with_otp(
                {
                    "email": email,
                    "options": {
                        "should_create_user": True
                    }
                }
            )

            st.session_state.otp_email = email
            st.success("OTP sent! Check your email.")

        except Exception as e:
            st.error(f"Failed to send OTP: {e}")

    if "otp_email" in st.session_state:

        otp = st.text_input(
            "Enter 6-digit OTP",
            max_chars=6,
            placeholder="123456"
        )

        if st.button("✅ Verify OTP", use_container_width=True):
            try:
                response = supabase.auth.verify_otp(
                    {
                        "email": st.session_state.otp_email,
                        "token": otp,
                        "type": "email"
                    }
                )

                if response.user:
                    st.session_state.user = response.user
                    st.session_state.pop("otp_email", None)
                    st.rerun()

            except Exception:
                st.error("Invalid or expired OTP.")


def require_auth():

    if "user" not in st.session_state:
        login_page()
        st.stop()


def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.clear()
    st.rerun()
