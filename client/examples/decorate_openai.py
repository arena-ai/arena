import os
from time import time
from rich import print
from dotenv import load_dotenv
from openai import OpenAI
from arena.client import Client
from arena.models import LMConfig
# Load .env
load_dotenv()

# BASE_URL = "http://localhost/api/v1"
BASE_URL = "https://arena.sarus.app/api/v1"

def simple_chat_completion():
    print("\n[bold red]Simple OpenAI chat completion")
    api_key = os.getenv("ARENA_OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    t = time()
    resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ])
    print(f"resp = {resp.choices[0].message.content} ({time()-t})")


def decorated_chat_completion():
    print("\n[bold red]Decorated OpenAI chat completion")
    # Added this
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    arena = Client(user=user, password=password, base_url=BASE_URL)
    arena.decorate(OpenAI)
    t = time()
    # Everything is unchanged then
    api_key = os.getenv("ARENA_OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ])
    print(f"resp = {resp.choices[0].message.content} ({time()-t})")


def decorated_chat_completion_with_user_eval():
    print("\n[bold red]Decorated OpenAI chat completion with eval")
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    arena = Client(user=user, password=password, base_url=BASE_URL)
    arena.decorate(OpenAI)
    # arena.lm_config(lm_config=LMConfig(pii_removal="replace"))
    t = time()
    api_key = os.getenv("ARENA_OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
        ],
    )
    print(f"resp = {resp.choices[0].message.content} ({time()-t})")
    # Added this
    arena.evaluation(resp.id, 0.98)

def arena_chat_completion_with_eval():
    print("\n[bold red]Arena chat completion with user eval")
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    arena = Client(user=user, password=password, base_url=BASE_URL)
    arena.anthropic_api_key(os.getenv("ARENA_ANTHROPIC_API_KEY"))
    t = time()
    resp = arena.chat_completions(model="claude-2.1", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
        ],
        max_tokens=100,
        lm_config={"judge_evaluation": True},
    )
    print(f"resp = {resp.choices[0].message.content} ({time()-t})")
    # Added this
    arena.evaluation(resp.id, 0.98)

def arena_chat_completion_with_eval_from_test():
    print("\n[bold red]Arena chat completion with user eval from test")
    user = "test@sarus.tech"
    password = "password"
    arena = Client(user=user, password=password, base_url=BASE_URL)
    arena.openai_api_key(os.getenv("ARENA_OPENAI_API_KEY"))
    arena.mistral_api_key(os.getenv("ARENA_MISTRAL_API_KEY"))
    arena.lm_config(lm_config=LMConfig(judge_evaluation=True, pii_removal="replace"))
    t = time()
    resp = arena.chat_completions(model="mistral-small", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What are the 10 first even prime numbers?"},
        ],
        temperature=1.0,
        lm_config={"judge_evaluation": True},
    )
    print(f"resp = {resp.choices[0].message.content} ({time()-t})")
    # Added this
    arena.evaluation(resp.id, 0.98)

simple_chat_completion()
decorated_chat_completion()
decorated_chat_completion_with_user_eval()
arena_chat_completion_with_eval()
for _ in range(5):
    arena_chat_completion_with_eval_from_test()
