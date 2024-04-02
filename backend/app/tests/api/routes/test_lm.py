import os
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings


def test_openai(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings/",
        headers=superuser_token_headers,
        json={"name": "OPENAI_API_KEY", "content": os.getenv("OPENAI_API_KEY")},
    )
    response = client.post(
        f"{settings.API_V1_STR}/lm/openai/chat/completions",
        headers=superuser_token_headers,
        json={
            "model": "gpt-3.5-turbo",
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
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["choices"]) == 1


def test_mistral(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings/",
        headers=superuser_token_headers,
        json={"name": "MISTRAL_API_KEY", "content": os.getenv("MISTRAL_API_KEY")},
    )
    response = client.post(
        f"{settings.API_V1_STR}/lm/mistral/chat/completions",
        headers=superuser_token_headers,
        json={
            "model": "mistral-small",
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
        },
    )
    assert response.status_code == 200
    content = response.json()


def test_anthropic(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings/",
        headers=superuser_token_headers,
        json={"name": "ANTHROPIC_API_KEY", "content": os.getenv("ANTHROPIC_API_KEY")},
    )
    response = client.post(
        f"{settings.API_V1_STR}/lm/anthropic/v1/messages",
        headers=superuser_token_headers,
        json={
            "model": "mistral-small",
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
        },
    )
    assert response.status_code == 200
    content = response.json()