from fastapi import FastAPI, File, UploadFile, Depends
from datetime import datetime
from schemas import InvoiceExtraction, CustomerProfileUpdate, CopilotRequest
from groq import Groq
from config import groq_vision_model, groq_api
from models import Customer, Invoice, InvoiceItem, Product
from database import SessionLocal
from auth_backend import get_current_user_id
from ai_helper import generate_prediction_message, generate_whatsapp_message
from copiloit import copilot
import base64

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
    get_inventory_signals,
    get_or_create_business
)

client = Groq(api_key=groq_api)

app = FastAPI()


# ============================================================
# UPLOAD INVOICE
# ============================================================

@app.post("/upload-invoice")
async def upload_invoice(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id)
):
    db = SessionLocal()

    try:
        business = get_or_create_business(db, user_id)

        image_bytes = await file.read()
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
            invoiceExtraction = InvoiceExtraction.model_validate_json(
                json_data
            )

            parsed_date = None

            if invoiceExtraction.date:
                try:
                    parsed_date = datetime.strptime(
                        invoiceExtraction.date,
                        "%d-%m-%Y"
                    ).date()
                except ValueError:
                    parsed_date = None

            customer = get_or_create_customer(
                db,
                invoiceExtraction.customer_name,
                invoiceExtraction.customer_phone,
                business.business_id
            )

            needs_profile = customer.customer_type is None

            items = []

            for item in invoiceExtraction.items:

                product = get_or_create_product(
                    db,
                    item.product_name,
                    business.business_id
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
                parsed_date,
                invoiceExtraction.total_amount,
                invoiceExtraction.paid_amount,
                invoiceExtraction.credit_amount,
                business.business_id
            )

            # Check whether this invoice already has items
            existing_items = db.query(InvoiceItem).filter(
                InvoiceItem.invoice_id == invoice.invoice_id
            ).first()

            if existing_items:
                return {
                    "message": "This invoice was already processed earlier",
                    "invoice_id": invoice.invoice_id,
                    "customer_id": customer.customer_id,
                    "needs_profile_questions": needs_profile
                }

            create_invoice_items(
                db,
                invoice.invoice_id,
                items,
                business.business_id
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

    finally:
        db.close()


# ============================================================
# UPDATE CUSTOMER PROFILE
# ============================================================

@app.post("/update-customer-profile")
def update_profile(
    data: CustomerProfileUpdate,
    user_id: str = Depends(get_current_user_id)
):
    db = SessionLocal()

    try:
        business = get_or_create_business(db, user_id)

        customer = update_customer_profile(
            db,
            data.customer_id,
            data.customer_type,
            data.bargains,
            data.payment_mode,
            data.preference_tier,
            data.buying_behavior,
            data.free_note,
            business.business_id
        )

        if customer is None:
            return {"error": "Customer not found"}

        return {
            "message": "Customer profile updated",
            "customer_id": customer.customer_id
        }

    finally:
        db.close()


# ============================================================
# CUSTOMER SEARCH
# ============================================================

@app.get("/customer-search")
def customer_search(
    phone: str = None,
    name: str = None,
    user_id: str = Depends(get_current_user_id)
):
    db = SessionLocal()

    try:
        business = get_or_create_business(db, user_id)

        query = db.query(Customer).filter(
            Customer.business_id == business.business_id
        )

        if phone:
            query = query.filter(
                Customer.phone == phone
            )

        elif name:
            query = query.filter(
                Customer.name.ilike(f"%{name}%")
            )

        else:
            return {"error": "Enter customer name or phone number"}

        customers = query.all()

        return [
            {
                "customer_id": customer.customer_id,
                "name": customer.name,
                "phone": customer.phone
            }
            for customer in customers
        ]

    finally:
        db.close()


# ============================================================
# CUSTOMER PROFILE
# ============================================================

@app.get("/customer/{customer_id}")
def customer_profile(
    customer_id: int,
    user_id: str = Depends(get_current_user_id)
):
    db = SessionLocal()

    try:
        business = get_or_create_business(db, user_id)

        profile = get_customer_profile(
            db,
            customer_id,
            business.business_id
        )

        if profile is None:
            return {"error": "Customer not found"}

        return profile

    finally:
        db.close()


# ============================================================
# CUSTOMER PREDICTION
# ============================================================

@app.get("/customer/{customer_id}/prediction")
def get_prediction(
    customer_id: int,
    user_id: str = Depends(get_current_user_id)
):
    db = SessionLocal()

    try:
        business = get_or_create_business(db, user_id)

        prediction = predict_next_purchase(
            db,
            customer_id,
            business.business_id
        )

        if prediction["status"] == "not_enough_data":
            return prediction

        message = generate_prediction_message(
            prediction["average_interval"],
            prediction["days_since_last_bought"],
            prediction["status"]
        )

        prediction["message"] = message

        return prediction

    except Exception as e:
        return {"error": str(e)}

    finally:
        db.close()


# ============================================================
# NEXT BEST ACTION
# ============================================================

@app.get("/customer/{customer_id}/next-best-action")
def next_best_action(
    customer_id: int,
    user_id: str = Depends(get_current_user_id)
):
    db = SessionLocal()

    try:
        business = get_or_create_business(db, user_id)

        prediction = predict_next_purchase(
            db,
            customer_id,
            business.business_id
        )

        if prediction["status"] == "not_enough_data":
            return prediction

        action = get_next_best_action(
            prediction["status"]
        )

        result = {
            "status": prediction["status"],
            "action": action
        }

        if prediction["status"] in ["overdue", "approaching"]:

            profile = get_customer_profile(
                db,
                customer_id,
                business.business_id
            )

            if profile is None:
                return {"error": "Customer not found"}

            customer_name = profile["customer"]["name"]

            favorite_product = (
                profile["favorite_products"][0]["product_name"]
                if profile["favorite_products"]
                else "their usual items"
            )

            message = generate_whatsapp_message(
                customer_name,
                favorite_product,
                prediction["status"]
            )

            result["whatsapp_message"] = message

        return result

    except Exception as e:
        return {"error": str(e)}

    finally:
        db.close()


# ============================================================
# BUSINESS DASHBOARD
# ============================================================

@app.get("/dashboard")
def dashboard(
    user_id: str = Depends(get_current_user_id)
):
    db = SessionLocal()

    try:
        business = get_or_create_business(db, user_id)

        summary = get_business_dashboard(
            db,
            business.business_id
        )

        hero_products = get_hero_products(
            db,
            business.business_id
        )

        weak_products = get_weak_products(
            db,
            business.business_id
        )

        return {
            "summary": summary,
            "hero_products": hero_products,
            "weak_products": weak_products
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        db.close()


# ============================================================
# COPILOT GET
# ============================================================

@app.get("/copilot")
def test_copilot(
    question: str,
    user_id: str = Depends(get_current_user_id)
):
    db = SessionLocal()

    try:
        business = get_or_create_business(db, user_id)

        return copilot(
            question,
            db,
            business.business_id
        )

    finally:
        db.close()


# ============================================================
# CREDIT OVERVIEW
# ============================================================

@app.get("/credit-overview")
def credit_overview(
    user_id: str = Depends(get_current_user_id)
):
    db = SessionLocal()

    try:
        business = get_or_create_business(db, user_id)

        return get_credit_overview(
            db,
            business.business_id
        )

    except Exception as e:
        return {"error": str(e)}

    finally:
        db.close()


# ============================================================
# PRODUCT BUNDLES
# ============================================================

@app.get("/product-bundles")
def product_bundles(
    user_id: str = Depends(get_current_user_id)
):
    db = SessionLocal()

    try:
        business = get_or_create_business(db, user_id)

        return get_product_bundles(
            db,
            business.business_id
        )

    except Exception as e:
        return {"error": str(e)}

    finally:
        db.close()


# ============================================================
# INVENTORY SIGNALS
# ============================================================

@app.get("/inventory-signals")
def inventory_signals(
    user_id: str = Depends(get_current_user_id)
):
    db = SessionLocal()

    try:
        business = get_or_create_business(db, user_id)

        return get_inventory_signals(
            db,
            business.business_id
        )

    except Exception as e:
        return {"error": str(e)}

    finally:
        db.close()


# ============================================================
# COPILOT POST
# ============================================================

@app.post("/copilot")
def copilot_route(
    data: CopilotRequest,
    user_id: str = Depends(get_current_user_id)
):
    db = SessionLocal()

    try:
        business = get_or_create_business(db, user_id)

        return copilot(
            data.question,
            db,
            business.business_id,
            data.history
        )

    finally:
        db.close()