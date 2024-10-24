import os
from time import sleep
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from rich import print
import pytest

from app.models import Event
from app.core.config import settings
from app.lm.models import (
    openai,
    mistral,
    anthropic,
    ChatCompletionRequest,
    LMConfig,
)

from openai import OpenAI
from mistralai import Mistral
from anthropic import Anthropic

# Open AI


def test_openai_client(chat_input_gen) -> None:
    """Test the native openai client"""
    openai_client = OpenAI(api_key=os.getenv("ARENA_OPENAI_API_KEY"))
    response = openai_client.chat.completions.create(
        **chat_input_gen("gpt-3.5-turbo")
    )
    assert len(response.choices) == 1


def test_openai_client_arena_endpoint(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    chat_input_gen,
) -> None:
    """Test the native openai client with arena in proxy mode"""
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={
            "name": "OPENAI_API_KEY",
            "content": os.getenv("ARENA_OPENAI_API_KEY"),
        },
    )
    openai_client = OpenAI(
        api_key=superuser_token_headers["Authorization"][7:],
        base_url="http://localhost/api/v1/lm/openai",
    )
    response = openai_client.chat.completions.create(
        **chat_input_gen("gpt-3.5-turbo")
    )
    assert len(response.choices) == 1


def test_openai(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    chat_input_gen,
) -> None:
    """Test arena openai"""
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={
            "name": "OPENAI_API_KEY",
            "content": os.getenv("ARENA_OPENAI_API_KEY"),
        },
    )
    response = client.post(
        f"{settings.API_V1_STR}/lm/openai/chat/completions",
        headers=superuser_token_headers,
        json=chat_input_gen("gpt-3.5-turbo"),
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["choices"]) == 1


@pytest.mark.skip(reason="too costly")
def test_all_openai_models(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    chat_input_gen,
) -> None:
    """Test arena openai"""
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={
            "name": "OPENAI_API_KEY",
            "content": os.getenv("ARENA_OPENAI_API_KEY"),
        },
    )
    for model in openai.MODELS:
        print(model)
        response = client.post(
            f"{settings.API_V1_STR}/lm/openai/chat/completions",
            headers=superuser_token_headers,
            json=chat_input_gen(model),
        )
        assert response.status_code == 200
        content = response.json()
        print(content)


def test_mistral_client(chat_input_gen) -> None:
    """Test the native mistral client"""
    mistral_client = Mistral(api_key=os.getenv("ARENA_MISTRAL_API_KEY"))
    response = mistral_client.chat.complete(**chat_input_gen("mistral-small"))
    assert len(response.choices) == 1


def test_mistral_client_arena_endpoint(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    chat_input_gen,
) -> None:
    """Test the native mistral client with arena in proxy mode"""
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={
            "name": "MISTRAL_API_KEY",
            "content": os.getenv("ARENA_MISTRAL_API_KEY"),
        },
    )
    mistral_client = Mistral(
        api_key=superuser_token_headers["Authorization"][7:],
        server_url="http://localhost/api/v1/lm/mistral",
    )
    response = mistral_client.chat.complete(**chat_input_gen("mistral-small"))
    assert len(response.choices) == 1


def test_mistral_models(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test the native mistral client"""
    mistral_client = Mistral(api_key=os.getenv("ARENA_MISTRAL_API_KEY"))
    response = mistral_client.models.list()
    print(sorted([m["id"] for m in response.model_dump()["data"]]))


def test_mistral(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    chat_input_gen,
) -> None:
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={
            "name": "MISTRAL_API_KEY",
            "content": os.getenv("ARENA_MISTRAL_API_KEY"),
        },
    )
    response = client.post(
        f"{settings.API_V1_STR}/lm/mistral/v1/chat/completions",
        headers=superuser_token_headers,
        json=chat_input_gen("mistral-small"),
    )
    assert response.status_code == 200
    _ = response.json()


@pytest.mark.skip(reason="Too costly")
def test_all_mistral_models(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    chat_input_gen,
) -> None:
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={
            "name": "MISTRAL_API_KEY",
            "content": os.getenv("ARENA_MISTRAL_API_KEY"),
        },
    )
    for model in mistral.MODELS:
        print(model)
        ccc = ChatCompletionRequest.model_validate(chat_input_gen(model))
        ccc = mistral.ChatCompletionRequest.from_chat_completion_request(ccc)
        response = client.post(
            f"{settings.API_V1_STR}/lm/mistral/v1/chat/completions",
            headers=superuser_token_headers,
            json=ccc.to_dict(),
        )
        assert response.status_code == 200
        content = response.json()
        print(content)


def test_anthropic_client(chat_input_gen) -> None:
    """Test the native anthropic client"""
    anthropic_client = Anthropic(api_key=os.getenv("ARENA_ANTHROPIC_API_KEY"))
    ccc = ChatCompletionRequest.model_validate(chat_input_gen("claude-2.1"))
    ccc = anthropic.ChatCompletionRequest.from_chat_completion_request(ccc)
    ccc = ccc.to_dict()
    response = anthropic_client.messages.create(**ccc)
    assert len(response.content) == 1


def test_anthropic_client_arena_endpoint(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    chat_input_gen,
) -> None:
    """Test the native mistral client with arena in proxy mode"""
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={
            "name": "ANTHROPIC_API_KEY",
            "content": os.getenv("ARENA_ANTHROPIC_API_KEY"),
        },
    )
    anthropic_client = Anthropic(
        auth_token=superuser_token_headers["Authorization"][7:],
        base_url="http://localhost/api/v1/lm/anthropic",
    )
    ccc = ChatCompletionRequest.model_validate(chat_input_gen("claude-2.1"))
    ccc = anthropic.ChatCompletionRequest.from_chat_completion_request(ccc)
    ccc = ccc.to_dict()
    response = anthropic_client.messages.create(**ccc)
    assert len(response.content) == 1


def test_anthropic(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    chat_input_gen,
) -> None:
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={
            "name": "ANTHROPIC_API_KEY",
            "content": os.getenv("ARENA_ANTHROPIC_API_KEY"),
        },
    )
    ccc = ChatCompletionRequest.model_validate(chat_input_gen("claude-2.1"))
    ccc = anthropic.ChatCompletionRequest.from_chat_completion_request(ccc)
    response = client.post(
        f"{settings.API_V1_STR}/lm/anthropic/v1/messages",
        headers=superuser_token_headers,
        json=ccc.to_dict(),
    )
    assert response.status_code == 200
    _ = response.json()


@pytest.mark.skip(reason="Too costly")
def test_all_anthropic_models(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    chat_input_gen,
) -> None:
    # Setup a token
    client.post(
        f"{settings.API_V1_STR}/settings",
        headers=superuser_token_headers,
        json={
            "name": "ANTHROPIC_API_KEY",
            "content": os.getenv("ARENA_ANTHROPIC_API_KEY"),
        },
    )
    for model in anthropic.MODELS:
        print(model)
        ccc = ChatCompletionRequest.model_validate(chat_input_gen(model))
        ccc = anthropic.ChatCompletionRequest.from_chat_completion_request(ccc)
        response = client.post(
            f"{settings.API_V1_STR}/lm/anthropic/v1/messages",
            headers=superuser_token_headers,
            json=ccc.to_dict(),
        )
        assert response.status_code == 200
        content = response.json()
        print(content)


def test_language_models(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    chat_input_gen,
) -> None:
    # Setup all tokens
    for api in ["OPENAI", "MISTRAL", "ANTHROPIC"]:
        print(f"Set {api} token")
        client.post(
            f"{settings.API_V1_STR}/settings",
            headers=superuser_token_headers,
            json={
                "name": f"{api}_API_KEY",
                "content": os.getenv(f"ARENA_{api}_API_KEY"),
            },
        )
    for ccc in [
        (ChatCompletionRequest(**chat_input_gen("gpt-3.5-turbo"))),
        (ChatCompletionRequest(**chat_input_gen("mistral-small"))),
        (ChatCompletionRequest(**chat_input_gen("claude-2.1"))),
    ]:
        # Call Arena
        response = client.post(
            f"{settings.API_V1_STR}/lm/chat/completions",
            headers=superuser_token_headers,
            json=ccc.to_dict(),
        )
        assert response.status_code == 200
    events = db.exec(select(Event)).all()
    for event in events:
        print(f"\nEVENT {event}")


def test_language_models_with_judges(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    chat_input_gen,
) -> None:
    # Setup all tokens
    for api in ["OPENAI", "MISTRAL", "ANTHROPIC"]:
        print(f"Set {api} token")
        client.post(
            f"{settings.API_V1_STR}/settings",
            headers=superuser_token_headers,
            json={
                "name": f"{api}_API_KEY",
                "content": os.getenv(f"ARENA_{api}_API_KEY"),
            },
        )
    for ccc in [
        (ChatCompletionRequest(**chat_input_gen("gpt-3.5-turbo"))),
        (ChatCompletionRequest(**chat_input_gen("mistral-small"))),
        (ChatCompletionRequest(**chat_input_gen("claude-2.1"))),
    ]:
        ccc.lm_config = LMConfig(judge_evaluation=True)
        # Call Arena
        response = client.post(
            f"{settings.API_V1_STR}/lm/chat/completions",
            headers=superuser_token_headers,
            json=ccc.to_dict(),
        )
        assert response.status_code == 200
    # Wait for the last judge to finish
    sleep(3)
    events = db.exec(select(Event)).all()
    for event in events:
        print(f"\nEVENT {event}")


def test_language_models_with_pii_removal(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    text_with_pii: str,
) -> None:
    # Setup all tokens
    for api in ["OPENAI", "MISTRAL", "ANTHROPIC"]:
        print(f"Set {api} token")
        client.post(
            f"{settings.API_V1_STR}/settings",
            headers=superuser_token_headers,
            json={
                "name": f"{api}_API_KEY",
                "content": os.getenv(f"ARENA_{api}_API_KEY"),
            },
        )
    # Call Arena
    response = client.post(
        f"{settings.API_V1_STR}/lm/chat/completions",
        headers=superuser_token_headers,
        json={
            "messages": [
                {
                    "role": "user",
                    "content": text_with_pii,
                }
            ],
            "model": "gpt-3.5-turbo",
            "lm_config": {"pii_removal": "replace"},
        },
    )
    assert response.status_code == 200
    print(response.json())
    events = db.exec(select(Event)).all()
    for event in events:
        print(f"\nEVENT {event}")
