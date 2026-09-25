from app.models import Business, Invoice, Product, InvoiceItem
from sqlalchemy.exc import IntegrityError


def test_same_product_and_invoice_allowed_for_different_businesses(test_db):
    # Create two retailers
    business_a = Business(
        supabase_user_id="item-user-a",
        business_name="Retailer A"
    )

    business_b = Business(
        supabase_user_id="item-user-b",
        business_name="Retailer B"
    )

    test_db.add_all([business_a, business_b])
    test_db.commit()

    # Same invoice ID and product ID for both businesses
    invoice_a = Invoice(
        business_id=business_a.business_id,
        invoice_id="INV-ITEM-001",
        total_amount=1000
    )

    invoice_b = Invoice(
        business_id=business_b.business_id,
        invoice_id="INV-ITEM-001",
        total_amount=2000
    )

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

    test_db.add_all([
        invoice_a,
        invoice_b,
        product_a,
        product_b
    ])
    test_db.commit()

    # Same invoice_id + product_id, but different businesses
    item_a = InvoiceItem(
        business_id=business_a.business_id,
        invoice_id="INV-ITEM-001",
        product_id="PROD-001",
        quantity=10,
        unit_price=100,
        total_price=1000
    )

    item_b = InvoiceItem(
        business_id=business_b.business_id,
        invoice_id="INV-ITEM-001",
        product_id="PROD-001",
        quantity=20,
        unit_price=100,
        total_price=2000
    )

    test_db.add_all([item_a, item_b])
    test_db.commit()

    items = test_db.query(InvoiceItem).all()

    assert len(items) == 2
    assert items[0].business_id != items[1].business_id


def test_same_invoice_product_not_allowed_within_same_business(test_db):
    business = Business(
        supabase_user_id="duplicate-item-user",
        business_name="Retailer A"
    )

    test_db.add(business)
    test_db.commit()

    invoice = Invoice(
        business_id=business.business_id,
        invoice_id="INV-ITEM-002",
        total_amount=1000
    )

    product = Product(
        business_id=business.business_id,
        product_id="PROD-002",
        product_name="Sugar"
    )

    test_db.add_all([invoice, product])
    test_db.commit()

    item_1 = InvoiceItem(
        business_id=business.business_id,
        invoice_id="INV-ITEM-002",
        product_id="PROD-002",
        quantity=10,
        unit_price=50,
        total_price=500
    )

    test_db.add(item_1)
    test_db.commit()

    # Exact same business + invoice + product
    item_2 = InvoiceItem(
        business_id=business.business_id,
        invoice_id="INV-ITEM-002",
        product_id="PROD-002",
        quantity=20,
        unit_price=50,
        total_price=1000
    )

    test_db.add(item_2)

    try:
        test_db.commit()
        assert False, "Duplicate invoice item should not be allowed"
    except IntegrityError:
        test_db.rollback()