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


def copilot(question, db, business_id, history=None):

    messages = [
        {
            "role": "system",
            "content": (
                "You are a retail business assistant. "
                "If a question requires more than one piece of information "
                "to answer fully, call ALL the necessary tools before answering "
                "— do not answer with only partial information. "
                "Use the earlier conversation for context when the question "
                "refers back to something previously discussed."
            )
        }
    ]

    if history:
        for entry in history:
            messages.append({
                "role": "user",
                "content": entry["question"]
            })

            messages.append({
                "role": "assistant",
                "content": str(entry["answer"])
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

            function_args = json.loads(
                tool_call.function.arguments
            )

            function_to_call = available_functions[function_name]

            # Never trust business_id coming from the LLM.
            # Always use the authenticated user's business_id.
            function_args.pop("business_id", None)

            result = function_to_call(
                db,
                business_id=business_id,
                **function_args
            )

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(
                    result,
                    default=str
                )
            })

    messages.append({
        "role": "system",
        "content": """Explain the tool result in clean, simple, user-friendly plain text.
All monetary values are in Indian Rupees (₹), not dollars — always refer to them as rupees.
Do not use Markdown.
Do not use *, **, #, tables, pipes, or JSON.
Do not include escape characters such as \\n.
Use short paragraphs instead of bullet points.
Return only the final answer."""
    })

    final_response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        tools=tools,
        tool_choice="none"
    )

    return final_response.choices[0].message.content