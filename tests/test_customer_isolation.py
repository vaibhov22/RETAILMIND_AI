from app.models import Business, Customer


def test_same_phone_allowed_for_different_businesses(test_db):
    business_a = Business(
        supabase_user_id="customer-user-a",
        business_name="Retailer A"
    )

    business_b = Business(
        supabase_user_id="customer-user-b",
        business_name="Retailer B"
    )

    test_db.add_all([business_a, business_b])
    test_db.commit()

    customer_a = Customer(
        business_id=business_a.business_id,
        name="Customer A",
        phone="9999999999"
    )

    customer_b = Customer(
        business_id=business_b.business_id,
        name="Customer B",
        phone="9999999999"
    )

    test_db.add_all([customer_a, customer_b])
    test_db.commit()

    customers = test_db.query(Customer).filter(
        Customer.phone == "9999999999"
    ).all()

    assert len(customers) == 2
    assert customers[0].business_id != customers[1].business_id