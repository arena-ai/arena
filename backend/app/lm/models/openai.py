from typing import Literal, Sequence

from app.lm import models

from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_system_message_param import ChatCompletionSystemMessageParam
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam
from openai.types.chat.chat_completion_assistant_message_param import ChatCompletionAssistantMessageParam
from openai.types.chat.completion_create_params import CompletionCreateParams, CompletionCreateParamsStreaming, CompletionCreateParamsNonStreaming, ResponseFormat
from openai.types.chat.chat_completion import ChatCompletion, Choice

"""
ChatCompletionCreate -> openai CompletionCreateParams -> openai ChatCompletion -> ChatCompletion
"""

def message(message: models.Message) -> ChatCompletionMessageParam:
    match message.role:
        case "system":
            return ChatCompletionSystemMessageParam(role="system", content=message.content)
        case "user":
            return ChatCompletionUserMessageParam(role="user", content=message.content)
        case "assistant":
            return ChatCompletionAssistantMessageParam(role="assistant", content=message.content)
        case _:
            return ChatCompletionUserMessageParam(role="user", content=message.content)


def chat_completion_create(chat_completion_create: models.ChatCompletionCreate) -> CompletionCreateParams:
    if chat_completion_create.stream:
        return CompletionCreateParamsStreaming(
            messages=[message(msg) for msg in chat_completion_create.messages],
            model=chat_completion_create.model,
            frequency_penalty=chat_completion_create.frequency_penalty,
            logit_bias=chat_completion_create.logit_bias,
            logprobs=chat_completion_create.logprobs,
            max_tokens=chat_completion_create.max_tokens,
            n=chat_completion_create.n,
            presence_penalty=chat_completion_create.presence_penalty,
            response_format=ResponseFormat(type=chat_completion_create.response_format) if chat_completion_create.response_format else None,
            seed=chat_completion_create.seed,
            stop=chat_completion_create.stop,
            temperature=chat_completion_create.temperature,
            tool_choice=chat_completion_create.tool_choice,
            tools=chat_completion_create.tools,
            top_logprobs=chat_completion_create.top_logprobs,
            top_p=chat_completion_create.top_p,
            user=chat_completion_create.user,
            streaming=True
            )
    else:
        return CompletionCreateParamsNonStreaming(
            messages=[message(msg) for msg in chat_completion_create.messages],
            model=chat_completion_create.model,
            frequency_penalty=chat_completion_create.frequency_penalty,
            logit_bias=chat_completion_create.logit_bias,
            logprobs=chat_completion_create.logprobs,
            max_tokens=chat_completion_create.max_tokens,
            n=chat_completion_create.n,
            presence_penalty=chat_completion_create.presence_penalty,
            response_format=ResponseFormat(type=chat_completion_create.response_format) if chat_completion_create.response_format else None,
            seed=chat_completion_create.seed,
            stop=chat_completion_create.stop,
            temperature=chat_completion_create.temperature,
            tool_choice=chat_completion_create.tool_choice,
            tools=chat_completion_create.tools,
            top_logprobs=chat_completion_create.top_logprobs,
            top_p=chat_completion_create.top_p,
            user=chat_completion_create.user,
            streaming=chat_completion_create.stream
            )