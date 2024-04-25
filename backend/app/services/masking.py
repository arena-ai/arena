from typing import Mapping, Sequence, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cached_property

from fastapi import APIRouter
from sqlmodel import func, select
import httpx

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.lm.models import ChatCompletionResponse, ChatCompletionRequest, openai, mistral, anthropic
from app.core.config import settings



@dataclass
class Analyzer:
    url: str = f"http://{settings.PRESIDIO_ANALYZER_SERVER}:{settings.PRESIDIO_ANALYZER_PORT}/analyze"

    async def analyze(self, ccc: openai.ChatCompletionRequest) -> openai.ChatCompletionResponse:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url=f"{self.url}/chat/completions",
                headers=self.headers,
                json=ccc.model_dump(exclude_unset=True, exclude_none=True),
            )
            return openai.ChatCompletionResponse.model_validate(response.raise_for_status().json())

    async def chat_completion(self, ccc: ChatCompletionRequest) -> ChatCompletionResponse:
        return (await self.openai_chat_completion(openai.ChatCompletionRequest.from_chat_completion_request(ccc))).to_chat_completion_response()
