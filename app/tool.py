tools = [

    # 1. Business Dashboard
    {
        "type": "function",
        "function": {
            "name": "get_business_dashboard",
            "description": "Get overall store performance: total revenue, total orders, total customers, average order value.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    # 2. Hero Products
    {
        "type": "function",
        "function": {
            "name": "get_hero_products",
            "description": "Get the top 3 products with the highest revenue.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    # 3. Weak Products
    {
        "type": "function",
        "function": {
            "name": "get_weak_products",
            "description": "Get the 3 products with the lowest revenue.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    # 4. Customer Profile
    {
        "type": "function",
        "function": {
            "name": "get_customer_profile",
            "description": "Get detailed business intelligence about a specific customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The ID of the customer."
                    }
                },
                "required": ["customer_id"]
            }
        }
    },

    # 5. Next Purchase Prediction
    {
        "type": "function",
        "function": {
            "name": "predict_next_purchase",
            "description": "Predict whether a customer is due for their next purchase.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The ID of the customer."
                    }
                },
                "required": ["customer_id"]
            }
        }
    }
    {
    "type": "function",
    "function": {
        "name": "list_customers",
        "description": "Get a list of all customers belonging to this business, including their customer_id, name, and phone number. Use this when the retailer asks about customer names, wants a customer list, or needs to find a customer_id before looking up their full profile.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}
]
