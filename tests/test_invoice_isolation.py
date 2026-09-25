from app.models import Business, Invoice
from sqlalchemy.exc import IntegrityError


def test_same_invoice_id_allowed_for_different_businesses(test_db):
    # Create two retailers
    business_a = Business(
        supabase_user_id="invoice-user-a",
        business_name="Retailer A"
    )

    business_b = Business(
        supabase_user_id="invoice-user-b",
        business_name="Retailer B"
    )

    test_db.add_all([business_a, business_b])
    test_db.commit()

    # Retailer A creates INV-001
    invoice_a = Invoice(
        business_id=business_a.business_id,
        invoice_id="INV-001",
        total_amount=1000
    )

    test_db.add(invoice_a)
    test_db.commit()

    # Retailer B creates the SAME invoice ID
    invoice_b = Invoice(
        business_id=business_b.business_id,
        invoice_id="INV-001",
        total_amount=2000
    )

    test_db.add(invoice_b)
    test_db.commit()

    invoices = test_db.query(Invoice).all()

    assert len(invoices) == 2
    assert invoices[0].invoice_id == "INV-001"
    assert invoices[1].invoice_id == "INV-001"
    assert invoices[0].business_id != invoices[1].business_id


def test_same_invoice_id_not_allowed_within_same_business(test_db):
    business = Business(
        supabase_user_id="duplicate-user",
        business_name="Retailer A"
    )

    test_db.add(business)
    test_db.commit()

    invoice_1 = Invoice(
        business_id=business.business_id,
        invoice_id="INV-002",
        total_amount=1000
    )

    test_db.add(invoice_1)
    test_db.commit()

    # Same business + same invoice ID
    invoice_2 = Invoice(
        business_id=business.business_id,
        invoice_id="INV-002",
        total_amount=2000
    )

    test_db.add(invoice_2)

    try:
        test_db.commit()
        assert False, "Duplicate invoice should not be allowed"
    except IntegrityError:
        test_db.rollback()