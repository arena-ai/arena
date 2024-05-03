from typing import Literal, Mapping, Sequence, Any

from pydantic import BaseModel

from arena import models
from arena.models import Function, ChatCompletionToolParam, Message, ResponseFormat, TopLogprob, TokenLogprob, ChoiceLogprobs, Choice
"""
ChatCompletionCreate -> anthropic MessageCreateParams -> anthropic Message -> ChatCompletion
"""

class Metadata(BaseModel):
    user_id: str


class FunctionDefinition(BaseModel):
    name: str
    description: str | None = None
    input_schema: Mapping[str, Any]


class ChatCompletionRequest(BaseModel):
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
    def from_chat_completion_request(cls, ccc: models.ChatCompletionRequest) -> "ChatCompletionRequest":
        messages: Sequence[Message] = [msg.model_dump() for msg in ccc.messages if not msg.role == "system"]
        system: Sequence[str] = [msg.content for msg in ccc.messages if msg.role == "system"]
        ccc = ccc.model_dump()
        if "max_tokens" in ccc:
            ccc["max_tokens"] = ccc["max_tokens"] or 1
        if "user" in ccc and ccc["user"] is not None:
            ccc["metadata"] = {"user_id": ccc["user"]}
            del ccc["user"]
        if "stop" in ccc:   
            ccc["stop_sequences"] = ccc["stop"]
            del ccc["stop"]
        if len(system)==0:
            ccc["system"] = None
        else:
            ccc["system"] = system[0]
        if "lm_config" in ccc:
            del ccc["lm_config"]
        ccc["messages"] = messages
        return ChatCompletionRequest.model_validate(ccc)

    def to_dict(self) -> Mapping[str, Any]:
        return self.model_dump(exclude_none=True)


class TextBlock(BaseModel):
    text: str = ""
    type: Literal["text"] = "text"

class CompletionUsage(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None


class ChatCompletionResponse(BaseModel):
    """
    https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message.py#L14
    """
    id: str
    content: Sequence[TextBlock]
    model: str
    role: Literal["assistant"] = "assistant"
    stop_reason: Literal["end_turn", "max_tokens", "stop_sequence"] | None = None
    stop_sequence: str | None = None
    type: Literal["message"] = "message"
    usage: CompletionUsage | None = None

    @classmethod
    def from_dict(cls, m: Mapping[str, Any]) -> "ChatCompletionResponse":
        return ChatCompletionResponse.model_validate(m)

    def to_chat_completion_response(self) -> models.ChatCompletionResponse:
        finish_reasons = {
            "end_turn": "tool_calls",
            "max_tokens": "length",
            "stop_sequence": "stop"
        }
        return models.ChatCompletionResponse(
            id=self.id,
            choices=[Choice(
                finish_reason=finish_reasons.get(self.stop_reason, None),
                index=i,
                logprobs=None,
                message=Message(role="assistant", content=cb.text)
            ) for i,cb in enumerate(self.content)],
            model=self.model,
            usage=models.CompletionUsage(
                prompt_tokens=self.usage.input_tokens,
                completion_tokens=self.usage.output_tokens,
                total_tokens=self.usage.input_tokens + self.usage.output_tokens,
            ),
        )
