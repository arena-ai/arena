import os
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from random import random

from app.models import Event, EventIdentifier
from app.core.config import settings
from app.lm.models import ChatCompletionRequest, Evaluation, Score


def test_evaluation(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session, chat_input_gen
) -> None:
    # Setup all tokens
    for api in ["OPENAI", "MISTRAL", "ANTHROPIC"]:
        print(f"Set {api} token")
        client.post(
            f"{settings.API_V1_STR}/settings",
            headers=superuser_token_headers,
            json={"name": f"{api}_API_KEY", "content": os.getenv(f"ARENA_{api}_API_KEY")},
        )
    for ccc in [
        (ChatCompletionRequest(**chat_input_gen("gpt-3.5-turbo"))),
        (ChatCompletionRequest(**chat_input_gen("mistral-small"))),
        (ChatCompletionRequest(**chat_input_gen("claude-2.1"))),
        ]:
        # Call Arena
        response = client.post(
            f"{settings.API_V1_STR}/lm/chat/completions",
            headers = superuser_token_headers,
            json = ccc.to_dict()
        )
        assert response.status_code == 200
        eval = client.post(
            f"{settings.API_V1_STR}/lm/evaluation",
            headers = superuser_token_headers,
            json = Evaluation(identifier=response.json()['id'], score=Score(value=random())).model_dump(mode="json")
        )
        assert eval.status_code == 200
    events = db.exec(select(Event).where(Event.name=="evaluation")).all()
    for event in events:
        print(event)


def test_evaluation_get(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session, chat_input_gen
) -> None:
    # Setup all tokens
    for api in ["OPENAI", "MISTRAL", "ANTHROPIC"]:
        print(f"Set {api} token")
        client.post(
            f"{settings.API_V1_STR}/settings",
            headers=superuser_token_headers,
            json={"name": f"{api}_API_KEY", "content": os.getenv(f"ARENA_{api}_API_KEY")},
        )
    for ccc in [
        (ChatCompletionRequest(**chat_input_gen("gpt-3.5-turbo"))),
        (ChatCompletionRequest(**chat_input_gen("mistral-small"))),
        (ChatCompletionRequest(**chat_input_gen("claude-2.1"))),
        ]:
        # Call Arena
        response = client.post(
            f"{settings.API_V1_STR}/lm/chat/completions",
            headers = superuser_token_headers,
            json = ccc.to_dict()
        )
        assert response.status_code == 200
        eval = client.get(
            f"{settings.API_V1_STR}/lm/evaluation/{response.json()['id']}/{random()}",
            headers = superuser_token_headers,
        )
        assert eval.status_code == 200
    events = db.exec(select(Event).where(Event.name.in_(["evaluation", "chat_completion_request"]))).all()
    for event in events:
        print(event)
