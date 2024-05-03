import os
from openai import OpenAI
from dotenv import load_dotenv
# Load .env
load_dotenv()
from arena.client import Client
from arena.models import LMConfig

def test_chat():
    api_key = os.getenv("ARENA_OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ])
    assert(resp.choices[0].message.role == "assistant")
    print(resp.choices[0].message.content)
    assert(len(resp.choices[0].message.content) > 10)


def test_masked_chat():
    api_key = os.getenv("ARENA_OPENAI_API_KEY")
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    arena = Client(user=user, password=password)
    arena.decorate(OpenAI)
    arena.lm_config(lm_config=LMConfig(pii_removal="replace"))

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hi, I am John Smith, I wonder what the fastest animal on earth is."},
    ])
    assert(resp.choices[0].message.role == "assistant")
    print(resp.choices[0].message.content)
    assert(len(resp.choices[0].message.content) > 10)


def test_chat_with_judge():
    api_key = os.getenv("ARENA_OPENAI_API_KEY")
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    arena = Client(user=user, password=password)
    arena.decorate(OpenAI)
    arena.lm_config(lm_config=LMConfig(judge_evaluation=True))

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ])
    assert(resp.choices[0].message.role == "assistant")
    print(resp.choices[0].message.content)
    assert(len(resp.choices[0].message.content) > 10)