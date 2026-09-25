from app.models import Business, Customer


def test_business_data_isolation(test_db):
    # Create two separate retailers
    business_a = Business(
        supabase_user_id="user-a",
        business_name="Retailer A"
    )

    business_b = Business(
        supabase_user_id="user-b",
        business_name="Retailer B"
    )

    test_db.add_all([business_a, business_b])
    test_db.commit()

    # Create one customer for each retailer
    customer_a = Customer(
        business_id=business_a.business_id,
        name="Customer A",
        phone="9999999991"
    )

    customer_b = Customer(
        business_id=business_b.business_id,
        name="Customer B",
        phone="9999999992"
    )

    test_db.add_all([customer_a, customer_b])
    test_db.commit()

    # Retailer A can only see its own customer
    retailer_a_customers = (
        test_db.query(Customer)
        .filter(Customer.business_id == business_a.business_id)
        .all()
    )

    assert len(retailer_a_customers) == 1
    assert retailer_a_customers[0].name == "Customer A"

    # Retailer B can only see its own customer
    retailer_b_customers = (
        test_db.query(Customer)
        .filter(Customer.business_id == business_b.business_id)
        .all()
    )

    assert len(retailer_b_customers) == 1
    assert retailer_b_customers[0].name == "Customer B"

    # Verify the businesses cannot see each other's customers
    assert all(
        customer.business_id != business_b.business_id
        for customer in retailer_a_customers
    )

    assert all(
        customer.business_id != business_a.business_id
        for customer in retailer_b_customers
    )