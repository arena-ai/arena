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
from app.lm.models import openai, mistral, anthropic, Choice, ChoiceLogprobs, Message, TokenLogprob, CompletionUsage, ChatCompletionToolParam, Function


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
def chat_completion_create_openai() -> openai.ChatCompletionCreate:
    return openai.ChatCompletionCreate(**{
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "Write a short poem about the beauty of nature."}
        ],
        "max_tokens": 100,
        "temperature": 0.9,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "n": 3
    })

@pytest.fixture
def chat_completion_openai() -> openai.ChatCompletion:
    return openai.ChatCompletion(
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
def chat_completion_create_mistral() -> mistral.ChatCompletionCreate:
    return mistral.ChatCompletionCreate(
        messages=[
            mistral.Message(
                content="Hello, how can I assist you today?",
                role="assistant",
            ),
            mistral.Message(
                content="I need the current weather in San Francisco",
                role="user",
                tool_calls=[
                    mistral.ChatCompletionToolParam(
                        function=mistral.Function(
                            arguments="{'location': 'San Francisco'}",
                            name="get_weather"
                        ),
                        type="function"
                    )
                ]
            )
        ],
        model="mistral-medium-2312",
        max_tokens=100,
        response_format=mistral.ResponseFormat(type="text"),
        safe_prompt=True,
        random_seed=0,
        temperature=0.5,
        tool_choice="auto",
        top_p=0.9,
        stream=False
    )


@pytest.fixture
def chat_completion_mistral() -> mistral.ChatCompletion:
    return mistral.ChatCompletion(
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