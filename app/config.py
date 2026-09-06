import os
from dotenv import load_dotenv
load_dotenv()

database_url = os.getenv("DATABASE_URL")
if database_url is None:
    raise ValueError("databse url is not found in .env")

groq_api = os.getenv("GROQ_API_KEY")

if groq_api is None:
    raise ValueError("groq api is not found in .env")

groq_vision_model = os.getenv("GROQ_VISION_MODEL")

