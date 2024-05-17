import os
from random import randint
from anthropic import Client as AnthropicClient
from dotenv import load_dotenv
# Load .env
load_dotenv()
from arena.client import Client
from arena.models import LMConfig

BASE_URL = "http://localhost/api/v1"

def test_chat():
    api_key = os.getenv("ARENA_ANTHROPIC_API_KEY")
    client = AnthropicClient(api_key=api_key)
    resp = client.messages.create(model="claude-2.1", messages=[
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ], max_tokens=1000, system="You are a helpful assistant.")
    print(resp.content[0].text)
    assert(len(resp.content[0].text) > 10)


def test_instrumented_chat():
    api_key = os.getenv("ARENA_ANTHROPIC_API_KEY")
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    arena = Client(username=user, password=password, base_url=BASE_URL)
    arena.decorate(AnthropicClient, mode="instrument")

    client = AnthropicClient(api_key=api_key)
    resp = client.messages.create(model="claude-2.1", messages=[
        {"role": "user", "content": f"What are instrumental variables in statistics? ({randint(0, 100)})"},
    ], max_tokens=1000, system="You are a helpful assistant.")
    print(resp.content[0].text)
    assert(len(resp.content[0].text) > 10)
