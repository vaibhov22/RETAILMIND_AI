import base64
from groq import Groq
from config import groq_api, groq_vision_model
from schemas import InvoiceExtraction

client = Groq(api_key=groq_api)


# ============================================================
# GOLDEN DATASET
# ============================================================

golden_dataset = [
    {
        "image_path": "Enterprise_Grocery_Bill.jpg",
        "ground_truth": {
            "invoice_id": "S01",
            "date": "11 August 2023",
            "customer_name": "Sampath singh",
            "customer_phone": "9981028177",
            "total_amount": 1055.0,
            "paid_amount": 500.0,
            "credit_amount": 555.0,

            "items": [
                {
                    "product_name": "Apple normal",
                    "quantity": 5,
                    "unit_price": 100,
                    "total_price": 525
                },
                {
                    "product_name": "Orange",
                    "quantity": 10,
                    "unit_price": 40,
                    "total_price": 420
                },
                {
                    "product_name": "Banana",
                    "quantity": 5,
                    "unit_price": 40,
                    "total_price": 210
                }
            ]
        }
    }
]

# ============================================================
# EXTRACTION
# ============================================================

def extract_invoice(image_path):

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model=groq_vision_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
Extract invoice details from this image.

Return ONLY valid JSON with these exact fields:

invoice_id,
date,
customer_name,
customer_phone,
items,
total_amount,
paid_amount,
credit_amount.

For each item return:

product_name,
quantity,
unit_price,
total_price.

For quantity, return only the numeric quantity.
For example, if the invoice says "5 KG", return 5.

No explanation.
No markdown.
Return only raw JSON.
"""
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

    extracted = InvoiceExtraction.model_validate_json(json_data)

    print("EXTRACTED PHONE:", extracted.customer_phone)

    return extracted


# ============================================================
# SCORING
# ============================================================

def score_extraction(extracted, ground_truth):

    results = {}

    # -------------------------
    # Invoice-level fields
    # -------------------------

    results["invoice_id"] = (
        extracted.invoice_id == ground_truth["invoice_id"]
    )

    results["date"] = (
        extracted.date == ground_truth["date"]
    )

    results["customer_name"] = (
        extracted.customer_name == ground_truth["customer_name"]
    )

    extracted_phone_digits = "".join(
        filter(str.isdigit, extracted.customer_phone or "")
    )

    expected_phone_digits = "".join(
        filter(str.isdigit, ground_truth["customer_phone"])
    )

    results["customer_phone"] = (
        extracted_phone_digits.endswith(expected_phone_digits)
    )

    results["total_amount"] = (
        extracted.total_amount == ground_truth["total_amount"]
    )

    results["paid_amount"] = (
        extracted.paid_amount == ground_truth["paid_amount"]
    )

    results["credit_amount"] = (
        extracted.credit_amount == ground_truth["credit_amount"]
    )

    # -------------------------
    # Item count
    # -------------------------

    results["item_count"] = (
        len(extracted.items) == len(ground_truth["items"])
    )

    # -------------------------
    # Item-level evaluation
    # -------------------------

    extracted_items = extracted.items
    expected_items = ground_truth["items"]

    item_fields = [
        "product_name",
        "quantity",
        "unit_price",
        "total_price"
    ]

    for index, expected_item in enumerate(expected_items):

        if index >= len(extracted_items):

            for field in item_fields:
                results[f"item_{index + 1}_{field}"] = False

            continue

        extracted_item = extracted_items[index]

        results[f"item_{index + 1}_product_name"] = (
            extracted_item.product_name
            == expected_item["product_name"]
        )

        results[f"item_{index + 1}_quantity"] = (
            extracted_item.quantity
            == expected_item["quantity"]
        )

        results[f"item_{index + 1}_unit_price"] = (
            extracted_item.unit_price
            == expected_item["unit_price"]
        )

        results[f"item_{index + 1}_total_price"] = (
            extracted_item.total_price
            == expected_item["total_price"]
        )

    return results


# ============================================================
# RUN EVALUATION
# ============================================================

def run_eval():

    all_field_results = []

    print("=" * 60)
    print("RETAILMIND AI — EXTRACTION ACCURACY EVAL")
    print("=" * 60)

    for case in golden_dataset:

        print(f"\nTesting: {case['image_path']}")

        try:

            extracted = extract_invoice(
                case["image_path"]
            )

            field_scores = score_extraction(
                extracted,
                case["ground_truth"]
            )

            all_field_results.append(field_scores)

            for field, correct in field_scores.items():

                status = "✅" if correct else "❌"

                print(
                    f"  {status} {field}"
                )

        except Exception as e:

            print(
                f"  ⚠️  FAILED TO EXTRACT: {e}"
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if not all_field_results:
        print("No successful evaluations.")
        return

    field_names = all_field_results[0].keys()

    total_fields = 0
    correct_fields = 0

    for field in field_names:

        field_correct = sum(
            1
            for result in all_field_results
            if result[field]
        )

        field_total = len(all_field_results)

        accuracy = (
            field_correct / field_total
        ) * 100

        total_fields += field_total
        correct_fields += field_correct

        print(
            f"{field}: "
            f"{accuracy:.1f}% "
            f"({field_correct}/{field_total})"
        )

    overall_accuracy = (
        correct_fields / total_fields
    ) * 100 if total_fields else 0

    print(
        f"\nOVERALL FIELD ACCURACY: "
        f"{overall_accuracy:.1f}% "
        f"({correct_fields}/{total_fields})"
    )


if __name__ == "__main__":
    run_eval()