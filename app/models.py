from database import Base
from sqlalchemy import Column , Integer, String, Text , Date,DECIMAL,TIMESTAMP,ForeignKey
from sqlalchemy import func , DateTime

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    phone = Column(String(15))
    location = Column(Text)
    customer_type = Column(String(20))
    bargains = Column(String(20))
    payment_mode = Column(String(20))
    preference_tier = Column(String(20))
    buying_behavior = Column(String(30))
    free_note = Column(Text)
    ai_summary = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class Invoice(Base):
    __tablename__ = "invoices"
    invoice_id = Column(String(10) , primary_key=True)
    customer_id = Column(Integer,ForeignKey("customers.customer_id"))
    invoice_date = Column(Date)
    total_amount = Column(DECIMAL(10,2))
    paid_amount = Column(DECIMAL(10,2))
    credit_amount = Column(DECIMAL(10,2))
    invoice_image = Column(Text)

class Product(Base):
    __tablename__ = "products"
    product_id = Column(String(10),primary_key=True)
    product_name = Column(String(150))
    category = Column(String(20))
    other_product_info = Column(Text)

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    invoice_id = Column(String(10), ForeignKey("invoices.invoice_id"), primary_key=True)
    product_id = Column(String(10), ForeignKey("products.product_id"), primary_key=True)
    quantity = Column(Integer)
    unit_price = Column(DECIMAL(10, 2))
    total_price = Column(DECIMAL(10, 2))
