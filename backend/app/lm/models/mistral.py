from typing import Literal, Mapping, Any

from app.lm import models

from mistralai.models.chat_completion import ChatMessage, ChatCompletionResponse, ChatCompletionResponseChoice, FinishReason, UsageInfo

"""
ChatCompletionCreate -> mistral CompletionCreateParams -> mistral ChatCompletionResponse -> ChatCompletion
"""


def chat_completion_create(ccc: models.ChatCompletionCreate) -> Mapping[str, Any]:
    return {
        "messages": ccc.messages,
        "model": ccc.model,
        "tools": ccc.tools if ccc.tools else None,
        "temperature": ccc.temperature,
        "max_tokens": ccc.max_tokens,
        "top_p": ccc.top_p,
        "random_seed": ccc.seed,
        "safe_prompt": ccc.safe_prompt,
        "tool_choice": ccc.tool_choice,
        "response_format": ccc.response_format
    }


def message(cm: ChatMessage) -> models.Message:
    return models.Message(
        role=cm.role,
        content=cm.content
    )


def finish_reason(fr: FinishReason) -> Literal['stop', 'length', 'tool_calls', 'content_filter', 'function_call', 'error']:
    return fr.value


def choice(ccrc: ChatCompletionResponseChoice) -> models.Choice:
    return models.Choice(
        finish_reason=finish_reason(ccrc.finish_reason) if ccrc.finish_reason else None,
        index=ccrc.index,
        message=message(ccrc.message),
    )


def completion_usage(ui: UsageInfo) -> models.CompletionUsage:
    return models.CompletionUsage(
        completion_tokens=ui.completion_tokens,
        prompt_tokens=ui.prompt_tokens,
        total_tokens=ui.total_tokens
    )


def chat_completion(ccr: ChatCompletionResponse) -> models.ChatCompletion:
    return models.ChatCompletion(
        id=ccr.id,
        choices=[choice(c) for c in ccr.choices],
        created=ccr.created,
        model=ccr.model,
        object=ccr.object,
        usage=completion_usage(ccr.usage),
    )