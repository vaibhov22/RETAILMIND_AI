import json
from groq import Groq

from config import groq_api
from tool import tools
from copiloit import available_functions


client = Groq(api_key=groq_api)


# ============================================================
# GOLDEN DATASET — COPILOT TOOL ROUTING
# ============================================================

copilot_golden_dataset = [

    # ========================================================
    # BUSINESS DASHBOARD
    # ========================================================

    {
        "question": "How is my business performing?",
        "expected_tools": ["get_business_dashboard"]
    },
    {
        "question": "What is my total revenue?",
        "expected_tools": ["get_business_dashboard"]
    },
    {
        "question": "How many orders have I received?",
        "expected_tools": ["get_business_dashboard"]
    },
    {
        "question": "How many customers do I have?",
        "expected_tools": ["get_business_dashboard"]
    },
    {
        "question": "Give me an overview of my business.",
        "expected_tools": ["get_business_dashboard"]
    },
    {
        "question": "What are my overall business numbers?",
        "expected_tools": ["get_business_dashboard"]
    },
    {
        "question": "Show me my business performance.",
        "expected_tools": ["get_business_dashboard"]
    },
    {
        "question": "How much money has my store made?",
        "expected_tools": ["get_business_dashboard"]
    },
    {
        "question": "What is my store's current performance?",
        "expected_tools": ["get_business_dashboard"]
    },
    {
        "question": "Give me my sales summary.",
        "expected_tools": ["get_business_dashboard"]
    },


    # ========================================================
    # HERO PRODUCTS
    # ========================================================

    {
        "question": "Which products are selling the most?",
        "expected_tools": ["get_hero_products"]
    },
    {
        "question": "What are my best-selling products?",
        "expected_tools": ["get_hero_products"]
    },
    {
        "question": "Which products are my heroes?",
        "expected_tools": ["get_hero_products"]
    },
    {
        "question": "Show me my top products.",
        "expected_tools": ["get_hero_products"]
    },
    {
        "question": "Which products contribute the most to sales?",
        "expected_tools": ["get_hero_products"]
    },
    {
        "question": "What should I focus on selling?",
        "expected_tools": ["get_hero_products"]
    },
    {
        "question": "Which products are performing best?",
        "expected_tools": ["get_hero_products"]
    },
    {
        "question": "Tell me my strongest products.",
        "expected_tools": ["get_hero_products"]
    },


    # ========================================================
    # WEAK PRODUCTS
    # ========================================================

    {
        "question": "Which products are selling poorly?",
        "expected_tools": ["get_weak_products"]
    },
    {
        "question": "What are my worst-performing products?",
        "expected_tools": ["get_weak_products"]
    },
    {
        "question": "Which products have weak sales?",
        "expected_tools": ["get_weak_products"]
    },
    {
        "question": "Show me products that are not selling well.",
        "expected_tools": ["get_weak_products"]
    },
    {
        "question": "Which products should I be concerned about?",
        "expected_tools": ["get_weak_products"]
    },
    {
        "question": "Tell me my weakest products.",
        "expected_tools": ["get_weak_products"]
    },
    {
        "question": "Which products have low demand?",
        "expected_tools": ["get_weak_products"]
    },
    {
        "question": "What products should I reconsider stocking?",
        "expected_tools": ["get_weak_products"]
    },


    # ========================================================
    # CUSTOMER PROFILE
    # ========================================================

    {
        "question": "Show me the profile of customer 1.",
        "expected_tools": ["get_customer_profile"]
    },
    {
        "question": "What has customer 1 purchased?",
        "expected_tools": ["get_customer_profile"]
    },
    {
        "question": "Tell me about customer 1.",
        "expected_tools": ["get_customer_profile"]
    },
    {
        "question": "How much has customer 1 spent?",
        "expected_tools": ["get_customer_profile"]
    },
    {
        "question": "What are customer 1's favorite products?",
        "expected_tools": ["get_customer_profile"]
    },
    {
        "question": "How many orders has customer 1 made?",
        "expected_tools": ["get_customer_profile"]
    },
    {
        "question": "When did customer 1 last purchase?",
        "expected_tools": ["get_customer_profile"]
    },
    {
        "question": "What is customer 1's outstanding credit?",
        "expected_tools": ["get_customer_profile"]
    },
    {
        "question": "Show me customer 1's buying behavior.",
        "expected_tools": ["get_customer_profile"]
    },
    {
        "question": "Give me all available information about customer 1.",
        "expected_tools": ["get_customer_profile"]
    },


    # ========================================================
    # NEXT PURCHASE PREDICTION
    # ========================================================

    {
        "question": "When will customer 1 buy again?",
        "expected_tools": ["predict_next_purchase"]
    },
    {
        "question": "Is customer 1 due for another purchase?",
        "expected_tools": ["predict_next_purchase"]
    },
    {
        "question": "Will customer 1 likely purchase soon?",
        "expected_tools": ["predict_next_purchase"]
    },
    {
        "question": "Is customer 1 overdue for a purchase?",
        "expected_tools": ["predict_next_purchase"]
    },
    {
        "question": "Predict customer 1's next purchase.",
        "expected_tools": ["predict_next_purchase"]
    },
    {
        "question": "Should I contact customer 1 now?",
        "expected_tools": ["predict_next_purchase"]
    },
    {
        "question": "When should I follow up with customer 1?",
        "expected_tools": ["predict_next_purchase"]
    },
    {
        "question": "Is now a good time to remind customer 1?",
        "expected_tools": ["predict_next_purchase"]
    },


    # ========================================================
    # MULTI-TOOL QUESTIONS
    # ========================================================

    {
        "question": "Which are my best and worst-performing products?",
        "expected_tools": [
            "get_hero_products",
            "get_weak_products"
        ]
    },
    {
        "question": "Compare my strongest products with my weakest products.",
        "expected_tools": [
            "get_hero_products",
            "get_weak_products"
        ]
    },
    {
        "question": "Tell me about customer 1 and predict when they will buy again.",
        "expected_tools": [
            "get_customer_profile",
            "predict_next_purchase"
        ]
    },
    {
        "question": "Show me customer 1's purchase history and tell me when they are likely to buy again.",
        "expected_tools": [
            "get_customer_profile",
            "predict_next_purchase"
        ]
    },
    {
        "question": "Give me my business overview and tell me which products are performing best.",
        "expected_tools": [
            "get_business_dashboard",
            "get_hero_products"
        ]
    },
    {
        "question": "Give me my business overview and show me both my best and weakest products.",
        "expected_tools": [
            "get_business_dashboard",
            "get_hero_products",
            "get_weak_products"
        ]
    }
]


# ============================================================
# TOOL ROUTING
# ============================================================

def get_called_tools(question):

    messages = [
        {
            "role": "system",
            "content": (
                "You are a retail business assistant. "
                "Select and call every tool necessary to answer "
                "the user's question. "
                "Do not answer until all necessary tools have been called."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    called_tools = []

    for _ in range(5):

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools,
            tool_choice="required"
        )

        message = response.choices[0].message

        messages.append(message)

        if not message.tool_calls:
            break

        for tool_call in message.tool_calls:

            function_name = tool_call.function.name

            called_tools.append(function_name)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": "{}"
                }
            )

    return list(dict.fromkeys(called_tools))


# ============================================================
# SCORE ROUTING
# ============================================================

def score_routing(expected_tools, actual_tools):

    expected = set(expected_tools)
    actual = set(actual_tools)

    return expected == actual


# ============================================================
# RUN EVALUATION
# ============================================================

def run_eval():

    correct = 0
    total = len(copilot_golden_dataset)

    single_tool_correct = 0
    single_tool_total = 0

    multi_tool_correct = 0
    multi_tool_total = 0

    print("=" * 60)
    print("RETAILMIND AI — COPILOT TOOL ROUTING EVAL")
    print("=" * 60)

    for index, case in enumerate(copilot_golden_dataset, start=1):

        question = case["question"]
        expected_tools = case["expected_tools"]

        print(f"\nTest {index}: {question}")

        try:

            actual_tools = get_called_tools(question)

            is_correct = score_routing(
                expected_tools,
                actual_tools
            )

            if is_correct:
                correct += 1

            if len(expected_tools) == 1:

                single_tool_total += 1

                if is_correct:
                    single_tool_correct += 1

            else:

                multi_tool_total += 1

                if is_correct:
                    multi_tool_correct += 1

            status = "✅" if is_correct else "❌"

            print(f"  {status}")
            print(f"  Expected: {expected_tools}")
            print(f"  Actual:   {actual_tools}")

        except Exception as e:

            print(f"  ⚠️ FAILED: {e}")

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    overall_accuracy = (
        correct / total * 100
        if total
        else 0
    )

    print(
        f"Overall Routing Accuracy: "
        f"{overall_accuracy:.1f}% "
        f"({correct}/{total})"
    )

    if single_tool_total:

        single_accuracy = (
            single_tool_correct
            / single_tool_total
            * 100
        )

        print(
            f"Single-Tool Accuracy: "
            f"{single_accuracy:.1f}% "
            f"({single_tool_correct}/{single_tool_total})"
        )

    if multi_tool_total:

        multi_accuracy = (
            multi_tool_correct
            / multi_tool_total
            * 100
        )

        print(
            f"Multi-Tool Accuracy: "
            f"{multi_accuracy:.1f}% "
            f"({multi_tool_correct}/{multi_tool_total})"
        )


if __name__ == "__main__":
    run_eval()