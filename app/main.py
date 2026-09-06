from fastapi import FastAPI , File, UploadFile
from schemas import InvoiceExtraction , CustomerProfileUpdate,CopilotRequest
from groq import Groq
from config import groq_vision_model, groq_api
from models import Customer, Invoice, InvoiceItem ,Product
from database import SessionLocal
from crud import predict_next_purchase
from copiloit import copilot
from ai_helper import generate_prediction_message,generate_whatsapp_message
from crud import (
    get_or_create_customer,
    get_or_create_product,
    create_invoice,
    create_invoice_items,
    update_customer_profile,
    get_customer_profile,
    predict_next_purchase,
    get_next_best_action,
    get_business_dashboard,
    get_hero_products,
    get_weak_products,
    get_credit_overview,
    get_product_bundles,
    get_inventory_signals
)
import base64
client = Groq(api_key=groq_api)
app = FastAPI()
@app.post("/upload-invoice")
async def uplaod_invoice(file:UploadFile= File(...)):
    image_bytes  =  await file.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    response = client.chat.completions.create(
    model=groq_vision_model,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Extract invoice details from this image. Return ONLY valid JSON with these exact fields: invoice_id, date, customer_name, customer_phone, items (list of objects with product_name, quantity, unit_price, total_price), total_amount, paid_amount, credit_amount. No explanation, no markdown, just raw JSON."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
         }
        ]
    )

    json_data = response.choices[0].message.content
    try:
        invoiceExtraction = InvoiceExtraction.model_validate_json(json_data)
        db = SessionLocal()

        customer = get_or_create_customer(
            db,
            invoiceExtraction.customer_name,
            invoiceExtraction.customer_phone
        )
        needs_profile = customer.customer_type is None
        items = []
        for item in invoiceExtraction.items:

            product = get_or_create_product(
                db,
                item.product_name
            )

            items.append({
                "product_id": product.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price
            }) 
        invoice = create_invoice(
            db,
            customer.customer_id,
            invoiceExtraction.invoice_id,
            invoiceExtraction.date,
            invoiceExtraction.total_amount,
            invoiceExtraction.paid_amount,
            invoiceExtraction.credit_amount
        )
        # Check if this invoice_id already had items saved
        existing_items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.invoice_id).first()

        if existing_items:
            return {
                "message": "This invoice was already processed earlier",
                "invoice_id": invoice.invoice_id,
                "customer_id": customer.customer_id,
                "needs_profile_questions": needs_profile
            }

        # 9. Create invoice items
        create_invoice_items(
            db,
            invoice.invoice_id,
            items
        )
        return {
            "message": "Invoice saved successfully",
            "invoice_id": invoice.invoice_id,
            "customer_id": customer.customer_id,
            "needs_profile_questions": needs_profile
        }
        
    except Exception as e:
        print("Validation failed:")
        return {"error": str(e)}

@app.post("/update-customer-profile")
def update_profile(data:CustomerProfileUpdate):
    db = SessionLocal()
    customer = update_customer_profile(
        db,
        data.customer_id,
        data.customer_type,
        data.bargains,
        data.payment_mode,
        data.preference_tier,
        data.buying_behavior,
        data.free_note
    )
    return {
        "message": "Customer profile updated",
        "customer_id": customer.customer_id
    }

@app.get("/customer/{customer_id}")
def customer_profile(customer_id: int):

    db = SessionLocal()

    profile = get_customer_profile(db, customer_id)

    if profile is None:
        return {"error": "Customer not found"}

    return profile

@app.get("/customer/{customer_id}/prediction")
def get_prediction(customer_id:int):
    db = SessionLocal()
    prediction = predict_next_purchase(db,customer_id)
    try:
        if prediction["status"] == "not_enough_data":
            return prediction
        
        else:
            message = generate_prediction_message(
                prediction["average_interval"],
                prediction["days_since_last_bought"],
                prediction["status"]
            )
            prediction["message"] = message

        return prediction
    
    except Exception as e:
        return {"error": str(e)}

@app.get("/customer/{customer_id}/next-best-action")
def next_best_action(customer_id:int):
    db = SessionLocal()
    try:
        prediction = predict_next_purchase(db, customer_id)

        if(prediction["status"] == "not_enough_data"):
            return prediction

        action = get_next_best_action(prediction["status"])
        result = {
            "status": prediction["status"],
            "action": action
        }
        if prediction["status"] in ["overdue", "approaching"]:
            profile = get_customer_profile(db, customer_id)
            customer_name = profile["customer"]["name"]
            favorite_product = profile["favorite_products"][0]["product_name"] if profile["favorite_products"] else "their usual items"

            message = generate_whatsapp_message(customer_name, favorite_product, prediction["status"])
            result["whatsapp_message"] = message

        return result

    except Exception as e:
        return{"error":str(e)}

@app.get("/dashboard")
def dashboard():
    db = SessionLocal()
    try:
        summary = get_business_dashboard(db)
        hero_products = get_hero_products(db)
        weak_products = get_weak_products(db)

        return {
            "summary": summary,
            "hero_products": hero_products,
            "weak_products": weak_products
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/copilot")
def test_copilot(question: str):
    db = SessionLocal()

    try:
        
            return copilot(question, db)
        
    finally:
        db.close()


@app.get("/credit-overview")
def credit_overview():
    db = SessionLocal()
    try:
        return get_credit_overview(db)
    except Exception as e:
        return {"error": str(e)}

@app.get("/product-bundles")
def product_bundles():
    db = SessionLocal()
    try:
        return get_product_bundles(db)
    except Exception as e:
        return {"error": str(e)}

@app.get("/inventory-signals")
def inventory_signals():
    db = SessionLocal()
    try:
        return get_inventory_signals(db)
    except Exception as e:
        return {"error": str(e)}

@app.post("/copilot")
def copilot_route(data: CopilotRequest):
    db = SessionLocal()
    try:
        return copilot(data.question, db, data.history)
    finally:
        db.close()