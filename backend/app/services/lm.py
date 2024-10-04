from typing import Mapping, Mapping, Sequence, Any
from dataclasses import dataclass, field
from functools import cached_property

import httpx

from app.lm.models import LMApiKeys, ChatCompletionResponse, ChatCompletionRequest
from app.lm.models import openai, mistral, anthropic
from app.services import Service, Request, Response


@dataclass
class OpenAI(Service[openai.ChatCompletionRequest, openai.ChatCompletionResponse]):
    api_key: str = ""
    url: str = "https://api.openai.com/v1"
    models: tuple[str] = openai.MODELS
    
    @cached_property
    def headers(self) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    def request(self, req: openai.ChatCompletionRequest) -> Request[openai.ChatCompletionRequest]:
        return Request(
            method="POST",
            url=f"{self.url}/chat/completions",
            headers=self.headers,
            content=req,
        )
    
    def from_any(self, a: Any) -> openai.ChatCompletionResponse:
        return openai.ChatCompletionResponse.model_validate(a)

    def has_model(self, model: str) -> bool:
        """Return True if the model is from OpenAI"""
        return "gpt-4" in model or "gpt-3" in model or model in self.models
    
    async def openai_chat_completion(self, ccc: openai.ChatCompletionRequest) -> Response[openai.ChatCompletionResponse]:
        return await self.call(ccc)

    async def chat_completion(self, ccc: ChatCompletionRequest) -> Response[ChatCompletionResponse]:
        #print(cc)
        response = await self.openai_chat_completion(openai.ChatCompletionRequest.from_chat_completion_request(ccc))
        print(response)
        return Response(
            status_code=response.status_code,
            headers=response.headers,
            content=response.content.to_chat_completion_response()
        )


@dataclass
class Mistral(Service[mistral.ChatCompletionRequest, mistral.ChatCompletionResponse]):
    api_key: str = ""
    url: str = "https://api.mistral.ai"
    models: tuple[str] = mistral.MODELS

    @cached_property
    def headers(self) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    def request(self, req: mistral.ChatCompletionRequest) -> Request[mistral.ChatCompletionRequest]:
        return Request(
            method="POST",
            url=f"{self.url}/v1/chat/completions",
            headers=self.headers,
            content=req,
        )
    
    def from_any(self, a: Any) -> mistral.ChatCompletionResponse:
        return mistral.ChatCompletionResponse.model_validate(a)
    
    def has_model(self, model: str) -> bool:
        """Return True if the model is from Mistral"""
        return "open-mistral-" in model or "open-mixtral-" in model or "mistral-" in model or model in self.models
    
    async def mistral_chat_completion(self, ccc: mistral.ChatCompletionRequest) -> Response[mistral.ChatCompletionResponse]:
        return await self.call(ccc)

    async def chat_completion(self, ccc: ChatCompletionRequest) -> Response[ChatCompletionResponse]:
        response = await self.mistral_chat_completion(mistral.ChatCompletionRequest.from_chat_completion_request(ccc))
        return Response(
            status_code=response.status_code,
            headers=response.headers,
            content=response.content.to_chat_completion_response()
        )


@dataclass
class Anthropic(Service[anthropic.ChatCompletionRequest, anthropic.ChatCompletionResponse]):
    api_key: str = ""
    url: str = "https://api.anthropic.com"
    models: tuple[str] = anthropic.MODELS

    @cached_property
    def headers(self) -> Mapping[str, str]:
        return {
            "x-api-key": f"{self.api_key}",
            "anthropic-version": "2023-06-01",
        }

    def request(self, req: anthropic.ChatCompletionRequest) -> Request[anthropic.ChatCompletionRequest]:
        return Request(
            method="POST",
            url=f"{self.url}/v1/messages",
            headers=self.headers,
            content=req,
        )
    
    def from_any(self, a: Any) -> anthropic.ChatCompletionResponse:
        return anthropic.ChatCompletionResponse.model_validate(a)
    
    def has_model(self, model: str) -> bool:
        """Return True if the model is from Anthropic"""
        return "claude-" in model or model in self.models
    
    async def anthropic_chat_completion(self, ccc: anthropic.ChatCompletionRequest) -> Response[anthropic.ChatCompletionRequest]:
        return await self.call(ccc)
    
    async def chat_completion(self, ccc: ChatCompletionRequest) -> Response[ChatCompletionResponse]:
        response = await self.anthropic_chat_completion(anthropic.ChatCompletionRequest.from_chat_completion_request(ccc))
        return Response(
            status_code=response.status_code,
            headers=response.headers,
            content=response.content.to_chat_completion_response()
        )


@dataclass
class LanguageModels:
    api_keys: LMApiKeys
    timeout: httpx.Timeout = field(default_factory=lambda: httpx.Timeout(30., read=None))

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

    def request(self, req: ChatCompletionRequest) -> Request[ChatCompletionRequest]:
        for service in self.services:
            if service.has_model(req.model):
                return service.request(req=req)
        raise ValueError(req.model)

    async def chat_completion(self, ccc: ChatCompletionRequest) -> Response[ChatCompletionResponse]:
        for service in self.services:
            if service.has_model(ccc.model):
                return await service.chat_completion(ccc=ccc)
        raise ValueError(ccc.model)

