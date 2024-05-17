import os
from random import randint
from mistralai.client import MistralClient
from dotenv import load_dotenv
# Load .env
load_dotenv()
from arena.client import Client
from arena.models import LMConfig

BASE_URL = "http://localhost/api/v1"

def test_chat():
    api_key = os.getenv("ARENA_MISTRAL_API_KEY")
    client = MistralClient(api_key=api_key)
    resp = client.chat(model="mistral-small", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ])
    assert(resp.choices[0].message.role == "assistant")
    print(resp.choices[0].message.content)
    assert(len(resp.choices[0].message.content) > 10)


def test_instrumented_chat():
    api_key = os.getenv("ARENA_MISTRAL_API_KEY")
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    arena = Client(username=user, password=password, base_url=BASE_URL)
    arena.decorate(MistralClient, mode="instrument")

    client = MistralClient(api_key=api_key)
    resp = client.chat(model="mistral-small", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"What are instrumental variables in statistics? ({randint(0, 100)})"},
    ])
    assert(resp.choices[0].message.role == "assistant")
    print(resp.choices[0].message.content)
    assert(len(resp.choices[0].message.content) > 10)

