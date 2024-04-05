from typing import Literal, Sequence

from app.lm import models

from openai.types.chat.completion_create_params import CompletionCreateParams
from openai.types.chat.chat_completion import ChatCompletion, Choice

"""
ChatCompletionCreate -> openai CompletionCreateParams -> openai ChatCompletion -> ChatCompletion
"""
