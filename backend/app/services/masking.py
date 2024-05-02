from typing import Mapping, Sequence, Literal, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, TypeAdapter

import httpx

from app.lm.models import ChatCompletionResponse, ChatCompletionRequest, openai, mistral, anthropic
from app.core.config import settings

class AnalyzerRequest(BaseModel):
    text: str
    language: str = "en"
    # From https://microsoft.github.io/presidio/supported_entities/
    entities: Sequence[str] | None = Field(default=None, description="""A list of values among the possible entities:
                                           PHONE_NUMBER, US_DRIVER_LICENSE, US_PASSPORT, LOCATION, CREDIT_CARD,
                                           CRYPTO, UK_NHS, US_SSN, US_BANK_NUMBER, EMAIL_ADDRESS, DATE_TIME,
                                           IP_ADDRESS, PERSON, IBAN_CODE, NRP, US_ITIN, MEDICAL_LICENSE, URL
                                           If entities=None then all entities are looked for.""") 
    
    correlation_id: str | None = None
    score_threshold: float | None = None
    log_decision_process: bool | None = None
    return_decision_process: bool | None = None


class AnalyzerResponseItem(BaseModel):
    entity_type: str
    start: int
    end: int
    score: float
    analysis_explanation: Mapping[str, Any] | None = None
    recognition_metadata: Mapping[str, Any] | None = None


analyzer_response = TypeAdapter(Sequence[AnalyzerResponseItem])


@dataclass
class Analyzer:
    url: str = f"http://{settings.PRESIDIO_ANALYZER_SERVER}:{settings.PRESIDIO_ANALYZER_PORT}/analyze"

    async def analyze(self, req: AnalyzerRequest) -> Sequence[AnalyzerResponseItem]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"{self.url}",
                json=req.model_dump(exclude_none=True),
            )
            try:
                return analyzer_response.validate_python(response.raise_for_status().json())
            except httpx.HTTPStatusError:
                return None


class Replace(BaseModel):
    type: Literal["replace"] = "replace"
    new_value: str | None = None

class Redact(BaseModel):
    type: Literal["redact"] = "redact"

class Mask(BaseModel):
    type: Literal["mask"] = "mask"
    masking_char: str
    chars_to_mask: int
    from_end: bool = False

class Hash(BaseModel):
    type: Literal["hash"] = "hash"
    hash_type: Literal["md5", "sha256", "sha512"] = "md5"

class Encrypt(BaseModel):
    type: Literal["encrypt"] = "encrypt"
    key: str

class Keep(BaseModel):
    type: Literal["keep"] = "keep"


class Anonymizers(BaseModel):
    # From https://microsoft.github.io/presidio/supported_entities/
    PHONE_NUMBER: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    US_DRIVER_LICENSE: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    US_PASSPORT: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    LOCATION: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    CREDIT_CARD: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    CRYPTO: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    UK_NHS: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    US_SSN: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    US_BANK_NUMBER: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    EMAIL_ADDRESS: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    DATE_TIME: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    IP_ADDRESS: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    PERSON: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    IBAN_CODE: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    NRP: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    US_ITIN: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    MEDICAL_LICENSE: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    URL: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None
    DEFAULT: Replace | Redact | Mask | Hash | Encrypt | Keep | None = None


class AnonymizerRequest(BaseModel):
    text: str
    anonymizers: Anonymizers | None = None
    analyzer_results: Sequence[AnalyzerResponseItem]


class AnonymizedItem(BaseModel):
    operator: str | None = None
    entity_type: str # From https://microsoft.github.io/presidio/supported_entities/
    start: int
    end: int
    text: str | None = None


anonymized_items = TypeAdapter(Sequence[AnonymizedItem])


class AnonymizerResponse(BaseModel):
    text: str
    items: Sequence[AnonymizedItem]


@dataclass
class Anonymizer:
    url: str = f"http://{settings.PRESIDIO_ANONYMIZER_SERVER}:{settings.PRESIDIO_ANONYMIZER_PORT}/anonymize"

    async def anonymize(self, req: AnonymizerRequest) -> AnonymizerResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"{self.url}",
                json=req.model_dump(exclude_none=True),
            )
            try:
                return AnonymizerResponse.model_validate(response.raise_for_status().json())
            except httpx.HTTPStatusError:
                return None
    