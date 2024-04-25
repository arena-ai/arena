from sqlmodel import Session
from anyio import run

from app.ops.utils import var, tup
from app.ops.lm import Chat, Judge
from app.lm.models import ChatCompletionCreate, Message


def test_chat(language_models_api_keys) -> None:
    lm = Chat()
    comp = lm(language_models_api_keys, ChatCompletionCreate(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France?")
        ]
    ))
    print(run(comp.evaluate).choices[0].message.content)
    

def test_judge(language_models_api_keys) -> None:
    chat = Chat()
    judge = Judge()
    req = ChatCompletionCreate(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Can you write a short poem about prime numbers?")
        ]
    )
    resp = chat(language_models_api_keys, req)
    comp = tup(resp.choices[0].message.content, judge(language_models_api_keys, req, resp))
    print(run(comp.evaluate))


def test_other_judge(language_models_api_keys) -> None:
    chat = Chat()
    judge = Judge()
    req = ChatCompletionCreate(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Can you give the first 10 even prime numbers?")
        ]
    )
    resp = chat(language_models_api_keys, req)
    comp = tup(resp.choices[0].message.content, judge(language_models_api_keys, req, resp))
    print(run(comp.evaluate))