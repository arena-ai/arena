from typing import Literal
from pydantic import BaseModel


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
    response_format: ResponseFormat
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


class Choice(BaseModel):
    finish_reason: Literal["stop", "length", "tool_calls", "content_filter", "function_call"]
    index: int
    logprobs: ChoiceLogprobs | None = None
    message: ChatCompletionMessage


class ChatCompletion(BaseModel):
    id: str
    choices: list[Choice]
    created: int
    model: str
    object: Literal["chat.completion"]
    system_fingerprint: str | None = None
    usage: CompletionUsage | None = None
