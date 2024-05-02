from typing import Mapping, Sequence, Literal, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

import httpx

from app.lm.models import ChatCompletionResponse, ChatCompletionRequest, openai, mistral, anthropic
from app.core.config import settings

class AnalyzerRequest(BaseModel):
    text: str
    language: str = "en"
    entities: Sequence[str] | None = Field(default=None, description="""A list of values among the possible entities:
                                           PHONE_NUMBER, US_DRIVER_LICENSE, US_PASSPORT, LOCATION, CREDIT_CARD,
                                           CRYPTO, UK_NHS, US_SSN, US_BANK_NUMBER, EMAIL_ADDRESS, DATE_TIME,
                                           IP_ADDRESS, PERSON, IBAN_CODE, NRP, US_ITIN, MEDICAL_LICENSE, URL
                                           If entities=None then all entities are looked for.""") 
    
    correlation_id: str | None = None
    score_threshold: float | None = None
    log_decision_process: bool | None = None
    return_decision_process: bool | None = None



@dataclass
class Analyzer:
    url: str = f"http://{settings.PRESIDIO_ANALYZER_SERVER}:{settings.PRESIDIO_ANALYZER_PORT}/analyze"

    async def analyze(self, req: AnalyzerRequest) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"{self.url}",
                json=req.model_dump(exclude_none=True),
            )
            return response.raise_for_status().json()
