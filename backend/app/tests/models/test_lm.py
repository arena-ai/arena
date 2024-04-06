import os
from typing import Any, Mapping
from datetime import datetime

import pytest

from app.lm import models
from app.lm.models import openai, mistral, anthropic

from openai.types.chat.completion_create_params import CompletionCreateParams
from openai.types.chat.chat_completion import ChatCompletion, ChoiceLogprobs, ChatCompletionTokenLogprob, ChatCompletionMessage, CompletionUsage, Choice
from mistralai.client import ChatCompletionResponse
from mistralai.models.chat_completion import ChatMessage, ChatCompletionResponse, ChatCompletionResponseChoice, FinishReason, UsageInfo, ToolCall, FunctionCall
from anthropic.types import MessageCreateParams, Message, ContentBlock, Usage

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


@pytest.fixture
def chat_completion_mistral() -> ChatCompletionResponse:
    # Let's create instances of the nested classes first
    function_call = FunctionCall(name="function_name", arguments="function_arguments")
    tool_call = ToolCall(id="tool_id", function=function_call)
    chat_message = ChatMessage(role="assistant", content="This is a message content", name="Assistant", tool_calls=[tool_call])
    finish_reason = FinishReason.stop
    chat_completion_response_choice = ChatCompletionResponseChoice(index=0, message=chat_message, finish_reason=finish_reason)
    usage_info = UsageInfo(prompt_tokens=10, completion_tokens=20, total_tokens=30)
    # Now, let's create an instance of ChatCompletionResponse
    chat_completion_response = ChatCompletionResponse(
        id="cmpl-123",
        object="chat.completion",
        created=int(datetime.now().timestamp()),
        model="text-davinci-002",
        choices=[chat_completion_response_choice],
        usage=usage_info
    )
    return chat_completion_response


@pytest.fixture
def chat_completion_create_anthropic() -> models.ChatCompletionCreate:
    return models.ChatCompletionCreate(**{
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Hello, Claude"},
            {"role": "assistant", "content": "Hi, I'm Claude. How can I help you?"},
        ],
        "model": "claude-2.0",
        "metadata": {"user_id": "123e4567-e89b-12d3-a456-426614174000"},
        "stop_sequences": ["Stop generating."],
        "system": "You are a helpful assistant.",
        "temperature": 0.8,
        "top_k": 0,
        "top_p": 1.0,
        "stream": True,
    })

@pytest.fixture
def chat_completion_anthropic() -> Message:
    return Message(
        id="0987654321",
        content=[ContentBlock(type="text", text="The best answer is (B)")],
        model="text-generation-model",
        role="assistant",
        stop_reason="stop_sequence",
        stop_sequence="B)",
        type="message",
        usage=Usage(input_tokens=10, output_tokens=20)
    )

# Test openai

def test_chat_completion_create_openai(chat_completion_create_openai) -> None:
    ccc: CompletionCreateParams = openai.chat_completion_create(chat_completion_create_openai)

def test_chat_completion_openai(chat_completion_openai) -> None:
    cc: models.ChatCompletion = openai.chat_completion(chat_completion_openai)

def test_chat_completion_create_mistral(chat_completion_create_mistral) -> None:
    m: Mapping[str, Any] = mistral.chat_completion_create(chat_completion_create_mistral)

def test_chat_completion_mistral(chat_completion_mistral) -> None:
    cc: models.ChatCompletion = mistral.chat_completion(chat_completion_mistral)

def test_chat_completion_create_anthropic(chat_completion_create_anthropic) -> None:
    mcp: MessageCreateParams = anthropic.chat_completion_create(chat_completion_create_anthropic)

def test_chat_completion_anthropic(chat_completion_anthropic) -> None:
    cc: models.ChatCompletion = anthropic.chat_completion(chat_completion_anthropic)
