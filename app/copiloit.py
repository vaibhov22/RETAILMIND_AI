import json
from groq import Groq

from config import groq_api
from tool import tools
from crud import (
    get_business_dashboard,
    get_hero_products,
    get_weak_products,
    get_customer_profile,
    predict_next_purchase,
    list_customers
)

client = Groq(api_key=groq_api)

available_functions = {
    "get_business_dashboard": get_business_dashboard,
    "get_hero_products": get_hero_products,
    "get_weak_products": get_weak_products,
    "get_customer_profile": get_customer_profile,
    "predict_next_purchase": predict_next_purchase,
    "list_customers": list_customers
}

allowed_arguments = {
    "get_business_dashboard": set(),
    "get_hero_products": set(),
    "get_weak_products": set(),
    "list_customers": set(),
    "get_customer_profile": {"customer_id"},
    "predict_next_purchase": {"customer_id"}
}


def copilot(question, db, business_id, history=None):

    messages = [
        {
            "role": "system",
            "content": (
                "STRICT TOOL SELECTION:\n"
                "Before calling any tool, identify the minimum set of tools "
                "required to answer the question.\n\n"

                "If the question is about overall business metrics, revenue, "
                "orders, customer count, or business overview, call ONLY "
                "get_business_dashboard.\n"

                "If the question is about best-selling, strongest, or top "
                "products, call ONLY get_hero_products.\n"

                "If the question is about weak, poor, worst, or low-demand "
                "products, call ONLY get_weak_products.\n"

                "If the question asks to list or search customers, call ONLY "
                "list_customers.\n"

                "If the question is about an identified customer's existing "
                "information, including purchases, spending, favorite products, "
                "orders, last purchase, credit, buying behavior, or profile, "
                "call ONLY get_customer_profile.\n"

                "If the question is about when an identified customer will buy "
                "again, whether they are likely to purchase, whether they are "
                "overdue, or when to contact/follow up with them, call ONLY "
                "predict_next_purchase.\n\n"

                "NEVER call list_customers together with get_customer_profile.\n"
                "NEVER call get_customer_profile together with "
                "predict_next_purchase unless the user explicitly asks for "
                "both existing information and future prediction.\n"
                "NEVER call get_hero_products together with get_weak_products "
                "unless the user explicitly asks for both.\n\n"

                "Use earlier conversation context when the user refers to "
                "something previously discussed."
            )
        }
    ]

    if history:
        for item in history:
            if not isinstance(item, dict):
                continue

            role = item.get("role")
            content = item.get("content")

            if role in {"user", "assistant"} and content:
                messages.append({
                    "role": role,
                    "content": str(content)
                })

    messages.append({
        "role": "user",
        "content": question
    })

    while True:

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        messages.append(message)

        if not message.tool_calls:
            break

        for tool_call in message.tool_calls:

            function_name = tool_call.function.name

            if function_name not in available_functions:
                continue

            try:
                function_args = json.loads(
                    tool_call.function.arguments or "{}"
                )
            except (json.JSONDecodeError, TypeError):
                function_args = {}

            if not isinstance(function_args, dict):
                function_args = {}

            allowed = allowed_arguments.get(function_name, set())

            function_args = {
                key: value
                for key, value in function_args.items()
                if key in allowed
            }

            function_to_call = available_functions[function_name]

            if function_name in {
                "get_business_dashboard",
                "get_hero_products",
                "get_weak_products",
                "list_customers"
            }:
                result = function_to_call(
                    db,
                    business_id=business_id
                )

            elif function_name in {
                "get_customer_profile",
                "predict_next_purchase"
            }:
                if "customer_id" not in function_args:
                    result = {
                        "error": "Customer ID is required for this request."
                    }
                else:
                    result = function_to_call(
                        db,
                        customer_id=function_args["customer_id"],
                        business_id=business_id
                    )

            else:
                result = {
                    "error": "Unknown tool."
                }

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(result, default=str)
            })

    messages.append({
        "role": "system",
        "content": (
            "Explain the tool result in clean, simple, user-friendly plain text. "
            "All monetary values are in Indian Rupees (₹), not dollars. "
            "Do not use Markdown. "
            "Do not use *, **, #, tables, pipes, or JSON. "
            "Do not include escape characters such as \\n. "
            "Use short paragraphs instead of bullet points. "
            "Return only the final answer."
        )
    })

    final_response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        tool_choice="none"
    )

    return final_response.choices[0].message.content