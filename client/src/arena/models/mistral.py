from typing import Literal, Mapping, Sequence, Any

from pydantic import BaseModel

from arena import models
from arena.models import Function, FunctionDefinition, ChatCompletionToolParam, Message, ResponseFormat, TopLogprob, TokenLogprob, ChoiceLogprobs, Choice, CompletionUsage

"""
models.ChatCompletionCreate -> ChatCompletionCreate -> ChatCompletion -> models.ChatCompletion
"""

class ChatCompletionRequest(BaseModel):
    """
    Maps to:
    https://github.com/mistralai/client-python/blob/main/src/mistralai/client.py#L153
    https://github.com/mistralai/client-python/blob/main/src/mistralai/models/chat_completion.py
    https://docs.mistral.ai/api/#operation/createChatCompletion
    """
    messages: Sequence[Message]
    model: str | Literal["mistral-embed", "mistral-large-2402", "mistral-large-latest", "mistral-medium", "mistral-medium-2312", "mistral-medium-latest", "mistral-small", "mistral-small-2312", "mistral-small-2402", "mistral-small-latest", "mistral-tiny", "mistral-tiny-2312", "open-mistral-7b", "open-mixtral-8x7b"]
    max_tokens: int | None = None
    response_format: ResponseFormat | None = None
    safe_prompt: bool | None = None
    random_seed: int | None = None
    temperature: float | None = None
    tool_choice: Literal["none", "auto", "any"] | None = None
    tools: Sequence[ChatCompletionToolParam] | None = None
    top_p: float | None = None
    stream: bool | None = None

    @classmethod
    def from_chat_completion_request(cls, ccc: models.ChatCompletionRequest) -> "ChatCompletionRequest":
        ccc = ccc.model_dump()
        if "seed" in ccc:
            ccc["random_seed"] = ccc["seed"]
            del ccc["seed"]
        if "lm_config" in ccc:
            del ccc["lm_config"]
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
        return models.ChatCompletionResponse.model_validate(self.model_dump(exclude_none=True))
