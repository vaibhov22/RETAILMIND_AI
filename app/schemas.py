from pydantic import BaseModel
from typing import Optional, List
class InvoiceItem(BaseModel):
    product_name:str
    quantity:int
    unit_price:int
    total_price:int

class InvoiceExtraction(BaseModel):
    invoice_id:Optional[str]
    date:Optional[str]
    customer_name:Optional[str]
    customer_phone:Optional[str]
    items:list[InvoiceItem]
    total_amount:float
    paid_amount:Optional[float]
    credit_amount:Optional[float]

class CustomerProfileUpdate(BaseModel):
    customer_id: int
    customer_type: str
    bargains: str
    payment_mode: str
    preference_tier: str
    buying_behavior: str
    free_note: Optional[str] = None

class CopilotRequest(BaseModel):
    question: str
    history: list = []