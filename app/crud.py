
from models import Customer,Product,InvoiceItem,Invoice,Business
from database import SessionLocal
from sqlalchemy import func
from datetime import date
def get_or_create_customer(db, name, phone,business_id):

    customer = db.query(Customer).filter(
        Customer.phone == phone,
        Customer.business_id == business_id
    ).first()

    if customer:
        return customer

    customer = Customer(
        name=name,
        phone=phone,
        business_id=business_id
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer
def get_or_create_product(db, product_name, business_id):
    product = db.query(Product).filter(
        Product.product_name == product_name,
        Product.business_id == business_id
    ).first()

    if product:
        return product

    count = db.query(Product).filter(Product.business_id == business_id).count()
    new_id = f"P{count+1:04d}"

    product = Product(product_id=new_id, product_name=product_name, business_id=business_id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def create_invoice(db, customer_id, invoice_id, date, total_amount, paid_amount, credit_amount, business_id):
    if invoice_id is None:
        count = db.query(Invoice).filter(Invoice.business_id == business_id).count()
        invoice_id = f"INV-AUTO-{count+1:04d}"
    else:
        existing = db.query(Invoice).filter(
            Invoice.invoice_id == invoice_id,
            Invoice.business_id == business_id
        ).first()
        if existing:
            return existing

    invoice = Invoice(
        invoice_id=invoice_id,
        customer_id=customer_id,
        invoice_date=date,
        total_amount=total_amount,
        paid_amount=paid_amount,
        credit_amount=credit_amount,
        business_id=business_id
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice
def create_invoice_items(db, invoice_id, items_with_product_ids, business_id):
    for item in items_with_product_ids:
        invoiceItem = InvoiceItem(
            invoice_id=invoice_id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            total_price=item["total_price"],
            business_id=business_id
        )
        db.add(invoiceItem)

    db.commit()
    return True

def update_customer_profile(db, customer_id, customer_type, bargains, payment_mode, preference_tier, buying_behavior, free_note):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()

    customer.customer_type = customer_type
    customer.bargains = bargains
    customer.payment_mode = payment_mode
    customer.preference_tier = preference_tier
    customer.buying_behavior = buying_behavior
    customer.free_note = free_note

    db.commit()
    db.refresh(customer)
    return customer

def get_customer_profile(db,customer_id):
    customer = db.query(Customer).filter(
    Customer.customer_id == customer_id
    ).first()

    if customer is None:
        return None
    order_count = db.query(
    func.count(Invoice.invoice_id)
            ).filter(
                Invoice.customer_id == customer_id
            ).scalar() or 0
    total_spend = db.query(
    func.sum(Invoice.total_amount)
        ).filter(
            Invoice.customer_id == customer_id
        ).scalar() or 0
    last_purchase = db.query(
    func.max(Invoice.invoice_date)
        ).filter(
            Invoice.customer_id == customer_id
        ).scalar() or 0 
    average_order_value = total_spend / order_count if order_count else 0

    outstanding_credit = db.query(
    func.sum(Invoice.credit_amount)
        ).filter(
            Invoice.customer_id == customer_id
        ).scalar() or 0
    favorite_products = db.query(
    Product.product_name,
    func.sum(InvoiceItem.quantity).label("total_quantity")
    ).join(
        InvoiceItem,
        Product.product_id == InvoiceItem.product_id
    ).join(
        Invoice,
        Invoice.invoice_id == InvoiceItem.invoice_id
    ).filter(
        Invoice.customer_id == customer_id
    ).group_by(
        Product.product_name
    ).order_by(
        func.sum(InvoiceItem.quantity).desc()
    ).all()
    return {
    "customer": {
        "customer_id": customer.customer_id,
        "name": customer.name,
        "phone": customer.phone,
        "location": customer.location,
        "customer_type": customer.customer_type,
        "bargains": customer.bargains,
        "payment_mode": customer.payment_mode,
        "preference_tier": customer.preference_tier,
        "buying_behavior": customer.buying_behavior,
        "free_note": customer.free_note
    },
    "order_count": order_count,
    "total_spend": total_spend,
    "average_order_value": average_order_value,
    "last_purchase": last_purchase,
    "outstanding_credit": outstanding_credit,
    "favorite_products": [
        {
            "product_name": product.product_name,
            "total_quantity": product.total_quantity
        }
        for product in favorite_products
    ]
}

def predict_next_purchase(db,customer_id):
    dates = [row[0] for row in db.query(Invoice.invoice_date).filter(Invoice.customer_id == customer_id).order_by(Invoice.invoice_date).all()]
    if len(dates) < 2:
        return {"status": "not_enough_data"}
    gaps = []
    for i in range(0,len(dates)-1):
        gap = (dates[i+1] - dates[i]).days
        gaps.append(gap)
    sum_of_gap = 0
    for gap in gaps:
        sum_of_gap+=gap

    average_interval = sum_of_gap / len(gaps)
    days_since_last_bought = (date.today() - dates[-1]).days
    status = ""
    if days_since_last_bought >= average_interval:
        status = "overdue"
    elif days_since_last_bought>=average_interval*0.8:
        status = "approaching"
    else:
        status = "not due yet"

    return {
     "average_interval" : average_interval,
     "days_since_last_bought" : days_since_last_bought,
      "status" : status
    }

    
def get_next_best_action(status):
    if status == "overdue":
        return "Send whatsapp reminder - customer is overdue for their usual purchase"
    elif status == "approaching":
        return "Consider sending a gentle reminder — customer's usual purchase window is approaching"
    elif status == "not due yet":
        return "No action needed right now"
    else:
        return "Not enough data to recommend an action"
    

def get_business_dashboard(db):
    total_revenue = db.query(func.sum(Invoice.total_amount)).scalar() or 0
    total_orders = db.query(func.count(Invoice.invoice_id)).scalar() or 0
    total_customers = db.query(func.count(Customer.customer_id)).scalar() or 0
    if total_orders != 0:
        average_order_value = total_revenue / total_orders 
    else:
        average_order_value = 0

    return {
        "total_revenue" : total_revenue,
        "total_orders" : total_orders,
        "total_customers" : total_customers,
        "average_order_value" : average_order_value

    }

def get_hero_products(db):
    hero_products = db.query(
    Product.product_name,
    func.sum(InvoiceItem.total_price).label("total_revenue")
    ).join(
        InvoiceItem,
        Product.product_id == InvoiceItem.product_id
    ).group_by(
        Product.product_name
    ).order_by(
        func.sum(InvoiceItem.total_price).desc()
    ).limit(3).all()
    return [
        {"product_name": p.product_name, "total_revenue": p.total_revenue}
        for p in hero_products
    ]

def get_weak_products(db):
    weak_products = db.query(
    Product.product_name,
    func.sum(InvoiceItem.total_price).label("total_revenue")
    ).join(
        InvoiceItem,
        Product.product_id == InvoiceItem.product_id
    ).group_by(
        Product.product_name
    ).order_by(
        func.sum(InvoiceItem.total_price).asc()
    ).limit(3).all()
    return [
        {"product_name": p.product_name, "total_revenue": p.total_revenue}
        for p in weak_products
    ]
    
    
def get_credit_overview(db):
    total_outstanding = db.query(func.sum(Invoice.credit_amount)).scalar() or 0

    customers_with_credit = db.query(
        Customer.customer_id,
        Customer.name,
        Customer.phone,
        func.sum(Invoice.credit_amount).label("total_credit")
    ).join(
        Invoice,
        Customer.customer_id == Invoice.customer_id
    ).group_by(
        Customer.customer_id, Customer.name, Customer.phone
    ).having(
        func.sum(Invoice.credit_amount) > 0
    ).order_by(
        func.sum(Invoice.credit_amount).desc()
    ).all()

    return {
        "total_outstanding": total_outstanding,
        "customers": [
            {
                "customer_id": c.customer_id,
                "name": c.name,
                "phone": c.phone,
                "total_credit": c.total_credit
            }
            for c in customers_with_credit
        ]
    }

def get_product_bundles(db):
    all_items = db.query(InvoiceItem.invoice_id, InvoiceItem.product_id).all()

    invoice_products = {}
    for invoice_id, product_id in all_items:
        if invoice_id not in invoice_products:
            invoice_products[invoice_id] = []
        invoice_products[invoice_id].append(product_id)

    pair_counts = {}
    for invoice_id, product_ids in invoice_products.items():
        unique_products = list(set(product_ids))
        for i in range(len(unique_products)):
            for j in range(i + 1, len(unique_products)):
                pair = tuple(sorted([unique_products[i], unique_products[j]]))
                pair_counts[pair] = pair_counts.get(pair, 0) + 1

    sorted_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)
    top_pairs = sorted_pairs[:5]

    result = []
    for (product_id_1, product_id_2), count in top_pairs:
        product_1 = db.query(Product).filter(Product.product_id == product_id_1).first()
        product_2 = db.query(Product).filter(Product.product_id == product_id_2).first()
        result.append({
            "product_1": product_1.product_name,
            "product_2": product_2.product_name,
            "times_bought_together": count
        })

    return result

from datetime import timedelta

def get_inventory_signals(db, days=30):
    cutoff_date = date.today() - timedelta(days=days)

    recent_sales = db.query(
        Product.product_name,
        func.sum(InvoiceItem.quantity).label("units_sold")
    ).join(
        InvoiceItem,
        Product.product_id == InvoiceItem.product_id
    ).join(
        Invoice,
        Invoice.invoice_id == InvoiceItem.invoice_id
    ).filter(
        Invoice.invoice_date >= cutoff_date
    ).group_by(
        Product.product_name
    ).order_by(
        func.sum(InvoiceItem.quantity).desc()
    ).limit(5).all()

    return [
        {"product_name": p.product_name, "units_sold_recently": p.units_sold}
        for p in recent_sales
    ]

def get_or_create_business(db, supabase_user_id, business_name=None):
    business = db.query(Business).filter(
        Business.supabase_user_id == supabase_user_id
    ).first()

    if business:
        return business

    business = Business(
        supabase_user_id=supabase_user_id,
        business_name=business_name
    )
    db.add(business)
    db.commit()
    db.refresh(business)

    return business