from typing import Mapping, Sequence, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cached_property

from fastapi import APIRouter
from sqlmodel import func, select
import httpx

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.lm.models import ChatCompletion, ChatCompletionCreate, openai, mistral, anthropic
from app.core.config import settings



@dataclass
class Analyzer:
    url: str = f"http://{settings.PRESIDIO_ANALYZER_SERVER}:{settings.PRESIDIO_ANALYZER_PORT}/analyze"

    async def analyze(self, ccc: openai.ChatCompletionCreate) -> openai.ChatCompletion:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url=f"{self.url}/chat/completions",
                headers=self.headers,
                json=ccc.model_dump(exclude_unset=True, exclude_none=True),
            )
            return openai.ChatCompletion.model_validate(response.raise_for_status().json())

    async def chat_completion(self, ccc: ChatCompletionCreate) -> ChatCompletion:
        return (await self.openai_chat_completion(openai.ChatCompletionCreate.from_chat_completion_create(ccc))).to_chat_completion()
