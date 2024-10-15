import os
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings


def test_create_setting(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    data = {
        "name": "OPENAI_API_KEY",
        "content": os.getenv("ARENA_OPENAI_API_KEY"),
    }
    response = client.post(
        f"{settings.API_V1_STR}/settings/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["content"] == data["content"]
