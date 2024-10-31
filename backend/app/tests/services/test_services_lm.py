import os
from anyio import run
from app.services.lm import OpenAI, Mistral, Anthropic


def test_openai(chat_completion_create_openai) -> None:
    client = OpenAI(api_key=os.getenv("ARENA_OPENAI_API_KEY"))
    print(f"\n{client.headers}")
    response = run(
        client.openai_chat_completion, chat_completion_create_openai
    )
    print(f"\n{response}")


def test_mistral(chat_completion_create_mistral) -> None:
    client = Mistral(api_key=os.getenv("ARENA_MISTRAL_API_KEY"))
    print(f"\n{client.headers}")
    response = run(
        client.mistral_chat_completion, chat_completion_create_mistral
    )
    print(f"\n{response}")


def test_anthropic(chat_completion_create_anthropic) -> None:
    client = Anthropic(api_key=os.getenv("ARENA_ANTHROPIC_API_KEY"))
    print(f"\n{client.headers}")
    response = run(
        client.anthropic_chat_completion, chat_completion_create_anthropic
    )
    print(f"\n{response}")
