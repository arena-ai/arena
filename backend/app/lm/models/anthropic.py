from typing import Literal, Mapping, Sequence, Any

from pydantic import BaseModel

from app.lm import models
from app.lm.models import Function, ChatCompletionToolParam, Message, ResponseFormat, TopLogprob, TokenLogprob, ChoiceLogprobs, Choice, CompletionUsage
"""
ChatCompletionCreate -> anthropic MessageCreateParams -> anthropic Message -> ChatCompletion
"""

class Metadata(BaseModel):
    user_id: str | None


class FunctionDefinition(BaseModel):
    name: str
    description: str | None = None
    input_schema: Mapping[str, Any]


class ChatCompletionCreate(BaseModel):
    """
    Maps to:
    https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message_create_params.py#L13
    https://docs.anthropic.com/claude/reference/messages_post
    """
    max_tokens: int = 1
    messages: Sequence[Message]
    model: str | Literal["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-2.1", "claude-2.0", "claude-instant-1.2"]
    metadata: Metadata | None = None
    stop_sequences: Sequence[str] | None = None
    system: str | None = None
    temperature: float | None = None
    tools: Sequence[FunctionDefinition] | None = None
    top_p: float | None = None
    top_k: int | None = None
    stream: bool | None = None

    @classmethod
    def from_chat_completion_create(cls, ccc: models.ChatCompletionCreate) -> "ChatCompletionCreate":
        messages: Sequence[MessageParam] = [msg.model_dump() for msg in ccc.messages if not isinstance(msg, str)]
        system: Sequence[str] = [msg for msg in ccc.messages if isinstance(msg, str)]
        ccc = ccc.model_dump()
        ccc["max_tokens"] = ccc["max_tokens"] or 1
        ccc["metadata"] = {"user_id": ccc["user"]}
        ccc["stop_sequences"] = ccc["stop"]
        del ccc["stop"]
        ccc["system"] = None if len(system)==0 else system[0]
        return ChatCompletionCreate.model_validate(ccc)

    def to_dict(self) -> Mapping[str, Any]:
        return self.model_dump(exclude_unset=True, exclude_none=True)


class TextBlock(BaseModel):
    text: str = ""
    type: Literal["text"] = "text"

class ChatCompletion(BaseModel):
    """
    https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message.py#L14
    """
    id: str
    content: Sequence[TextBlock]
    model: str
    role: Literal["assistant"] = "assistant"
    stop_reason: Literal["end_turn", "max_tokens", "stop_sequence"] | None = None
    stop_sequence: str = None
    type: Literal["message"] = "message"
    usage: CompletionUsage | None = None

    @classmethod
    def from_dict(cls, m: Mapping[str, Any]) -> "ChatCompletion":
        return ChatCompletion.model_validate(m)

    def to_chat_completion(self) -> models.ChatCompletion:
        return models.ChatCompletion(
            id=self.id,
            choices=[models.Choice(
                finish_reason=self.stop_reason,
                index=i,
                logprobs=None,
                message=models.Message(role="assistant", content=cb.text)
            ) for i,cb in enumerate(self.content)],
            model=self.model,
            usage=(self.usage),
        )
