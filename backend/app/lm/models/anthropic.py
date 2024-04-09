from typing import Literal, Sequence, Mapping, Any

from app.lm import models

from anthropic.types import MessageCreateParams, MessageParam, Message, ContentBlock, Usage
from anthropic.types.message_create_params import MessageCreateParamsStreaming, MessageCreateParamsNonStreaming, Metadata

"""
ChatCompletionCreate -> anthropic MessageCreateParams -> anthropic Message -> ChatCompletion
"""

def _message_param(message: models.Message) -> MessageParam | str:
    match message.role:
        case "system":
            return message.content
        case "user":
            return MessageParam(role="user", content=message.content)
        case "assistant":
            return MessageParam(role="assistant", content=message.content)
        case _:
            return message.content


def _chat_completion_create(ccc: models.ChatCompletionCreate) -> MessageCreateParams:
    all_messages: Sequence[MessageParam | str] = [_message_param(msg) for msg in ccc.messages]
    messages: Sequence[MessageParam] = [msg for msg in all_messages if not isinstance(msg, str)]
    system: Sequence[str] = [msg for msg in all_messages if isinstance(msg, str)]
    if ccc.stream:
        return MessageCreateParamsStreaming(
            messages=messages,
            model=ccc.model,
            max_tokens=ccc.max_tokens,
            metadata=Metadata(user_id=ccc.user),
            stop_sequences=ccc.stop,
            system=None if len(system)==0 else system[0],
            temperature=ccc.temperature,
            stream=True
            )
    else:
        return MessageCreateParamsNonStreaming(
            messages=messages,
            model=ccc.model,
            max_tokens=ccc.max_tokens,
            metadata=Metadata(user_id=ccc.user),
            stop_sequences=ccc.stop,
            system=None if len(system)==0 else system[0],
            temperature=ccc.temperature,
            stream=False
            )


def chat_completion_create(ccc: models.ChatCompletionCreate) -> Mapping[str, Any]:
    return _chat_completion_create(ccc)


def _completion_usage(u: Usage) -> models.CompletionUsage:
    return models.CompletionUsage(
        completion_tokens=u.output_tokens,
        prompt_tokens=u.input_tokens,
        total_tokens=u.input_tokens+u.output_tokens
    )


def _finish_reason(sr: Literal['end_turn', 'max_tokens', 'stop_sequence'] | None) -> Literal['stop', 'length', 'tool_calls', 'content_filter', 'function_call', 'error'] | None:
    match sr:
        case 'end_turn':
            return 'tool_calls'
        case 'max_tokens':
            return 'length'
        case 'stop_sequence':
            return 'stop'
        case _:
            return None


def chat_completion(m: Message) -> models.ChatCompletion:
    return models.ChatCompletion(
        id=m.id,
        choices=[models.Choice(
            finish_reason=_finish_reason(m.stop_reason),
            index=i,
            logprobs=None,
            message=models.Message(role="assistant", content=cb.text)
        ) for i,cb in enumerate(m.content)],
        model=m.model,
        usage=_completion_usage(m.usage),
    )
