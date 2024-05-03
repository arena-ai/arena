from sqlmodel import Session
from anyio import run

from app.models import LMConfig
from app.ops import tup
from app.ops.lm import openai, mistral, anthropic, chat, judge
from app.lm.models import ChatCompletionRequest, Message
import app.lm.models.openai as oai
import app.lm.models.mistral as mis
import app.lm.models.anthropic as ant


def test_openai_mistral_anthropic(language_models_api_keys) -> None:
    comp_oai = openai(language_models_api_keys.openai_api_key, oai.ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France?")
        ]
    ))
    comp_mis = mistral(language_models_api_keys.mistral_api_key, mis.ChatCompletionRequest(
        model="mistral-small",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France?")
        ]
    ))
    comp_ant = anthropic(language_models_api_keys.anthropic_api_key, ant.ChatCompletionRequest(
        model="claude-2.0",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France?")
        ]
    ))
    print(run(tup(comp_oai, comp_mis, comp_ant).evaluate))


def test_chat(language_models_api_keys) -> None:
    comp = chat(language_models_api_keys, ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France?")
        ]
    )).content
    print(run(comp.evaluate).choices[0].message.content)
    

def test_judge(language_models_api_keys) -> None:
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
    comp = chat(language_models_api_keys, ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France?")
        ],
        lm_config=LMConfig(judge_evaluation=True)
    )).content
    print(run(comp.evaluate).choices[0].message.content)