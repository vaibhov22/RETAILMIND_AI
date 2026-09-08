import os
import requests

API_URL = "https://retailmind-ai-7h7v.onrender.com"

TOKEN_A = os.getenv("RETAILMIND_TOKEN_A")
TOKEN_B = os.getenv("RETAILMIND_TOKEN_B")

CUSTOMER_A_ID = os.getenv("RETAILMIND_CUSTOMER_A_ID")


def test(name, passed, detail=""):
    print(f"{'✅' if passed else '❌'} {name}")
    if detail:
        print(f"   {detail}")


def request(method, endpoint, token=None, **kwargs):
    headers = kwargs.pop("headers", {})

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return requests.request(
        method,
        f"{API_URL}{endpoint}",
        headers=headers,
        timeout=30,
        **kwargs
    )


print("=" * 60)
print("RETAILMIND AI — AUTH & MULTI-TENANT SECURITY TEST")
print("=" * 60)

# ------------------------------------------------------------
# 1. Missing authentication
# ------------------------------------------------------------

try:
    response = request("GET", "/dashboard")

    test(
        "Missing token rejected",
        response.status_code == 401,
        f"HTTP {response.status_code}"
    )
except Exception as e:
    test("Missing token rejected", False, str(e))


# ------------------------------------------------------------
# 2. Invalid authentication
# ------------------------------------------------------------

try:
    response = request(
        "GET",
        "/dashboard",
        token="invalid-token"
    )

    test(
        "Invalid token rejected",
        response.status_code == 401,
        f"HTTP {response.status_code}"
    )
except Exception as e:
    test("Invalid token rejected", False, str(e))


# ------------------------------------------------------------
# 3. Malformed Authorization header
# ------------------------------------------------------------

try:
    response = request(
        "GET",
        "/dashboard",
        headers={
            "Authorization": "Invalid invalid-token"
        }
    )

    test(
        "Malformed Authorization header rejected",
        response.status_code == 401,
        f"HTTP {response.status_code}"
    )
except Exception as e:
    test(
        "Malformed Authorization header rejected",
        False,
        str(e)
    )


# ------------------------------------------------------------
# 4. Authenticated user A
# ------------------------------------------------------------

if TOKEN_A:
    try:
        response = request(
            "GET",
            "/dashboard",
            token=TOKEN_A
        )

        test(
            "Authenticated user A can access dashboard",
            response.status_code == 200,
            f"HTTP {response.status_code}"
        )
    except Exception as e:
        test(
            "Authenticated user A can access dashboard",
            False,
            str(e)
        )
else:
    print("⚠️ User A token not supplied — skipping authenticated test.")


# ------------------------------------------------------------
# 5. Authenticated user B
# ------------------------------------------------------------

if TOKEN_B:
    try:
        response = request(
            "GET",
            "/dashboard",
            token=TOKEN_B
        )

        test(
            "Authenticated user B can access dashboard",
            response.status_code == 200,
            f"HTTP {response.status_code}"
        )
    except Exception as e:
        test(
            "Authenticated user B can access dashboard",
            False,
            str(e)
        )
else:
    print("⚠️ User B token not supplied — skipping authenticated test.")


# ------------------------------------------------------------
# 6. Cross-tenant customer isolation
# ------------------------------------------------------------

if TOKEN_A and TOKEN_B and CUSTOMER_A_ID:
    try:
        response = request(
            "GET",
            f"/customer/{CUSTOMER_A_ID}",
            token=TOKEN_B
        )

        blocked = (
            response.status_code == 404
            or (
                response.status_code == 200
                and (
                    isinstance(response.json(), dict)
                    and response.json().get("error") == "Customer not found"
                )
            )
        )

        test(
            "User B cannot access User A customer",
            blocked,
            f"HTTP {response.status_code} — {response.text[:200]}"
        )

    except Exception as e:
        test(
            "User B cannot access User A customer",
            False,
            str(e)
        )
else:
    print(
        "⚠️ Cross-tenant test skipped. "
        "Set RETAILMIND_TOKEN_A, RETAILMIND_TOKEN_B, "
        "and RETAILMIND_CUSTOMER_A_ID."
    )


# ------------------------------------------------------------
# 7. Cross-tenant customer search
# ------------------------------------------------------------

if TOKEN_A and TOKEN_B:
    try:
        response_a = request(
            "GET",
            "/customer-search?name=",
            token=TOKEN_A
        )

        response_b = request(
            "GET",
            "/customer-search?name=",
            token=TOKEN_B
        )

        test(
            "Customer search requires a valid authenticated session",
            response_a.status_code in (200, 400),
            f"User A HTTP {response_a.status_code}"
        )

        test(
            "Customer search requires a valid authenticated session",
            response_b.status_code in (200, 400),
            f"User B HTTP {response_b.status_code}"
        )

    except Exception as e:
        test(
            "Customer search authentication",
            False,
            str(e)
        )


print("\n" + "=" * 60)
print("SECURITY TEST COMPLETE")
print("=" * 60)
print(
    "For the strongest multi-tenant test, provide two valid Supabase "
    "access tokens belonging to different businesses and a customer ID "
    "belonging to User A."
)
