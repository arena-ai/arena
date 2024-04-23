from anyio import run
from sqlmodel import Session, select

from app.ops.utils import var
from app.ops.lm import Chat
from app.lm.models import ChatCompletionCreate, Message


def test_language_models(db: Session, language_models_api_keys) -> None:
    lm = Chat(api_keys=language_models_api_keys)
    comp = lm(var("chat_completion_create", ChatCompletionCreate(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France?")
        ]
    )))
    print(run(comp.evaluate).choices[0].message.content)
    