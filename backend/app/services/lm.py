from typing import Mapping, Any
from dataclasses import dataclass
from functools import cached_property

from fastapi import APIRouter
from sqlmodel import func, select
import httpx

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.lm.models import ChatCompletion, ChatCompletionCreate, openai, mistral, anthropic


@dataclass
class OpenAI:
    api_key: str
    timeout = httpx.Timeout(30., read=None)
    url = "https://api.openai.com/v1"
    models: list[str] = ("gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-4-vision-preview", "gpt-4", "gpt-4-0314", "gpt-4-0613", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-0613", "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-16k-0613")
    
    @cached_property
    def headers(self) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    async def chat_completion(self, ccc: openai.ChatCompletionCreate) -> openai.ChatCompletion:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url=f"{self.url}/chat/completions",
                headers=self.headers,
                json=ccc.model_dump(exclude_unset=True, exclude_none=True),
            )
            return openai.ChatCompletion.model_validate(response.raise_for_status().json())



@dataclass
class Mistral:
    api_key: str
    timeout = httpx.Timeout(30., read=None)
    url = "https://api.mistral.ai"
    models: list[str] = ("mistral-embed", "mistral-large-2402", "mistral-large-latest", "mistral-medium", "mistral-medium-2312", "mistral-medium-latest", "mistral-small", "mistral-small-2312", "mistral-small-2402", "mistral-small-latest", "mistral-tiny", "mistral-tiny-2312", "open-mistral-7b", "open-mixtral-8x7b")

    @cached_property
    def headers(self) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    async def chat_completion(self, ccc: mistral.ChatCompletionCreate) -> mistral.ChatCompletion:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url=f"{self.url}/v1/chat/completions",
                headers=self.headers,
                json=ccc.model_dump(exclude_unset=True, exclude_none=True),
            )
            return mistral.ChatCompletion.model_validate(response.raise_for_status().json())


@dataclass
class Anthropic:
    api_key: str
    timeout = httpx.Timeout(30., read=None)
    url = "https://api.anthropic.com"
    models: list[str] = ("claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-2.1", "claude-2.0", "claude-instant-1.2")

    @cached_property
    def headers(self) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    async def chat_completion(self, ccc: anthropic.ChatCompletionCreate) -> anthropic.ChatCompletion:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url=f"{self.url}/v1/messages",
                headers=self.headers,
                json=ccc.model_dump(exclude_unset=True, exclude_none=True),
            )
            return anthropic.ChatCompletion.model_validate(response.raise_for_status().json())


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
        