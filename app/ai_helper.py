from groq import Groq
from config import groq_api
client = Groq(api_key= groq_api)


def generate_prediction_message(average_interval,days_since_last_bought,status):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role" : "user",
                "content" : [
                    {
                    "type" : "text",
                    "text" : f"""You are a retail business assistant.

                            Generate one short, natural sentence explaining the customer's next-purchase prediction.

                            Average purchase interval: {average_interval} days.
                            Days since last purchase: {days_since_last_bought} days.
                            Current status: {status}.

                            Explain what this means in simple business language. Do not mention calculations or technical terms. Return only the sentence."""
                    }
                ]
            }
        ]
    )
    return response.choices[0].message.content

def generate_whatsapp_message(customer_name,favorite_product,status):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role" : "user",
                "content" : [
                    {
                        "type" : "text",
                        "text" : f"""
                                    You are a friendly small retail store owner writing a casual WhatsApp message to a regular customer.

                                    Customer name: {customer_name}
                                    Their most frequently bought product: {favorite_product}
                                    Situation: {status}

                                    Instructions:
                                    - If status is "overdue", write a warm, gentle nudge — like you're checking in because you haven't seen them in a while.
                                    - If status is "approaching", write a soft, casual reminder — like you just thought of them, not urgent.
                                    - Keep it short: 2-3 sentences maximum.
                                    - Sound like a real shop owner texting a regular customer — casual, warm, not corporate or formal.
                                    - Naturally mention the product without sounding like an advertisement.
                                    - Do NOT mention "AI", "prediction", "algorithm", "system", "data", or anything technical.
                                    - Return ONLY the message text, nothing else — no greeting like "Here's your message:", no quotes around it."""
                    }
                ]
            }
        ]
    )
    return response.choices[0].message.content