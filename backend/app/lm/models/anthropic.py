from typing import Literal

from app.lm import models

from anthropic.types import MessageCreateParams, Message

"""
ChatCompletionCreate -> anthropic MessageCreateParams -> opeanthropicnai Message -> ChatCompletion
"""

class Message(models.Message):
    role: Literal["user", "assistant"]
    content: str