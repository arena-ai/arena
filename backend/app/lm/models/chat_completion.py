from typing import Literal, Mapping, Sequence, Any
from pydantic import BaseModel
from app.models import EventOut
from app.lm.models.settings import LMConfig


"""All LanguageModels"""

class LMApiKeys(BaseModel):
    openai_api_key: str
    mistral_api_key: str
    anthropic_api_key: str

"""ChatCompletionCreate"""

# Inspired by https://github.com/mistralai/client-python/tree/main/src/mistralai/models
# And: https://github.com/anthropics/anthropic-sdk-python/tree/main/src/anthropic/types
# And: https://github.com/openai/openai-python/tree/main/src/openai/types


class Function(BaseModel):
    arguments: str
    name: str


class FunctionDefinition(BaseModel):
    name: str
    description: str | None = None
    parameters: Mapping[str, Any]


class ChatCompletionToolParam(BaseModel):
    id: str | None = None
    function: Function
    type: Literal["function"]


class Message(BaseModel):
    """
    Maps to:
    https://github.com/openai/openai-python/blob/main/src/openai/types/chat/chat_completion_message_param.py#L15
    https://github.com/openai/openai-python/blob/main/src/openai/types/chat/chat_completion_user_message_param.py#L13
    https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message_param.py#L15
    """
    content: str
    role: Literal["system", "user", "assistant", "tools"]
    name: str | None = None
    tool_calls: Sequence[ChatCompletionToolParam] | None = None
    """The tool calls generated by the model, such as function calls."""


class ResponseFormat(BaseModel):
    type: Literal["text", "json_object"] | None = None


class ChatCompletionRequest(BaseModel):
    """
    Maps to:
    https://github.com/openai/openai-python/blob/main/src/openai/types/chat/completion_create_params.py#L24
    https://github.com/mistralai/client-python/blob/main/src/mistralai/client.py#L153
    https://github.com/mistralai/client-python/blob/main/src/mistralai/models/chat_completion.py
    https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message_create_params.py#L13
    """
    messages: Sequence[Message]
    model: str | None
    frequency_penalty: float | None = None
    logit_bias: Mapping[str, int] | None = None
    logprobs: bool | None = None
    max_tokens: int | None = None
    n: int | None = None
    presence_penalty: float | None = None
    response_format: ResponseFormat | None = None
    safe_prompt: bool | None = None
    seed: int | None = None
    stop: str | Sequence[str] | None = None
    temperature: float | None = None
    tool_choice: Literal["none", "auto"] | ChatCompletionToolParam | None = None
    tools: Sequence[ChatCompletionToolParam] | None = None
    top_logprobs: int | None = None
    top_p: float | None = None
    user: str | None = None
    stream: bool | None = None
    lm_config: LMConfig | None = None

    def to_dict(self) -> Mapping[str, Any]:
        return self.model_dump(exclude_none=True)


"""ChatCompletion"""

class TopLogprob(BaseModel):
    token: str
    bytes: Sequence[int] | None = None
    logprob: float


class TokenLogprob(BaseModel):
    token: str
    logprob: float
    top_logprobs: Sequence[TopLogprob]


class ChoiceLogprobs(BaseModel):
    content: Sequence[TokenLogprob] | None = None


class Choice(BaseModel):    
    finish_reason: Literal["stop", "length", "tool_calls", "content_filter", "function_call", "error"] | None = None
    index: int
    logprobs: ChoiceLogprobs | None = None
    message: Message


class CompletionUsage(BaseModel):
    completion_tokens: int | None = None
    prompt_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """
    Maps to:
    https://github.com/openai/openai-python/blob/main/src/openai/types/chat/chat_completion.py#L40
    https://github.com/mistralai/client-python/blob/main/src/mistralai/models/chat_completion.py#L86
    https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message.py#L14
    """
    id: str
    choices: Sequence[Choice]
    created: int | None = None
    model: str
    object: Literal["chat.completion"] | None = None
    system_fingerprint: str | None = None
    usage: CompletionUsage | None = None
    lm_config: LMConfig | None = None

    @classmethod
    def from_dict(cls, m: Mapping[str, Any]) -> "ChatCompletionResponse":
        return ChatCompletionResponse.model_validate(m)


class ChatCompletionRequestEventResponse(BaseModel):
    request: ChatCompletionRequest | None = None
    request_event: EventOut
    response: ChatCompletionResponse
