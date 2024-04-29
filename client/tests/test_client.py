import os
from dotenv import load_dotenv
# Load .env
load_dotenv()
from arena.client import Client

def test_chat():
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    client = Client(user=user, password=password)
    client.openai_api_key(os.getenv("ARENA_OPENAI_API_KEY"))
    client.mistral_api_key(os.getenv("ARENA_MISTRAL_API_KEY"))
    client.anthropic_api_key(os.getenv("ARENA_ANTHROPIC_API_KEY"))
    resp = client.chat_completions(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ])
    assert(resp.choices[0].message.role == "assistant")
    print(resp.choices[0].message.content)
    assert(len(resp.choices[0].message.content) > 10)