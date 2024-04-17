import os
from typing import Any, Mapping
from datetime import datetime

import pytest

from app.lm import models
from app.lm.models import openai, mistral, anthropic

from anthropic.types import MessageCreateParams, Message, ContentBlock, Usage

# Testing CreateChatCompletion -> CreateChatCompletionXXX


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
    ccc: Mapping = openai.ChatCompletionCreate.from_chat_completion_create(chat_completion_create_openai).to_dict()

def test_chat_completion_openai(chat_completion_openai) -> None:
    cc: Mapping = openai.ChatCompletion.from_chat_completion(chat_completion_openai).to_dict()

def test_chat_completion_create_mistral(chat_completion_create_mistral) -> None:
    m: Mapping = mistral.ChatCompletionCreate.from_chat_completion_create(chat_completion_create_mistral).to_dict()

def test_chat_completion_mistral(chat_completion_mistral) -> None:
    cc: Mapping = mistral.ChatCompletion.from_chat_completion(chat_completion_mistral).to_dict()

def test_chat_completion_create_anthropic(chat_completion_create_anthropic) -> None:
    mcp: MessageCreateParams = anthropic._chat_completion_create(chat_completion_create_anthropic)

def test_chat_completion_anthropic(chat_completion_anthropic) -> None:
    cc: models.ChatCompletion = anthropic.chat_completion(chat_completion_anthropic)
