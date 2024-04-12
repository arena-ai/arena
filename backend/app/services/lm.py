from typing import Mapping, Any
from dataclasses import dataclass

from fastapi import APIRouter
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.lm.models import ChatCompletion, ChatCompletionCreate, openai, mistral, anthropic

from openai import OpenAI as OpenAIClient
from openai.types.chat.chat_completion import ChatCompletion as ChatCompletionOpenAI
from openai.types.chat.completion_create_params import CompletionCreateParams as ChatCompletionCreateOpenAI

from mistralai.client import MistralClient, MistralException
from mistralai.models.chat_completion import ChatCompletionResponse as ChatCompletionMistral

from anthropic import Anthropic as AnthropicClient
from anthropic.types import MessageCreateParams as ChatCompletionCreateAnthropic, Message as ChatCompletionAnthropic


@dataclass
class OpenAI:
    api_key: str
    models: list[str] = ("gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-4-vision-preview", "gpt-4", "gpt-4-0314", "gpt-4-0613", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-0613", "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-16k-0613")

    def native(self, ccc: Mapping) -> ChatCompletionOpenAI:
        client = OpenAIClient(api_key=self.api_key)
        return client.chat.completions.create(**ccc)

    def call(self, ccc: ChatCompletionCreate) -> ChatCompletion:
        return openai.chat_completion(self.native(openai.chat_completion_create(ccc)))


@dataclass
class Mistral:
    api_key: str
    models: list[str] = ("mistral-embed", "mistral-large-2402", "mistral-large-latest", "mistral-medium", "mistral-medium-2312", "mistral-medium-latest", "mistral-small", "mistral-small-2312", "mistral-small-2402", "mistral-small-latest", "mistral-tiny", "mistral-tiny-2312", "open-mistral-7b", "open-mixtral-8x7b")
        
    def native(self, ccc: Mapping) -> ChatCompletionMistral:
        client = MistralClient(api_key=self.api_key)
        request = client._make_chat_request(**ccc)
        single_response = client._request("post", request, "v1/chat/completions")
        for response in single_response:
            return ChatCompletionMistral(**response)
        raise MistralException("No response received")

    def call(self, ccc: ChatCompletionCreate) -> ChatCompletion:
        return mistral.chat_completion(self.native(mistral.chat_completion_create(ccc)))


@dataclass
class Anthropic:
    api_key: str
    models: list[str] = ("claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-2.1", "claude-2.0", "claude-instant-1.2")

    def native(self, ccc: Mapping) -> ChatCompletionAnthropic:
        client = AnthropicClient(api_key=self.api_key)
        return client.messages.create(**ccc)

    def call(self, ccc: ChatCompletionCreate) -> ChatCompletion:
        return anthropic.chat_completion(self.native(anthropic.chat_completion_create(ccc)))


@dataclass
class Arena:
    openai_api_key: str
    mistral_api_key: str
    anthropic_api_key: str

    def call(self, ccc: ChatCompletionCreate) -> ChatCompletion:
        for service in [OpenAI(api_key=self.openai_api_key), Mistral(api_key=self.openai_api_key), Anthropic(api_key=self.anthropic_api_key)]:
            if ccc.model in service.models:
                return service.call(ccc=ccc)
        raise ValueError(ccc.model)
        