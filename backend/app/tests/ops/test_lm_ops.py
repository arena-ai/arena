from sqlmodel import Session
from anyio import run

from app.ops import tup
from app.ops.lm import OpenAI, Mistral, Anthropic, Chat, Judge
from app.lm.models import ChatCompletionRequest, Message, openai, mistral, anthropic, ArenaParameters


def test_openai_mistral_anthropic(language_models_api_keys) -> None:
    oai = OpenAI()
    mis = Mistral()
    ant = Anthropic()
    comp_oai = oai(language_models_api_keys.openai_api_key, openai.ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France?")
        ]
    ))
    comp_mis = mis(language_models_api_keys.mistral_api_key, mistral.ChatCompletionRequest(
        model="mistral-small",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France?")
        ]
    ))
    comp_ant = ant(language_models_api_keys.anthropic_api_key, anthropic.ChatCompletionRequest(
        model="claude-2.0",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France?")
        ]
    ))
    print(run(tup(comp_oai, comp_mis, comp_ant).evaluate))


def test_chat(language_models_api_keys) -> None:
    lm = Chat()
    comp = lm(language_models_api_keys, ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France?")
        ]
    )).content
    print(run(comp.evaluate).choices[0].message.content)
    

def test_judge(language_models_api_keys) -> None:
    chat = Chat()
    judge = Judge()
    req = ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Can you write a short poem about prime numbers?")
        ]
    )
    resp = chat(language_models_api_keys, req).content
    comp = tup(resp.choices[0].message.content, judge(language_models_api_keys, req, resp))
    print(run(comp.evaluate))


def test_other_judge(language_models_api_keys) -> None:
    chat = Chat()
    judge = Judge()
    req = ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Can you give the first 10 even prime numbers?")
        ]
    )
    resp = chat(language_models_api_keys, req).content
    comp = tup(resp.choices[0].message.content, judge(language_models_api_keys, req, resp))
    print(run(comp.evaluate))

def test_chat_judge(language_models_api_keys) -> None:
    lm = Chat()
    comp = lm(language_models_api_keys, ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France?")
        ],
        arena_parameters=ArenaParameters(judge_evaluation=True)
    )).content
    print(run(comp.evaluate).choices[0].message.content)