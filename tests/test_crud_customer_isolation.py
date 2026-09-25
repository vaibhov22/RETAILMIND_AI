from app.models import Business
from app.crud import get_or_create_customer


def test_get_or_create_customer_is_business_scoped(test_db):
    business_a = Business(
        supabase_user_id="crud-user-a",
        business_name="Retailer A"
    )

    business_b = Business(
        supabase_user_id="crud-user-b",
        business_name="Retailer B"
    )

    test_db.add_all([business_a, business_b])
    test_db.commit()

    customer_a = get_or_create_customer(
        test_db,
        name="Customer A",
        phone="8888888888",
        business_id=business_a.business_id
    )

    customer_b = get_or_create_customer(
        test_db,
        name="Customer B",
        phone="8888888888",
        business_id=business_b.business_id
    )

    test_db.commit()

    assert customer_a.customer_id != customer_b.customer_id
    assert customer_a.business_id == business_a.business_id
    assert customer_b.business_id == business_b.business_id


def test_get_or_create_customer_reuses_customer_within_same_business(test_db):
    business = Business(
        supabase_user_id="crud-same-user",
        business_name="Retailer A"
    )

    test_db.add(business)
    test_db.commit()

    customer_1 = get_or_create_customer(
        test_db,
        name="Rahul",
        phone="7777777777",
        business_id=business.business_id
    )

    test_db.commit()

    customer_2 = get_or_create_customer(
        test_db,
        name="Rahul Updated",
        phone="7777777777",
        business_id=business.business_id
    )

    test_db.commit()

    assert customer_1.customer_id == customer_2.customer_id