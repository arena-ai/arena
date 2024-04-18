from typing import Literal, Mapping, Sequence, Any

from pydantic import BaseModel

from app.lm import models
from app.lm.models import Function, FunctionDefinition, ChatCompletionToolParam, Message, ResponseFormat, TopLogprob, TokenLogprob, ChoiceLogprobs, Choice, CompletionUsage

"""
models.ChatCompletionCreate -> ChatCompletionCreate -> ChatCompletion -> models.ChatCompletion
"""

class ChatCompletionCreate(BaseModel):
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
    def from_chat_completion_create(cls, ccc: models.ChatCompletionCreate) -> "ChatCompletionCreate":
        ccc = ccc.model_dump()
        if "seed" in ccc:
            ccc["random_seed"] = ccc["seed"]
            del ccc["seed"]
        return ChatCompletionCreate.model_validate(ccc)

    def to_dict(self) -> Mapping[str, Any]:
        return self.model_dump(exclude_unset=True, exclude_none=True)


class ChatCompletion(models.ChatCompletion):
    """
    https://github.com/mistralai/client-python/blob/main/src/mistralai/models/chat_completion.py#L86
    """
    @classmethod
    def from_dict(cls, m: Mapping[str, Any]) -> "ChatCompletion":
        return ChatCompletion.model_validate(m)

    def to_chat_completion(self) -> models.ChatCompletion:
        return models.ChatCompletion.model_validate(self.model_dump(exclude_unset=True, exclude_none=True))
