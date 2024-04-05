from typing import Literal, Sequence

from app.lm import models

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
ChatCompletionCreate -> openai CompletionCreateParams -> openai ChatCompletion -> ChatCompletion
"""

def chat_completion_message_param(message: models.Message) -> ChatCompletionMessageParam:
    match message.role:
        case "system":
            return ChatCompletionSystemMessageParam(role="system", content=message.content)
        case "user":
            return ChatCompletionUserMessageParam(role="user", content=message.content)
        case "assistant":
            return ChatCompletionAssistantMessageParam(role="assistant", content=message.content)
        case _:
            return ChatCompletionUserMessageParam(role="user", content=message.content)


def chat_completion_create(ccc: models.ChatCompletionCreate) -> CompletionCreateParams:
    if ccc.stream:
        return CompletionCreateParamsStreaming(
            messages=[chat_completion_message_param(msg) for msg in ccc.messages],
            model=ccc.model,
            frequency_penalty=ccc.frequency_penalty,
            logit_bias=ccc.logit_bias,
            logprobs=ccc.logprobs,
            max_tokens=ccc.max_tokens,
            n=ccc.n,
            presence_penalty=ccc.presence_penalty,
            response_format=ResponseFormat(type=ccc.response_format) if ccc.response_format else None,
            seed=ccc.seed,
            stop=ccc.stop,
            temperature=ccc.temperature,
            tool_choice=ccc.tool_choice,
            tools=ccc.tools,
            top_logprobs=ccc.top_logprobs,
            top_p=ccc.top_p,
            user=ccc.user,
            streaming=True
            )
    else:
        return CompletionCreateParamsNonStreaming(
            messages=[chat_completion_message_param(msg) for msg in ccc.messages],
            model=ccc.model,
            frequency_penalty=ccc.frequency_penalty,
            logit_bias=ccc.logit_bias,
            logprobs=ccc.logprobs,
            max_tokens=ccc.max_tokens,
            n=ccc.n,
            presence_penalty=ccc.presence_penalty,
            response_format=ResponseFormat(type=ccc.response_format) if ccc.response_format else None,
            seed=ccc.seed,
            stop=ccc.stop,
            temperature=ccc.temperature,
            tool_choice=ccc.tool_choice,
            tools=ccc.tools,
            top_logprobs=ccc.top_logprobs,
            top_p=ccc.top_p,
            user=ccc.user,
            streaming=ccc.stream
            )


def message(ccm: ChatCompletionMessage) -> models.Message:
    return models.Message(
        role=ccm.role,
        content=ccm.content
    )


def top_logprob(tl: TopLogprob) -> models.TopLogprob:
    return models.TopLogprob(
        token=tl.token,
        bytes=tl.bytes,
        logprob=tl.logprob
    )


def chat_completion_token_logprob(cctl: ChatCompletionTokenLogprob) -> models.ChatCompletionTokenLogprob:
    return models.ChatCompletionTokenLogprob(
        token=cctl.token,
        logprob=cctl.logprob,
        top_logprobs=[top_logprob(tl) for tl in cctl.top_logprobs]
    )


def choice_logprobs(cl: ChoiceLogprobs) -> models.ChoiceLogprobs:
    return models.ChoiceLogprobs(content=[chat_completion_token_logprob(cctl) for cctl in cl.content] if cl else None)


def choice(c: Choice) -> models.Choice:
    return models.Choice(
        finish_reason=c.finish_reason,
        index=c.index,
        logprobs=choice_logprobs(c.logprobs) if c.logprobs else None,
        message=message(c.message),
    )


def completion_usage(cu: CompletionUsage) -> models.CompletionUsage:
    return models.CompletionUsage(
        completion_tokens=cu.completion_tokens,
        prompt_tokens=cu.prompt_tokens,
        total_tokens=cu.total_tokens
    )


def chat_completion(cc: ChatCompletion) -> models.ChatCompletion:
    return models.ChatCompletion(
        id=cc.id,
        choices=[choice(c) for c in cc.choices],
        created=cc.created,
        model=cc.model,
        object=cc.object,
        system_fingerprint=cc.system_fingerprint,
        usage=completion_usage(cc.usage),
    )