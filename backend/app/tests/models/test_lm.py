import pytest

from app.lm.models import (
    ChatCompletionCreate,
    Choice, FinishReason,
    ChatCompletionMessage,
    # CreateChatCompletion, CreateChatCompletionOpenAI, CreateChatCompletionMistral, CreateChatCompletionAnthropic,
    # ChatCompletionOpenAI, ChatCompletionMistral, ChatCompletionAnthropic, ChatCompletion
    )

# Testing CreateChatCompletion -> CreateChatCompletionXXX

@pytest.fixture
def chat_completion_create_openai() -> ChatCompletionCreate:
    return ChatCompletionCreate(**{
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

# Test openai

def test_chat_completion_create_openai(chat_completion_create_openai) -> None:
    print(chat_completion_create_openai)


# Testing finish_reason

def test_finish_reason() -> None:
    c = Choice.model_validate({
        "finish_reason": FinishReason.stop,
        "index": 0,
        "message": ChatCompletionMessage()
    })
    assert c.finish_reason == "stop"

