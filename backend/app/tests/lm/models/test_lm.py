import os
from typing import Any, Mapping
from datetime import datetime

import pytest

from app.lm import models
from app.lm.models import openai, mistral, anthropic

from anthropic.types import MessageCreateParams, Message, ContentBlock, Usage

# Testing CreateChatCompletion -> CreateChatCompletionXXX

# Test openai

def test_chat_completion_create_openai(chat_completion_create_openai) -> None:
    ccc: Mapping = openai.ChatCompletionCreate.from_chat_completion_create(chat_completion_create_openai).to_dict()

def test_chat_completion_openai(chat_completion_openai) -> None:
    cc: openai.ChatCompletion = openai.ChatCompletion.from_dict(chat_completion_openai.model_dump()).to_chat_completion()

def test_chat_completion_create_mistral(chat_completion_create_mistral) -> None:
    m: Mapping = mistral.ChatCompletionCreate.from_chat_completion_create(chat_completion_create_mistral).to_dict()

def test_chat_completion_mistral(chat_completion_mistral) -> None:
    cc: mistral.ChatCompletion = mistral.ChatCompletion.from_dict(chat_completion_mistral.model_dump()).to_chat_completion()

def test_chat_completion_create_anthropic(chat_completion_create_anthropic) -> None:
    mcp: Mapping = anthropic.ChatCompletionCreate.from_chat_completion_create(chat_completion_create_anthropic).to_dict()

def test_chat_completion_anthropic(chat_completion_anthropic) -> None:
    cc: anthropic.ChatCompletion = anthropic.ChatCompletion.from_dict(chat_completion_anthropic).to_chat_completion()
