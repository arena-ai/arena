from typing import Mapping, Sequence, Literal, Any
from pydantic import BaseModel
from app.lm import models
from app.lm.models import Function, FunctionDefinition, ChatCompletionToolParam, Message, ResponseFormat

from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_system_message_param import ChatCompletionSystemMessageParam
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam
from openai.types.chat.chat_completion_assistant_message_param import ChatCompletionAssistantMessageParam
from openai.types.chat.chat_completion_token_logprob import ChatCompletionTokenLogprob, TopLogprob
from openai.types.completion_usage import CompletionUsage
from openai.types.chat.chat_completion import ChatCompletion, Choice, ChoiceLogprobs
from openai.types.chat.completion_create_params import CompletionCreateParams, CompletionCreateParamsStreaming, CompletionCreateParamsNonStreaming, ResponseFormat

"""
models.ChatCompletionCreate -> ChatCompletionCreate -> ChatCompletion -> models.ChatCompletion
Tools such as function calls are well supported yet
"""

"""ChatCompletionCreate"""

class ChatCompletionCreate(models.ChatCompletionCreate):
    model: str | Literal[
        "gpt-4-0125-preview",
        "gpt-4-turbo-preview",
        "gpt-4-1106-preview",
        "gpt-4-vision-preview",
        "gpt-4",
        "gpt-4-0314",
        "gpt-4-0613",
        "gpt-4-32k",
        "gpt-4-32k-0314",
        "gpt-4-32k-0613",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-16k-0613",
    ]


def _chat_completion_create(ccc: models.ChatCompletionCreate) -> ChatCompletionCreate:
    return ChatCompletionCreate(ccc)


def chat_completion_create(ccc: models.ChatCompletionCreate) -> Mapping[str, Any]:
    return _chat_completion_create(ccc)


def _message(ccm: ChatCompletionMessage) -> models.Message:
    return models.Message(
        role=ccm.role,
        content=ccm.content
    )


def _top_logprob(tl: TopLogprob) -> models.TopLogprob:
    return models.TopLogprob(
        token=tl.token,
        bytes=tl.bytes,
        logprob=tl.logprob
    )


def _chat_completion_token_logprob(cctl: ChatCompletionTokenLogprob) -> models.ChatCompletionTokenLogprob:
    return models.ChatCompletionTokenLogprob(
        token=cctl.token,
        logprob=cctl.logprob,
        top_logprobs=[_top_logprob(tl) for tl in cctl.top_logprobs]
    )


def _choice_logprobs(cl: ChoiceLogprobs) -> models.ChoiceLogprobs:
    return models.ChoiceLogprobs(content=[_chat_completion_token_logprob(cctl) for cctl in cl.content] if cl else None)


def _choice(c: Choice) -> models.Choice:
    return models.Choice(
        finish_reason=c.finish_reason,
        index=c.index,
        logprobs=_choice_logprobs(c.logprobs) if c.logprobs else None,
        message=_message(c.message),
    )


def _completion_usage(cu: CompletionUsage) -> models.CompletionUsage:
    return models.CompletionUsage(
        completion_tokens=cu.completion_tokens,
        prompt_tokens=cu.prompt_tokens,
        total_tokens=cu.total_tokens
    )


def chat_completion(cc: ChatCompletion) -> models.ChatCompletion:
    return models.ChatCompletion(
        id=cc.id,
        choices=[_choice(c) for c in cc.choices],
        created=cc.created,
        model=cc.model,
        object=cc.object,
        system_fingerprint=cc.system_fingerprint,
        usage=_completion_usage(cc.usage),
    )