import streamlit as st
import httpx
import extra_streamlit_components as stx


SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]


def get_cookie_manager():
    if "cookie_manager" not in st.session_state:
        st.session_state.cookie_manager = stx.CookieManager(key="retailmind_cookies")
    return st.session_state.cookie_manager


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
        json={"email": email, "create_user": True},
        timeout=20,
    )
    return response


def verify_otp(email, token):
    url = f"{SUPABASE_URL}/auth/v1/verify"
    response = httpx.post(
        url,
        headers=supabase_headers(),
        json={"email": email, "token": token, "type": "email"},
        timeout=20,
    )
    return response


def login_page():
    st.title("🛒 RetailMind AI")
    st.subheader("Login to continue")

    email = st.text_input("Email address", placeholder="Enter your email")

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
                try:
                    message = response.json().get("msg", response.text)
                except Exception:
                    message = response.text
                st.error(f"Failed to send OTP: {message}")
        except Exception as e:
            st.error(f"Connection error: {e}")

    if "otp_email" in st.session_state:
        otp = st.text_input("Enter 6-digit OTP", max_chars=6, placeholder="123456")

        if st.button("✅ Verify OTP", use_container_width=True):
            try:
                response = verify_otp(st.session_state.otp_email, otp)

                if response.status_code == 200:
                    data = response.json()

                    st.session_state.user = data.get("user")
                    st.session_state.access_token = data.get("access_token")

                    # Save token in a real browser cookie so it survives refresh
                    cookie_manager = get_cookie_manager()
                    cookie_manager.set(
                        "retailmind_access_token",
                        data.get("access_token"),
                        key="set_token_cookie"
                    )

                    st.session_state.pop("otp_email", None)
                    st.rerun()

                else:
                    try:
                        message = response.json().get("msg", response.text)
                    except Exception:
                        message = response.text
                    st.error(f"Invalid or expired OTP: {message}")

            except Exception as e:
                st.error(f"Verification error: {e}")


def require_auth():
    # Already logged in this session — nothing to do
    if "access_token" in st.session_state:
        return

    cookie_manager = get_cookie_manager()
    cookies = cookie_manager.get_all()

    # Cookie manager hasn't synced with the browser yet — wait for it
    if cookies is None:
        st.stop()

    token_from_cookie = cookies.get("retailmind_access_token")

    if token_from_cookie:
        st.session_state.access_token = token_from_cookie
        return

    # Genuinely no cookie and no session — show login
    login_page()
    st.stop()

def logout():
    cookie_manager = get_cookie_manager()
    cookie_manager.delete("retailmind_access_token", key="delete_token_cookie")
    st.session_state.clear()
    st.rerun()