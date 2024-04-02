from enum import Enum
from typing import Literal, Any
from pydantic import BaseModel

# Inspired by https://github.com/mistralai/client-python/tree/main/src/mistralai/models
# And: https://github.com/anthropics/anthropic-sdk-python/tree/main/src/anthropic/types
# And: https://github.com/openai/openai-python/tree/main/src/openai/types

class Message(BaseModel):
    role: str
    content: str
    name: str | None = None


class ResponseFormat(BaseModel):
    type: str | Literal["text", "json_object"]


class Function(BaseModel):
    name: str


class ChatCompletionNamedToolChoiceParam(BaseModel):
    function: Function
    type: Literal["function"]


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: dict[str, object]


class ChatCompletionToolParam(BaseModel):
    function: FunctionDefinition
    type: Literal["function"]


class CreateChatCompletion(BaseModel):
    messages: list[Message]
    model: str | None
    frequency_penalty: float | None = None
    logit_bias: dict[str, int] | None = None
    logprobs: bool | None = None
    max_tokens: int | None = None
    n: int | None = None
    presence_penalty: float | None = None
    response_format: ResponseFormat | None = None
    seed: int | None = None
    stop: str | list[str] | None = None
    tool_choice: Literal["none", "auto"] | ChatCompletionNamedToolChoiceParam | None = None
    tools: list[ChatCompletionToolParam] | None = None
    temperature: float | None = None
    top_logprobs: int | None = None
    top_p: float | None = None
    user: str | None = None
    stream: bool | None = None
    safe_prompt: bool | None = None


class ChatCompletionMessage(BaseModel):
    content: str | None = None
    role: Literal["assistant"]
    function_call: Any | None = None
    tool_calls: Any | None = None


class TopLogprob(BaseModel):
    token: str
    bytes: list[int] | None = None
    logprob: float


class ChatCompletionTokenLogprob(BaseModel):
    token: str
    logprob: float
    top_logprobs: list[TopLogprob]


class ChoiceLogprobs(BaseModel):
    content: list[ChatCompletionTokenLogprob] | None = None


class FinishReason(str, Enum):
    stop = "stop"
    length = "length"
    error = "error"
    tool_calls = "tool_calls"


class Choice(BaseModel):
    finish_reason: Literal["stop", "length", "tool_calls", "content_filter", "function_call"] | FinishReason | None = None
    index: int
    logprobs: ChoiceLogprobs | None = None
    message: ChatCompletionMessage


class CompletionUsage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


class ChatCompletion(BaseModel):
    id: str
    choices: list[Choice]
    created: int
    model: str
    object: Literal["chat.completion"]
    system_fingerprint: str | None = None
    usage: CompletionUsage | None = None
