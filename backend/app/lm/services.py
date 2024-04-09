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

    def native(self, ccc: Mapping) -> ChatCompletionOpenAI:
        client = OpenAIClient(api_key=self.api_key)
        return client.chat.completions.create(**ccc)

    def call(self, ccc: ChatCompletionCreate) -> ChatCompletion:
        return openai.chat_completion(self.native(openai.chat_completion_create(ccc)))


@dataclass
class Mistral:
    api_key: str
        
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

    def native(self, ccc: Mapping) -> ChatCompletionAnthropic:
        client = AnthropicClient(api_key=self.api_key)
        return client.messages.create(**ccc)

    def call(self, ccc: ChatCompletionCreate) -> ChatCompletion:
        return anthropic.chat_completion(self.native(anthropic.chat_completion_create(ccc)))
