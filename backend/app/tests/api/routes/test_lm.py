import os
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings

from openai import OpenAI
from mistralai.client import MistralClient
from anthropic import Anthropic

def chat_input(model: str, system=True):
    """A Standard chat input"""
    return {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Who is Victor Hugo? Where does he live?"
            }
        ]
    }


def test_openai_client() -> None:
    """Test the native openai client"""
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response =  openai_client.chat.completions.create(**chat_input("gpt-3.5-turbo"))
    assert len(response.choices) == 1


def test_openai_client_arena_endpoint(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test the native openai client with arena in proxy mode"""
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={"name": "OPENAI_API_KEY", "content": os.getenv("OPENAI_API_KEY")},
    )
    openai_client = OpenAI(api_key=superuser_token_headers["Authorization"][7:], base_url=f"http://localhost/api/v1/lm/openai")
    response =  openai_client.chat.completions.create(**chat_input("gpt-3.5-turbo"))
    assert len(response.choices) == 1


def test_openai(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test arena openai"""
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={"name": "OPENAI_API_KEY", "content": os.getenv("OPENAI_API_KEY")},
    )
    response = client.post(
        f"{settings.API_V1_STR}/lm/openai/chat/completions",
        headers=superuser_token_headers,
        json=chat_input("gpt-3.5-turbo"),
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["choices"]) == 1



def test_mistral_client() -> None:
    """Test the native mistral client"""
    mistral_client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))
    response =  mistral_client.chat(**chat_input("mistral-small"))
    assert len(response.choices) == 1


def test_mistral_client_arena_endpoint(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test the native mistral client with arena in proxy mode"""
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={"name": "MISTRAL_API_KEY", "content": os.getenv("MISTRAL_API_KEY")},
    )
    mistral_client = MistralClient(api_key=superuser_token_headers["Authorization"][7:], endpoint=f"http://localhost/api/v1/lm/mistral")
    response =  mistral_client.chat(**chat_input("mistral-small"))
    assert len(response.choices) == 1


def test_mistral_models(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test the native mistral client"""
    mistral_client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))
    response =  mistral_client.list_models()
    print(response)
    assert False


def test_mistral(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={"name": "MISTRAL_API_KEY", "content": os.getenv("MISTRAL_API_KEY")},
    )
    response = client.post(
        f"{settings.API_V1_STR}/lm/mistral/v1/chat/completions",
        headers=superuser_token_headers,
        json=chat_input("mistral-small"),
    )
    assert response.status_code == 200
    content = response.json()



def test_anthropic_client() -> None:
    """Test the native anthropic client"""
    anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response =  anthropic_client.messages.create(**chat_input("claude-2.1"))
    assert len(response.choices) == 1


def test_anthropic_client_arena_endpoint(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test the native mistral client with arena in proxy mode"""
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={"name": "ANTHROPIC_API_KEY", "content": os.getenv("ANTHROPIC_API_KEY")},
    )
    anthropic_client = MistralClient(api_key=superuser_token_headers["Authorization"][7:], endpoint=f"http://localhost/api/v1/lm/mistral")
    response =  anthropic_client.messages.create(**chat_input("claude-2.1"))
    assert len(response.choices) == 1


def test_anthropic(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={"name": "ANTHROPIC_API_KEY", "content": os.getenv("ANTHROPIC_API_KEY")},
    )
    response = client.post(
        f"{settings.API_V1_STR}/lm/anthropic/v1/messages",
        headers=superuser_token_headers,
        json=(chat_input("claude-2.1") | {"max_tokens": 1584, "temperature": 0.5}),
    )
    assert response.status_code == 200
    content = response.json()