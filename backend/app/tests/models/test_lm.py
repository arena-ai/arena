import os

import pytest

from app.lm import models
from app.lm.models import openai, mistral

from openai.types.chat.completion_create_params import CompletionCreateParams
from openai.types.chat.chat_completion import ChatCompletion, ChoiceLogprobs, ChatCompletionTokenLogprob, ChatCompletionMessage, CompletionUsage, Choice
from mistralai.client import MistralClient
from anthropic import Anthropic

# Testing CreateChatCompletion -> CreateChatCompletionXXX

@pytest.fixture
def chat_completion_create_openai() -> models.ChatCompletionCreate:
    return models.ChatCompletionCreate(**{
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
def chat_completion_openai() -> ChatCompletion:
    return ChatCompletion(
        id="cmpl-123",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                logprobs=ChoiceLogprobs(
                    content=[
                        ChatCompletionTokenLogprob(
                            token="Hello",
                            logprob=-1.34,
                            top_logprobs=[],
                            text_offset=None,
                        ),
                        ChatCompletionTokenLogprob(
                            token="world!",
                            logprob=-1.19,
                            top_logprobs=[],
                            text_offset=None,
                        ),
                    ]
                ),
                message=ChatCompletionMessage(
                    role="assistant", content="Hello world!"
                ),
            )
        ],
        created=1672463200,
        model="gpt-3.5-turbo",
        object="chat.completion",
        system_fingerprint="0x1234abcd",
        usage=CompletionUsage(
            prompt_tokens=5,
            completion_tokens=10,
            total_tokens=15,
        ),
    )

@pytest.fixture
def chat_completion_create_mistral() -> models.ChatCompletionCreate:
    return models.ChatCompletionCreate(**{
        "model": "mistral-small",
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

# Test openai

def test_chat_completion_create_openai(chat_completion_create_openai) -> None:
    ccc: CompletionCreateParams = openai.chat_completion_create(chat_completion_create_openai)

def test_chat_completion_openai(chat_completion_openai) -> None:
    cc: models.ChatCompletion = openai.chat_completion(chat_completion_openai)

def test_chat_completion_create_mistral(chat_completion_create_mistral) -> None:
    ccc: CompletionCreateParams = mistral.chat_completion_create(chat_completion_create_mistral)

# def test_chat_completion_openai(chat_completion_openai) -> None:
#     cc: models.ChatCompletion = chat_completion(chat_completion_openai)

# Testing finish_reason

# def test_finish_reason() -> None:
#     c = Choice.model_validate({
#         "finish_reason": FinishReason.stop,
#         "index": 0,
#         "message": ChatCompletionMessage()
#     })
#     assert c.finish_reason == "stop"

