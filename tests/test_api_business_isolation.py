from fastapi.testclient import TestClient

from app.main import app
from app.models import Business, Customer
from app.auth_backend import get_current_user_id


def test_customer_search_is_business_isolated(test_db, monkeypatch):

    business_a = Business(
        supabase_user_id="api-user-a",
        business_name="Retailer A"
    )

    business_b = Business(
        supabase_user_id="api-user-b",
        business_name="Retailer B"
    )

    test_db.add_all([business_a, business_b])
    test_db.commit()

    customer_a = Customer(
        business_id=business_a.business_id,
        name="Customer A",
        phone="9000000001"
    )

    customer_b = Customer(
        business_id=business_b.business_id,
        name="Customer B",
        phone="9000000002"
    )

    test_db.add_all([customer_a, customer_b])
    test_db.commit()

    import app.main as main_module

    monkeypatch.setattr(
        main_module,
        "SessionLocal",
        lambda: test_db
    )

    # IMPORTANT:
    # main.py imported get_current_user_id from auth_backend,
    # so override the exact dependency object used by FastAPI.
    dependency = main_module.get_current_user_id

    app.dependency_overrides[dependency] = lambda: "api-user-a"

    client = TestClient(app)

    response = client.get(
        "/customer-search",
        params={"name": "Customer"}
    )

    print("USER A STATUS:", response.status_code)
    print("USER A RESPONSE:", response.text)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Customer A"

    # Switch to User B
    app.dependency_overrides[dependency] = lambda: "api-user-b"

    response = client.get(
        "/customer-search",
        params={"name": "Customer"}
    )

    print("USER B STATUS:", response.status_code)
    print("USER B RESPONSE:", response.text)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Customer B"

    app.dependency_overrides.clear()