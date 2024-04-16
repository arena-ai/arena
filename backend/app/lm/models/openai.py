from typing import Mapping, Sequence, Literal, Any
from pydantic import BaseModel
from app.lm import models
from app.lm.models import ChatCompletion

from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_token_logprob import ChatCompletionTokenLogprob, TopLogprob
from openai.types.completion_usage import CompletionUsage
from openai.types.chat.chat_completion import ChatCompletion, Choice, ChoiceLogprobs
"""
models.ChatCompletionCreate -> ChatCompletionCreate -> ChatCompletion -> models.ChatCompletion
Tools such as function calls are not well supported yet
"""

"""ChatCompletionCreate"""

class ChatCompletionCreate(models.ChatCompletionCreate):
    """
    https://github.com/openai/openai-python/blob/main/src/openai/types/chat/completion_create_params.py#L24
    https://platform.openai.com/docs/api-reference/chat
    """
    model: str | Literal["gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-4-vision-preview", "gpt-4", "gpt-4-0314", "gpt-4-0613", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-0613", "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-16k-0613"]

    @classmethod
    def from_chat_completion_create(cls, ccc: models.ChatCompletionCreate) -> "ChatCompletionCreate":
        return ChatCompletionCreate.model_validate(ccc.model_dump())

    def to_dict(self) -> Mapping[str, Any]:
        return self.model_dump(exclude_unset=True, exclude_none=True)


def chat_completion(cc: ChatCompletion) -> models.ChatCompletion:
    return cc
