import os
from openai import OpenAI
from dotenv import load_dotenv
from arena.client import Client
# Load .env
load_dotenv()

def simple_chat_completion():
    api_key = os.getenv("ARENA_OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ])
    print(resp.choices[0].message.content)


def decorated_chat_completion():
    # Added this
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    arena = Client(user=user, password=password, base_url="http://localhost/api/v1")
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
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    arena = Client(user=user, password=password, base_url="http://localhost/api/v1")
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

def arena_chat_completion_with_user_eval():
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    arena = Client(user=user, password=password, base_url="http://localhost/api/v1")
    arena.openai_api_key(os.getenv("ARENA_OPENAI_API_KEY"))

    resp = arena.chat_completions(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
        ],
        arena_parameters={"judge_evaluation": True}
    )
    print(resp.choices[0].message.content)
    # Added this
    arena.evaluation(resp.id, 0.98)

# simple_chat_completion()
# decorated_chat_completion()
# decorated_chat_completion_with_user_eval()
arena_chat_completion_with_user_eval()
