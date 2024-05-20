from typing import Mapping, Sequence, Literal, Any

from pydantic import BaseModel

from arena import models
from arena.models import Function, FunctionDefinition, ChatCompletionToolParam, Message, ResponseFormat, TopLogprob, TokenLogprob, ChoiceLogprobs, Choice, CompletionUsage

MODELS = ("gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k")

class ChatCompletionRequest(models.ChatCompletionRequest):
    """
    https://github.com/openai/openai-python/blob/main/src/openai/types/chat/completion_create_params.py#L24
    https://platform.openai.com/docs/api-reference/chat
    """
    model: str | Literal[*MODELS]

    @classmethod
    def from_chat_completion_request(cls, ccc: models.ChatCompletionRequest) -> "ChatCompletionRequest":
        return ChatCompletionRequest.model_validate(ccc.model_dump(exclude=["lm_config"]))

    def to_dict(self) -> Mapping[str, Any]:
        return self.model_dump(exclude_none=True)

class ChatCompletionResponse(models.ChatCompletionResponse):
    """
    https://github.com/openai/openai-python/blob/main/src/openai/types/chat/chat_completion.py#L40
    """
    @classmethod
    def from_dict(cls, m: Mapping[str, Any]) -> "ChatCompletionResponse":
        return ChatCompletionResponse.model_validate(m)

    def to_chat_completion_response(self) -> models.ChatCompletionResponse:
        return models.ChatCompletionResponse.model_validate(self.model_dump(exclude_none=True))

