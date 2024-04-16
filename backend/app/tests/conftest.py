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
from app.lm.models import openai, mistral, anthropic


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