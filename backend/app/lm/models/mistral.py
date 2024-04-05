from typing import Literal

from app.lm import models

from mistralai.models.chat_completion import ChatMessage, ChatCompletionResponse, ChatCompletionResponseChoice, FinishReason

"""
ChatCompletionCreate -> mistral CompletionCreateParams -> mistral ChatCompletionResponse -> ChatCompletion
"""