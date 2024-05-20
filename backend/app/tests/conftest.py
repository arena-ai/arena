import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import User, Setting, Event, EventIdentifier, Attribute, EventAttribute
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers
from app.lm.models import LMApiKeys, ChatCompletionRequest, ChatCompletionResponse, openai, mistral, anthropic


@pytest.fixture(scope="module", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(EventIdentifier)
        session.exec(statement)
        statement = delete(EventAttribute)
        session.exec(statement)
        statement = delete(Attribute)
        session.exec(statement)
        statement = delete(Event)
        session.exec(statement)
        statement = delete(Setting)
        session.exec(statement)
        statement = delete(User)
        session.exec(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )

@pytest.fixture
def language_models_api_keys():
    return LMApiKeys(
        openai_api_key=os.getenv("ARENA_OPENAI_API_KEY"),
        mistral_api_key=os.getenv("ARENA_MISTRAL_API_KEY"),
        anthropic_api_key=os.getenv("ARENA_ANTHROPIC_API_KEY"),
    )

@pytest.fixture
def chat_input_gen():
    def chat_input(model: str):
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
            ],
            "temperature": 1.2,
            "max_tokens": 1000,
        }
    return chat_input


@pytest.fixture
def chat_completion_create_openai() -> openai.ChatCompletionRequest:
    return openai.ChatCompletionRequest(**{
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "Write a short poem about the beauty of nature."}
        ],
        "max_tokens": 100,
        "temperature": 0.9,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "n": 3,
    })

@pytest.fixture
def chat_completion_openai() -> openai.ChatCompletionResponse:
    return openai.ChatCompletionResponse(
        id="cmpl-123",
        choices=[
            openai.Choice(
                finish_reason="stop",
                index=0,
                logprobs=openai.ChoiceLogprobs(
                    content=[
                        openai.TokenLogprob(
                            token="Hello",
                            logprob=-1.34,
                            top_logprobs=[],
                            text_offset=None,
                        ),
                        openai.TokenLogprob(
                            token="world!",
                            logprob=-1.19,
                            top_logprobs=[],
                            text_offset=None,
                        ),
                    ]
                ),
                message=openai.Message(
                    role="assistant", content="Hello world!"
                ),
            )
        ],
        created=1672463200,
        model="gpt-3.5-turbo",
        object="chat.completion",
        system_fingerprint="0x1234abcd",
        usage=openai.CompletionUsage(
            prompt_tokens=5,
            completion_tokens=10,
            total_tokens=15,
        ),
    )

@pytest.fixture
def chat_completion_create_mistral() -> mistral.ChatCompletionRequest:
    return mistral.ChatCompletionRequest(
        messages=[
            mistral.Message(
                content="Hello, how can I assist you today?",
                role="assistant",
            ),
            mistral.Message(
                content="I need the current weather in San Francisco",
                role="user",
            )
        ],
        model="mistral-medium-2312",
        max_tokens=100,
        response_format=mistral.ResponseFormat(type="text"),
        safe_prompt=True,
        random_seed=0,
        temperature=1.0,
        stream=False
    )


@pytest.fixture
def chat_completion_mistral() -> mistral.ChatCompletionResponse:
    return mistral.ChatCompletionResponse(
        id="cmpl-3o4Mn05jW6S9Zu2DLt2g3t0aFgU",
        choices=[
            mistral.Choice(
                index=0,
                message=mistral.Message(role="assistant", content="Hello, how can I assist you today?"),
                finish_reason="stop",
                logprobs=mistral.ChoiceLogprobs(
                    content=[
                        mistral.TokenLogprob(
                            token=".",
                            logprob=-0.100103,
                            top_logprobs=[mistral.TopLogprob(token=".", logprob=-0.100103)]
                        )
                    ]
                )
            )
        ],
        model="gpt-3.0-turbo",
        object="chat.completion",
        created=1661535393,
        usage=mistral.CompletionUsage(completion_tokens=11, prompt_tokens=3, total_tokens=14)
    )


@pytest.fixture
def chat_completion_create_anthropic() -> anthropic.ChatCompletionRequest:
    return anthropic.ChatCompletionRequest(**{
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Hello, Claude, how can you help?"},
        ],
        "model": "claude-2.0",
        "metadata": {"user_id": "123e4567-e89b-12d3-a456-426614174000"},
        "system": "You are a helpful assistant.",
        "temperature": 0.8,
    })

@pytest.fixture
def chat_completion_anthropic() -> anthropic.ChatCompletionResponse:
    return anthropic.ChatCompletionResponse(
        id="0987654321",
        content=[anthropic.TextBlock(type="text", text="The best answer is (B)")],
        model="text-generation-model",
        role="assistant",
        stop_reason="stop_sequence",
        stop_sequence="B)",
        type="message",
        usage=anthropic.CompletionUsage(input_tokens=10, output_tokens=20)
    )

@pytest.fixture
def text_with_pii() -> str:
    return """Hello I am Henry Smith and my account IBAN is GB87 BARC 2065 8244 9716 55, John Dean should have my phone number: +1-202-688-5500.
If not send me a message at henry.smith@sarus.tech or a letter at: 32 rue Alexandre Dumas, Paris 11"""