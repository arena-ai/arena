from typing import Literal, Mapping, Sequence, Any

from pydantic import BaseModel

from app.lm import models

from mistralai.models.chat_completion import ChatMessage, ChatCompletionResponse, ChatCompletionResponseChoice, FinishReason, UsageInfo

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
    messages: Sequence[models.Message]
    model: str | Literal["mistral-embed", "mistral-large-2402", "mistral-large-latest", "mistral-medium", "mistral-medium-2312", "mistral-medium-latest", "mistral-small", "mistral-small-2312", "mistral-small-2402", "mistral-small-latest", "mistral-tiny", "mistral-tiny-2312", "open-mistral-7b", "open-mixtral-8x7b"]
    max_tokens: int | None = None
    response_format: models.ResponseFormat | None = None
    safe_prompt: bool | None = None
    random_seed: int | None = None
    stream: bool | None = None
    temperature: float | None = None
    tool_choice: Literal["none", "auto", "any"] | None = None
    tools: Sequence[models.ChatCompletionToolParam] | None = None
    top_p: float | None = None
    stream: bool | None = None


def chat_completion_create(ccc: models.ChatCompletionCreate) -> Mapping[str, Any]:
    ccc = ccc.model_dump(mode="json", exclude_none=True)
    if "seed" in ccc:
        ccc["random_seed"] = ccc["seed"]
        del ccc["seed"]
    return ccc


def _message(cm: ChatMessage) -> models.Message:
    return models.Message(
        role=cm.role,
        content=cm.content
    )


def _finish_reason(fr: FinishReason) -> Literal['stop', 'length', 'tool_calls', 'content_filter', 'function_call', 'error']:
    return fr.value


def _choice(ccrc: ChatCompletionResponseChoice) -> models.Choice:
    return models.Choice(
        finish_reason=_finish_reason(ccrc.finish_reason) if ccrc.finish_reason else None,
        index=ccrc.index,
        message=_message(ccrc.message),
    )


def _completion_usage(ui: UsageInfo) -> models.CompletionUsage:
    return models.CompletionUsage(
        completion_tokens=ui.completion_tokens,
        prompt_tokens=ui.prompt_tokens,
        total_tokens=ui.total_tokens
    )


def chat_completion(ccr: ChatCompletionResponse) -> models.ChatCompletion:
    return models.ChatCompletion(
        id=ccr.id,
        choices=[_choice(c) for c in ccr.choices],
        created=ccr.created,
        model=ccr.model,
        object=ccr.object,
        usage=_completion_usage(ccr.usage),
    )