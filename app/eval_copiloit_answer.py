import json
from groq import Groq
from config import groq_api

client = Groq(api_key=groq_api)

golden_dataset = [
    {"question": "What is my total revenue?", "tool_result": {"total_revenue": 935, "total_orders": 1, "total_customers": 1, "average_order_value": 935}, "expected_facts": ["revenue is 935", "currency is rupees"]},
    {"question": "How many orders have I received?", "tool_result": {"total_orders": 1}, "expected_facts": ["orders is 1"]},
    {"question": "How many customers do I have?", "tool_result": {"total_customers": 1}, "expected_facts": ["customers is 1"]},
    {"question": "Which products are selling the most?", "tool_result": [{"product_name": "Aashirvaad Atta", "total_quantity": 10, "total_sales": 2750}, {"product_name": "Fortune Oil", "total_quantity": 8, "total_sales": 1200}], "expected_facts": ["Aashirvaad Atta is the strongest product", "Aashirvaad Atta sales are 2750 rupees"]},
    {"question": "Which products are selling poorly?", "tool_result": [{"product_name": "Tata Salt", "total_quantity": 1, "total_sales": 25}, {"product_name": "Parle-G", "total_quantity": 2, "total_sales": 20}], "expected_facts": ["Tata Salt is a weak product", "Parle-G is a weak product"]},
    {"question": "How much has customer 1 spent?", "tool_result": {"customer": {"name": "Rohit Verma"}, "order_count": 3, "total_spend": 1500, "outstanding_credit": 200}, "expected_facts": ["customer spent 1500 rupees", "customer is Rohit Verma"]},
    {"question": "What is customer 1's outstanding credit?", "tool_result": {"outstanding_credit": 200}, "expected_facts": ["outstanding credit is 200 rupees"]},
    {"question": "When will customer 1 buy again?", "tool_result": {"predicted_next_purchase_days": 12, "predicted_next_purchase_date": "2026-09-13"}, "expected_facts": ["next purchase is predicted in 12 days", "predicted date is 2026-09-13"]},
    {"question": "Which are my best and worst-performing products?", "tool_result": {"hero_products": [{"product_name": "Aashirvaad Atta", "total_sales": 2750}], "weak_products": [{"product_name": "Parle-G", "total_sales": 20}]}, "expected_facts": ["Aashirvaad Atta is a best-performing product", "Parle-G is a weak product"]},
    {"question": "Tell me about customer 1 and predict when they will buy again.", "tool_result": {"customer": {"name": "Rohit Verma", "total_spend": 1500, "outstanding_credit": 200}, "prediction": {"predicted_next_purchase_days": 12, "predicted_next_purchase_date": "2026-09-13"}}, "expected_facts": ["customer is Rohit Verma", "customer spent 1500 rupees", "outstanding credit is 200 rupees", "next purchase is predicted in 12 days"]}
]

def generate_answer(question, tool_result):
    messages = [
        {"role": "system", "content": "You are a retail business assistant. Answer using ONLY the supplied tool result. Do not invent facts. All monetary values are Indian Rupees (₹). Be concise and directly answer the question."},
        {"role": "user", "content": question},
        {"role": "user", "content": "Tool result: " + json.dumps(tool_result, default=str)}
    ]
    response = client.chat.completions.create(model="openai/gpt-oss-120b", messages=messages)
    return response.choices[0].message.content

def judge_answer(question, tool_result, expected_facts, answer):
    prompt = f"""Evaluate this Copilot answer.

Question: {question}
Tool result: {json.dumps(tool_result, default=str)}
Expected facts: {json.dumps(expected_facts)}
Copilot answer: {answer}

Return ONLY valid JSON with:
factual_correctness: 1 or 0
relevance: 1 or 0
hallucination_free: 1 or 0
rupee_correctness: 1 or 0
overall: 1 only if all four are 1, otherwise 0"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "You are a strict evaluation judge. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
    )
    try:
        return json.loads(response.choices[0].message.content.strip())
    except Exception:
        return {"factual_correctness": 0, "relevance": 0, "hallucination_free": 0, "rupee_correctness": 0, "overall": 0}

def run_eval():
    print("=" * 60)
    print("RETAILMIND AI — COPILOT ANSWER QUALITY EVAL")
    print("=" * 60)

    results = []

    for i, test in enumerate(golden_dataset, 1):
        print(f"\nTest {i}: {test['question']}")
        try:
            answer = generate_answer(test["question"], test["tool_result"])
            scores = judge_answer(test["question"], test["tool_result"], test["expected_facts"], answer)
            results.append(scores)
            print("  " + ("✅" if scores["overall"] else "❌"))
            print(f"  Answer: {answer}")
            print(f"  Scores: Factual={scores['factual_correctness']}, Relevance={scores['relevance']}, Hallucination-Free={scores['hallucination_free']}, Rupee={scores['rupee_correctness']}")
        except Exception as e:
            print(f"  ⚠️ FAILED: {e}")

    if not results:
        return

    total = len(results)
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for label, key in [
        ("Overall Answer Quality", "overall"),
        ("Factual Correctness", "factual_correctness"),
        ("Relevance", "relevance"),
        ("Hallucination-Free", "hallucination_free"),
        ("Rupee Correctness", "rupee_correctness")
    ]:
        score = sum(r[key] for r in results)
        print(f"{label}: {score / total * 100:.1f}% ({score}/{total})")

if __name__ == "__main__":
    run_eval()
