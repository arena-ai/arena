from typing import Literal, Mapping, Any

from app.lm import models

from mistralai.models.chat_completion import ChatMessage, ChatCompletionResponse, ChatCompletionResponseChoice, FinishReason

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


# def message(ccm: ChatCompletionMessage) -> models.Message:
#     return models.Message(
#         role=ccm.role,
#         content=ccm.content
#     )


# def top_logprob(tl: TopLogprob) -> models.TopLogprob:
#     return models.TopLogprob(
#         token=tl.token,
#         bytes=tl.bytes,
#         logprob=tl.logprob
#     )


# def chat_completion_token_logprob(cctl: ChatCompletionTokenLogprob) -> models.ChatCompletionTokenLogprob:
#     return models.ChatCompletionTokenLogprob(
#         token=cctl.token,
#         logprob=cctl.logprob,
#         top_logprobs=[top_logprob(tl) for tl in cctl.top_logprobs]
#     )


# def choice_logprobs(cl: ChoiceLogprobs) -> models.ChoiceLogprobs:
#     return models.ChoiceLogprobs(content=[chat_completion_token_logprob(cctl) for cctl in cl.content] if cl else None)


# def choice(c: Choice) -> models.Choice:
#     return models.Choice(
#         finish_reason=c.finish_reason,
#         index=c.index,
#         logprobs=choice_logprobs(c.logprobs) if c.logprobs else None,
#         message=message(c.message),
#     )


# def completion_usage(cu: CompletionUsage) -> models.CompletionUsage:
#     return models.CompletionUsage(
#         completion_tokens=cu.completion_tokens,
#         prompt_tokens=cu.prompt_tokens,
#         total_tokens=cu.total_tokens
#     )


# def chat_completion(cc: ChatCompletion) -> models.ChatCompletion:
#     return models.ChatCompletion(
#         id=cc.id,
#         choices=[choice(c) for c in cc.choices],
#         created=cc.created,
#         model=cc.model,
#         object=cc.object,
#         system_fingerprint=cc.system_fingerprint,
#         usage=completion_usage(cc.usage),
#     )