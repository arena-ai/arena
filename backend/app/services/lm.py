from typing import Mapping, Sequence, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cached_property

from fastapi import APIRouter
from sqlmodel import func, select
import httpx

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.lm.models import LanguageModelsApiKeys, ChatCompletionResponse, ChatCompletionRequest, openai, mistral, anthropic


@dataclass
class Service(ABC):
    api_key: str

    @abstractmethod
    async def chat_completion(self, ccc: ChatCompletionRequest) -> ChatCompletionResponse:
        pass


@dataclass
class OpenAI(Service):
    timeout: httpx.Timeout = field(default_factory=lambda: httpx.Timeout(30., read=None))
    url: str = "https://api.openai.com/v1"
    models: tuple[str] = (
        "gpt-4-turbo",
        "gpt-4-turbo-2024-04-09",
        "gpt-4-0125-preview",
        "gpt-4-turbo-preview",
        "gpt-4-1106-preview",
        "gpt-4-vision-preview",
        "gpt-4",
        "gpt-4-0314",
        "gpt-4-0613",
        "gpt-4-32k",
        "gpt-4-32k-0314",
        "gpt-4-32k-0613",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-16k-0613",
        )
    
    @cached_property
    def headers(self) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    async def openai_chat_completion(self, ccc: openai.ChatCompletionRequest) -> openai.ChatCompletionResponse:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url=f"{self.url}/chat/completions",
                headers=self.headers,
                json=ccc.model_dump(exclude_unset=True, exclude_none=True),
            )
            return openai.ChatCompletionResponse.model_validate(response.raise_for_status().json())

    async def chat_completion(self, ccc: ChatCompletionRequest) -> ChatCompletionResponse:
        return (await self.openai_chat_completion(openai.ChatCompletionRequest.from_chat_completion_request(ccc))).to_chat_completion_response()


@dataclass
class Mistral(Service):
    timeout: httpx.Timeout = field(default_factory=lambda: httpx.Timeout(30., read=None))
    url: str = "https://api.mistral.ai"
    models: tuple[str] = ("mistral-embed", "mistral-large-2402", "mistral-large-latest", "mistral-medium", "mistral-medium-2312", "mistral-medium-latest", "mistral-small", "mistral-small-2312", "mistral-small-2402", "mistral-small-latest", "mistral-tiny", "mistral-tiny-2312", "open-mistral-7b", "open-mixtral-8x7b")

    @cached_property
    def headers(self) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    async def mistral_chat_completion(self, ccc: mistral.ChatCompletionRequest) -> mistral.ChatCompletionResponse:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url=f"{self.url}/v1/chat/completions",
                headers=self.headers,
                json=ccc.model_dump(exclude_unset=True, exclude_none=True),
            )
            return mistral.ChatCompletionResponse.model_validate(response.raise_for_status().json())

    async def chat_completion(self, ccc: ChatCompletionRequest) -> ChatCompletionResponse:
        return (await self.mistral_chat_completion(mistral.ChatCompletionRequest.from_chat_completion_request(ccc))).to_chat_completion_response()

@dataclass
class Anthropic(Service):
    timeout: httpx.Timeout = field(default_factory=lambda: httpx.Timeout(30., read=None))
    url: str = "https://api.anthropic.com"
    models: tuple[str] = ("claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-2.1", "claude-2.0", "claude-instant-1.2")

    @cached_property
    def headers(self) -> Mapping[str, str]:
        return {
            "x-api-key": f"{self.api_key}",
            "anthropic-version": "2023-06-01",
        }

    async def anthropic_chat_completion(self, ccc: anthropic.ChatCompletionRequest) -> anthropic.ChatCompletionResponse:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url=f"{self.url}/v1/messages",
                headers=self.headers,
                json=ccc.model_dump(exclude_unset=True, exclude_none=True),
            )
            return anthropic.ChatCompletionResponse.model_validate(response.raise_for_status().json())

    async def chat_completion(self, ccc: ChatCompletionRequest) -> ChatCompletionResponse:
        return (await self.anthropic_chat_completion(anthropic.ChatCompletionRequest.from_chat_completion_request(ccc))).to_chat_completion_response()


@dataclass
class LanguageModels:
    api_keys: LanguageModelsApiKeys
    timeout = httpx.Timeout(30., read=None)

    @cached_property
    def openai(self) -> OpenAI:
        return OpenAI(api_key=self.api_keys.openai_api_key, timeout=self.timeout)

    @cached_property
    def mistral(self) -> Mistral:
        return Mistral(api_key=self.api_keys.mistral_api_key, timeout=self.timeout)
    
    @cached_property
    def anthropic(self) -> Anthropic:
        return Anthropic(api_key=self.api_keys.anthropic_api_key, timeout=self.timeout)
    
    @cached_property
    def services(self) -> Sequence[Service]:
        return [self.openai, self.mistral, self.anthropic]

    async def chat_completion(self, ccc: ChatCompletionRequest) -> ChatCompletionResponse:
        for service in self.services:
            if ccc.model in service.models:
                return await service.chat_completion(ccc=ccc)
        raise ValueError(ccc.model)
        