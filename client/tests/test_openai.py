import os
from openai import OpenAI
from dotenv import load_dotenv
# Load .env
load_dotenv()

def test_chat():
    print(os.getenv("ARENA_OPENAI_API_KEY"))