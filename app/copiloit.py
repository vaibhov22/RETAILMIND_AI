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


def call_groq_with_retry(messages, tool_choice="auto", max_retries=2):
    """
    Calls Groq's chat completion with retry handling.

    Returns the model message on success.
    Returns None if all attempts fail.
    """

    for attempt in range(max_retries):

        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                tools=tools,
                tool_choice=tool_choice
            )

            return response.choices[0].message

        except Exception as e:

            print(
                f"Groq request failed "
                f"(attempt {attempt + 1}/{max_retries}): {e}"
            )

            if attempt == max_retries - 1:
                return None

            continue


def clean_tool_arguments(function_name, function_args):
    """
    Sanitizes arguments returned by the LLM before calling
    the actual Python function.

    The LLM must never be trusted to provide business_id.
    """

    if not isinstance(function_args, dict):
        return {}

    cleaned_args = {}

    for key, value in function_args.items():

        # Ignore invalid/empty argument names.
        if not isinstance(key, str) or not key.strip():
            continue

        key = key.strip()

        # Never allow the LLM to control business_id.
        if key == "business_id":
            continue

        cleaned_args[key] = value

    return cleaned_args


def copilot(question, db, business_id, history=None):

    messages = [
        {
            "role": "system",
            "content": (
                "You are a retail business assistant. "

                "If a question requires more than one piece of "
                "information to answer fully, call ALL the necessary "
                "tools before answering — do not answer with only "
                "partial information. "

                "Use the earlier conversation for context when the "
                "question refers back to something previously discussed. "

                "When calling list_customers, do not provide any "
                "arguments. The system automatically provides the "
                "authenticated business_id. "

                "Never invent customer IDs. If you need a customer's "
                "real ID, call list_customers first."
            )
        }
    ]

    # -----------------------------------------
    # Conversation history
    # -----------------------------------------

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

    # -----------------------------------------
    # Current question
    # -----------------------------------------

    messages.append({
        "role": "user",
        "content": question
    })

    # -----------------------------------------
    # Tool-calling loop
    # -----------------------------------------

    while True:

        message = call_groq_with_retry(
            messages,
            tool_choice="auto"
        )

        if message is None:

            return (
                "Sorry, I had trouble processing that question. "
                "Could you try rephrasing it?"
            )

        messages.append(message)

        # No tools requested.
        if not message.tool_calls:
            break

        # -----------------------------------------
        # Execute every requested tool
        # -----------------------------------------

        for tool_call in message.tool_calls:

            function_name = tool_call.function.name

            # -----------------------------------------
            # Check that requested function exists
            # -----------------------------------------

            if function_name not in available_functions:

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps({
                        "error": "Requested tool is not available."
                    })
                })

                continue

            function_to_call = available_functions[function_name]

            # -----------------------------------------
            # Safely parse tool arguments
            # -----------------------------------------

            raw_arguments = tool_call.function.arguments

            try:

                function_args = json.loads(raw_arguments)

            except (json.JSONDecodeError, TypeError):

                function_args = {}

            # -----------------------------------------
            # Make sure arguments are a dictionary
            # -----------------------------------------

            if not isinstance(function_args, dict):

                function_args = {}

            # -----------------------------------------
            # Sanitize arguments
            # -----------------------------------------

            function_args = clean_tool_arguments(
                function_name,
                function_args
            )

            # -----------------------------------------
            # Execute tool safely
            # -----------------------------------------

            try:

                result = function_to_call(
                    db,
                    business_id=business_id,
                    **function_args
                )

            except TypeError as e:

                print(
                    f"Tool argument error for "
                    f"{function_name}: {e}"
                )

                result = {
                    "error": (
                        f"Invalid arguments supplied to "
                        f"{function_name}."
                    )
                }

            except Exception as e:

                print(
                    f"Tool execution error for "
                    f"{function_name}: {e}"
                )

                result = {
                    "error": (
                        f"Unable to execute {function_name}."
                    )
                }

            # -----------------------------------------
            # Return tool result to the model
            # -----------------------------------------

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(
                    result,
                    default=str
                )
            })

    # -----------------------------------------
    # Final response instructions
    # -----------------------------------------

    messages.append({
        "role": "system",
        "content": """Explain the tool result in clean, simple, user-friendly plain text.

All monetary values are in Indian Rupees (₹), not dollars — always refer to them as rupees.

Do not use Markdown.

Do not use *, **, #, tables, pipes, or JSON.

Do not include escape characters such as \\n.

Use short paragraphs instead of bullet points.

Do not invent information that is not present in the tool results.

If a tool reports that information was not found, clearly say that it was not found.

Return only the final answer."""
    })

    # -----------------------------------------
    # Generate final answer
    # -----------------------------------------

    final_message = call_groq_with_retry(
        messages,
        tool_choice="none"
    )

    if final_message is None:

        return (
            "Sorry, I had trouble finalizing that answer. "
            "Please try again."
        )

    return final_message.content