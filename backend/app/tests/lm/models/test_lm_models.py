from typing import Mapping

from app.lm.models import openai, mistral, anthropic

# Testing CreateChatCompletion -> CreateChatCompletionXXX

# Test openai


def test_chat_completion_create_openai(chat_completion_create_openai) -> None:
    ccc: Mapping = openai.ChatCompletionRequest.from_chat_completion_request(
        chat_completion_create_openai
    ).to_dict()


def test_chat_completion_openai(chat_completion_openai) -> None:
    cc: openai.ChatCompletionResponse = (
        openai.ChatCompletionResponse.from_dict(
            chat_completion_openai.model_dump()
        ).to_chat_completion_response()
    )


def test_chat_completion_create_mistral(
    chat_completion_create_mistral,
) -> None:
    m: Mapping = mistral.ChatCompletionRequest.from_chat_completion_request(
        chat_completion_create_mistral
    ).to_dict()


def test_chat_completion_mistral(chat_completion_mistral) -> None:
    cc: mistral.ChatCompletionResponse = (
        mistral.ChatCompletionResponse.from_dict(
            chat_completion_mistral.model_dump()
        ).to_chat_completion_response()
    )


def test_chat_completion_create_anthropic(
    chat_completion_create_anthropic,
) -> None:
    mcp: Mapping = (
        anthropic.ChatCompletionRequest.from_chat_completion_request(
            chat_completion_create_anthropic
        ).to_dict()
    )


def test_chat_completion_anthropic(chat_completion_anthropic) -> None:
    cc: anthropic.ChatCompletionResponse = (
        anthropic.ChatCompletionResponse.from_dict(
            chat_completion_anthropic
        ).to_chat_completion_response()
    )
