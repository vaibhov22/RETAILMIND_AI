from groq import Groq
from config import groq_api, groq_vision_model
import base64
from schemas import InvoiceExtraction,InvoiceItem

client = Groq(api_key=groq_api)

with open("sample_invoice.png", "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode("utf-8")

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
    print(invoiceExtraction)
except Exception as e:
    print("Validation failed:")
    print(e)


