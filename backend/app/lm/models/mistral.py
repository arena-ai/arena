from typing import Literal, Mapping, Sequence, Any

from pydantic import BaseModel

from app.lm import models
from app.lm.models import (
    ChatCompletionToolParam,
    Message,
    ResponseFormatBase,
)

"""
models.ChatCompletionCreate -> ChatCompletionCreate -> ChatCompletion -> models.ChatCompletion
"""

MODELS = (
    "mistral-large-latest",
    "mistral-medium",
    "mistral-medium-latest",
    "mistral-small",
    "mistral-small-latest",
    "mistral-tiny",
    "open-mistral-7b",
    "open-mixtral-8x7b",
)


class ChatCompletionRequest(BaseModel):
    """
    Maps to:
    https://github.com/mistralai/client-python/blob/main/src/mistralai/client.py#L153
    https://github.com/mistralai/client-python/blob/main/src/mistralai/models/chat_completion.py
    https://docs.mistral.ai/api/#operation/createChatCompletion
    """

    messages: Sequence[Message]
    model: str | Literal[*MODELS]
    max_tokens: int | None = None
    response_format: ResponseFormatBase | None = None
    safe_prompt: bool | None = None
    random_seed: int | None = None
    temperature: float | None = None
    tool_choice: Literal["none", "auto", "any"] | None = None
    tools: Sequence[ChatCompletionToolParam] | None = None
    top_p: float | None = None
    stream: bool | None = None

    @classmethod
    def from_chat_completion_request(
        cls, ccc: models.ChatCompletionRequest
    ) -> "ChatCompletionRequest":
        ccc = ccc.model_dump(exclude_none=True)
        if "seed" in ccc:
            ccc["random_seed"] = ccc["seed"]
            del ccc["seed"]
        if "lm_config" in ccc:
            del ccc["lm_config"]
        if "temperature" in ccc:
            ccc["temperature"] = min(1.0, max(0.0, ccc["temperature"]))
        else:
            ccc["temperature"] = 1.0
        return ChatCompletionRequest.model_validate(ccc)

    def to_dict(self) -> Mapping[str, Any]:
        return self.model_dump(exclude_none=True)


class ChatCompletionResponse(models.ChatCompletionResponse):
    """
    https://github.com/mistralai/client-python/blob/main/src/mistralai/models/chat_completion.py#L86
    """

    @classmethod
    def from_dict(cls, m: Mapping[str, Any]) -> "ChatCompletionResponse":
        return ChatCompletionResponse.model_validate(m)

    def to_chat_completion_response(self) -> models.ChatCompletionResponse:
        return models.ChatCompletionResponse.model_validate(
            self.model_dump(exclude_none=True)
        )
