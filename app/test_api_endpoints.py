import requests

API_URL = "https://retailmind-ai-7h7v.onrender.com"

ENDPOINTS = [
    ("GET", "/dashboard"),
    ("GET", "/credit-overview"),
    ("GET", "/product-bundles"),
    ("GET", "/inventory-signals"),
    ("GET", "/customer-search?name=test"),
    ("GET", "/customer/999999"),
    ("GET", "/customer/999999/prediction"),
    ("GET", "/customer/999999/next-best-action"),
    ("GET", "/copilot?question=What%20is%20my%20total%20revenue%3F"),
]

print("=" * 60)
print("RETAILMIND AI — API ENDPOINT SECURITY TEST")
print("=" * 60)

passed = 0
failed = 0

for method, endpoint in ENDPOINTS:
    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            timeout=45
        )

        # FastAPI returns 422 because Authorization is declared
        # as a required header with Header(...).
        if response.status_code == 422:
            print(f"✅ {method} {endpoint} → 422 Missing Authorization")
            passed += 1
        else:
            print(
                f"❌ {method} {endpoint} → "
                f"HTTP {response.status_code}"
            )
            failed += 1

    except requests.exceptions.Timeout:
        print(f"⚠️ {method} {endpoint} → Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"❌ {method} {endpoint} → {e}")
        failed += 1

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(
    "\nExpected behavior: protected endpoints return 422 when "
    "the required Authorization header is completely missing."
)
