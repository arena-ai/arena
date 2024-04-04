from enum import Enum
from typing import Literal, Any
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from openai.types.completion import Completion
from openai.types.completion_choice import CompletionChoice

from mistralai.models.chat_completion import ChatCompletionResponse, ChatCompletionResponseChoice, FinishReason

from anthropic.types import Message as AnthropicMessage, ContentBlock
from anthropic import Anthropic

# Inspired by https://github.com/mistralai/client-python/tree/main/src/mistralai/models
# And: https://github.com/anthropics/anthropic-sdk-python/tree/main/src/anthropic/types
# And: https://github.com/openai/openai-python/tree/main/src/openai/types


class MessageBase(BaseModel):
    role: str
    content: str


class MessageOpenAI(MessageBase):
    name: str | None = None


class Message(MessageBase):
    pass


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


class CreateChatCompletionBase(BaseModel):
    messages: list[Message]
    model: str | None
    max_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    stream: bool | None = None


class CreateChatCompletion(CreateChatCompletionBase):
    frequency_penalty: float | None = None
    logit_bias: dict[str, int] | None = None
    logprobs: bool | None = None
    n: int | None = None
    presence_penalty: float | None = None
    response_format: ResponseFormat | None = None
    seed: int | None = None
    stop: str | list[str] | None = None
    tool_choice: Literal["none", "auto"] | ChatCompletionNamedToolChoiceParam | None = None
    tools: list[ChatCompletionToolParam] | None = None
    top_logprobs: int | None = None
    user: str | None = None
    safe_prompt: bool | None = None


class CreateChatCompletionOpenAI(CreateChatCompletion):
    messages: list[MessageOpenAI]


class ChatCompletionMessage(BaseModel):
    content: str | None = None
    role: Literal["assistant"] = "assistant"
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


class Choice(BaseModel):    
    finish_reason: Literal["stop", "length", "tool_calls", "content_filter", "function_call", "error"] | None = None
    index: int
    logprobs: ChoiceLogprobs | None = None
    message: ChatCompletionMessage

    @field_validator('finish_reason', mode='before')
    @classmethod
    def convert_finish_reason(cls, v) -> str:
        if isinstance(v, FinishReason):
            return v.value
        return v

    @classmethod
    def from_openai(cls, v: CompletionChoice) -> "Choice":
        return Choice.model_validate(v, strict=False, from_attributes=True)

    @classmethod
    def from_mistral(cls, v: ChatCompletionResponseChoice) -> "Choice":
        return Choice.model_validate(v, strict=False, from_attributes=True)
        # return Choice(finish_reason=v.finish_reason, index=v.index, message=v.message)

    @classmethod
    def from_anthropic(cls, v: CompletionChoice) -> "Choice":
        return Choice(index=0, message=ChatCompletionMessage())

    


class CompletionUsage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


class ChatCompletion(BaseModel):
    id: str
    choices: list[Choice]
    created: int | None = None
    model: str
    object: Literal["chat.completion"] | None = None
    system_fingerprint: str | None = None
    usage: CompletionUsage | None = None

    @classmethod
    def from_openai(cls, chat_completion: Completion) -> "ChatCompletion":
        return ChatCompletion.model_validate(chat_completion, strict=False, from_attributes=True)

    @classmethod
    def from_mistral(cls, chat_completion: ChatCompletionResponse) -> "ChatCompletion":
        return ChatCompletion(
            id=chat_completion.id,
            choices=[Choice.from_mistral(choice) for choice in chat_completion.choices],
            model=chat_completion.model,
        )
    
    @classmethod
    def from_anthropic(cls, message: AnthropicMessage) -> "ChatCompletion":
        return ChatCompletion(
            id=message.id,
            choices=[Choice.from_anthropic(choice) for choice in message.content],
            model=message.model,
        )
