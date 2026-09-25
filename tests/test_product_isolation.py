from app.models import Business, Product
from sqlalchemy.exc import IntegrityError


def test_same_product_id_allowed_for_different_businesses(test_db):
    # Create two retailers
    business_a = Business(
        supabase_user_id="product-user-a",
        business_name="Retailer A"
    )

    business_b = Business(
        supabase_user_id="product-user-b",
        business_name="Retailer B"
    )

    test_db.add_all([business_a, business_b])
    test_db.commit()

    # Both businesses use the same product ID
    product_a = Product(
        business_id=business_a.business_id,
        product_id="PROD-001",
        product_name="Rice"
    )

    product_b = Product(
        business_id=business_b.business_id,
        product_id="PROD-001",
        product_name="Rice"
    )

    test_db.add_all([product_a, product_b])
    test_db.commit()

    products = test_db.query(Product).all()

    assert len(products) == 2
    assert products[0].product_id == "PROD-001"
    assert products[1].product_id == "PROD-001"
    assert products[0].business_id != products[1].business_id


def test_same_product_id_not_allowed_within_same_business(test_db):
    business = Business(
        supabase_user_id="duplicate-product-user",
        business_name="Retailer A"
    )

    test_db.add(business)
    test_db.commit()

    product_1 = Product(
        business_id=business.business_id,
        product_id="PROD-002",
        product_name="Sugar"
    )

    test_db.add(product_1)
    test_db.commit()

    # Same business + same product ID
    product_2 = Product(
        business_id=business.business_id,
        product_id="PROD-002",
        product_name="Sugar"
    )

    test_db.add(product_2)

    try:
        test_db.commit()
        assert False, "Duplicate product should not be allowed"
    except IntegrityError:
        test_db.rollback()