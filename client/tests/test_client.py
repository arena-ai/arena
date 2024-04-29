import os
from dotenv import load_dotenv
# Load .env
load_dotenv()
from arena.client import Client

def test_chat():
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")

    # Connect to arena
    client = Client(user=user, password=password)
    
    # Set the credentials
    client.openai_api_key(os.getenv("ARENA_OPENAI_API_KEY"))

    # Run a query
    resp = client.chat_completions(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ])
    assert(resp.choices[0].message.role == "assistant")
    print(f"\n{resp.choices[0].message.content}")

    # Mistral
    client.mistral_api_key(os.getenv("ARENA_MISTRAL_API_KEY"))
    resp = client.chat_completions(model="mistral-small", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ])
    assert(resp.choices[0].message.role == "assistant")
    print(f"\n{resp.choices[0].message.content}")

    # Anthropic
    client.anthropic_api_key(os.getenv("ARENA_ANTHROPIC_API_KEY"))
    resp = client.chat_completions(model="claude-2.0", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ], max_tokens=500)
    assert(resp.choices[0].message.role == "assistant")
    print(f"\n{resp.choices[0].message.content}")


def test_judge():
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")

    # Connect to arena
    client = Client(user=user, password=password)
    
    # Set the credentials
    client.openai_api_key(os.getenv("ARENA_OPENAI_API_KEY"))

    # Run a query
    resp = client.chat_completions(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
        ], arena_parameters={
            "judge_evaluation": True,
        })
    assert(resp.choices[0].message.role == "assistant")
    print(f"\n{resp.choices[0].message.content}")

    # Mistral
    client.mistral_api_key(os.getenv("ARENA_MISTRAL_API_KEY"))
    resp = client.chat_completions(model="mistral-small", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
        ], arena_parameters={
            "judge_evaluation": True,
        })
    assert(resp.choices[0].message.role == "assistant")
    print(f"\n{resp.choices[0].message.content}")

    # Anthropic
    client.anthropic_api_key(os.getenv("ARENA_ANTHROPIC_API_KEY"))
    resp = client.chat_completions(model="claude-2.0", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
        ], max_tokens=500, arena_parameters={
            "judge_evaluation": True,
        })
    assert(resp.choices[0].message.role == "assistant")
    print(f"\n{resp.choices[0].message.content}")


def test_user_eval():
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")

    # Connect to arena
    client = Client(user=user, password=password)
    
    # Set the credentials
    client.openai_api_key(os.getenv("ARENA_OPENAI_API_KEY"))

    # Run a query
    resp = client.chat_completions(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
        ], arena_parameters={
            "judge_evaluation": True,
        })
    print(client.evaluation(resp.id, 0.5))
