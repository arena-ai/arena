import os
from openai import OpenAI
from rich import print
from dotenv import load_dotenv
from arena.client import Client
# Load .env
load_dotenv()

def simple_chat_completion():
    print("\n[bold red]Simple OpenAI chat completion")
    api_key = os.getenv("ARENA_OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ])
    print(resp.choices[0].message.content)


def decorated_chat_completion():
    print("\n[bold red]Decorated OpenAI chat completion")
    # Added this
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    arena = Client(user=user, password=password)
    arena.decorate(OpenAI)

    # Everything is unchanged then
    api_key = os.getenv("ARENA_OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ])
    print(resp.choices[0].message.content)


def decorated_chat_completion_with_user_eval():
    print("\n[bold red]Decorated OpenAI chat completion with eval")
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    arena = Client(user=user, password=password)
    arena.decorate(OpenAI)

    api_key = os.getenv("ARENA_OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
        ],
    )
    print(resp.choices[0].message.content)
    # Added this
    arena.evaluation(resp.id, 0.98)

def arena_chat_completion_with_eval():
    print("\n[bold red]Arena chat completion with user eval")
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    arena = Client(user=user, password=password)
    arena.anthropic_api_key(os.getenv("ARENA_ANTHROPIC_API_KEY"))

    resp = arena.chat_completions(model="claude-2.1", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
        ],
        arena_parameters={"judge_evaluation": True},
        streaming=False,
        max_tokens=100,
    )
    print(resp.choices[0].message.content)
    # Added this
    arena.evaluation(resp.id, 0.98)

def arena_chat_completion_with_eval_from_test():
    print("\n[bold red]Arena chat completion with user eval from test")
    user = "test@sarus.tech"
    password = "password"
    arena = Client(user=user, password=password)
    arena.openai_api_key(os.getenv("ARENA_OPENAI_API_KEY"))
    arena.mistral_api_key(os.getenv("ARENA_MISTRAL_API_KEY"))

    resp = arena.chat_completions(model="mistral-small", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What are the 10 first even prime numbers?"},
        ],
        arena_parameters={"judge_evaluation": True},
    )
    print(resp.choices[0].message.content)
    # Added this
    arena.evaluation(resp.id, 0.98)

simple_chat_completion()
decorated_chat_completion()
decorated_chat_completion_with_user_eval()
arena_chat_completion_with_eval()
arena_chat_completion_with_eval_from_test()
