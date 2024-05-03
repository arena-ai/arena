import os
from openai import OpenAI
from dotenv import load_dotenv
# Load .env
load_dotenv()

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