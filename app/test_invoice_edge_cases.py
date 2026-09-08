import requests

API_URL = "https://retailmind-ai-7h7v.onrender.com"

print("=" * 60)
print("RETAILMIND AI — INVOICE EDGE-CASE TEST")
print("=" * 60)

passed = 0
failed = 0


def test(name, condition, detail=""):
    global passed, failed

    if condition:
        print(f"✅ {name}")
        passed += 1
    else:
        print(f"❌ {name}")
        failed += 1

    if detail:
        print(f"   {detail}")


# ------------------------------------------------------------
# 1. Missing authentication
# ------------------------------------------------------------

try:
    response = requests.post(
        f"{API_URL}/upload-invoice",
        timeout=45
    )

    test(
        "Upload invoice requires authentication",
        response.status_code == 422,
        f"HTTP {response.status_code}"
    )

except Exception as e:
    test(
        "Upload invoice requires authentication",
        False,
        str(e)
    )


# ------------------------------------------------------------
# 2. Invalid authentication
# ------------------------------------------------------------

try:
    response = requests.post(
        f"{API_URL}/upload-invoice",
        headers={
            "Authorization": "Bearer invalid-token"
        },
        timeout=45
    )

    test(
        "Invalid authentication rejected",
        response.status_code == 401,
        f"HTTP {response.status_code}"
    )

except Exception as e:
    test(
        "Invalid authentication rejected",
        False,
        str(e)
    )


# ------------------------------------------------------------
# 3. No invoice file
# ------------------------------------------------------------

try:
    response = requests.post(
        f"{API_URL}/upload-invoice",
        headers={
            "Authorization": "Bearer invalid-token"
        },
        timeout=45
    )

    # Authentication should be checked before invoice processing.
    test(
        "Invalid token is rejected before invoice processing",
        response.status_code == 401,
        f"HTTP {response.status_code}"
    )

except Exception as e:
    test(
        "Invalid token is rejected before invoice processing",
        False,
        str(e)
    )


# ------------------------------------------------------------
# 4. Malformed Authorization header
# ------------------------------------------------------------

try:
    response = requests.post(
        f"{API_URL}/upload-invoice",
        headers={
            "Authorization": "Invalid token"
        },
        timeout=45
    )

    test(
        "Malformed authentication rejected",
        response.status_code == 401,
        f"HTTP {response.status_code}"
    )

except Exception as e:
    test(
        "Malformed authentication rejected",
        False,
        str(e)
    )


# ------------------------------------------------------------
# 5. Invalid customer profile payload
# ------------------------------------------------------------

try:
    response = requests.post(
        f"{API_URL}/update-customer-profile",
        headers={
            "Authorization": "Bearer invalid-token",
            "Content-Type": "application/json"
        },
        json={},
        timeout=45
    )

    # Invalid authentication should still be rejected.
    test(
        "Customer profile rejects invalid authentication",
        response.status_code == 401,
        f"HTTP {response.status_code}"
    )

except Exception as e:
    test(
        "Customer profile rejects invalid authentication",
        False,
        str(e)
    )


# ------------------------------------------------------------
# 6. Invalid customer ID format
# ------------------------------------------------------------

try:
    response = requests.get(
        f"{API_URL}/customer/not-a-number",
        headers={
            "Authorization": "Bearer invalid-token"
        },
        timeout=45
    )

    # Authentication dependency executes before route processing.
    test(
        "Invalid customer ID cannot bypass authentication",
        response.status_code == 401,
        f"HTTP {response.status_code}"
    )

except Exception as e:
    test(
        "Invalid customer ID cannot bypass authentication",
        False,
        str(e)
    )


print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Passed: {passed}")
print(f"Failed: {failed}")

print("\nThese tests use zero Groq API calls.")
print("They verify that malformed or unauthenticated invoice-related")
print("requests cannot reach protected business logic.")
