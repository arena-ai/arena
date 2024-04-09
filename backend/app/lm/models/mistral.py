from typing import Literal, Mapping, Any

from app.lm import models

from mistralai.models.chat_completion import ChatMessage, ChatCompletionResponse, ChatCompletionResponseChoice, FinishReason, UsageInfo

"""
ChatCompletionCreate -> mistral CompletionCreateParams -> mistral ChatCompletionResponse -> ChatCompletion
"""


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