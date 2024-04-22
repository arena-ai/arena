import os

from anyio import run
from sqlmodel import Session, select

from app import crud
from app.models import UserCreate, Event
from app.ops.utils import var
from app.ops.lm import Arena
from app.lm.models import ChatCompletion, ChatCompletionCreate, Message


def test_arena(db: Session) -> None:
    lm = Arena(
        openai_api_key=os.getenv("ARENA_OPENAI_API_KEY"),
        mistral_api_key=os.getenv("ARENA_MISTRAL_API_KEY"),
        anthropic_api_key=os.getenv("ARENA_ANTHROPIC_API_KEY"),
    )
    comp = lm(var("chat_completion_create", ChatCompletionCreate(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France?")
        ]
    )))
    print(run(comp.evaluate).content)
    