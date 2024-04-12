from functools import cached_property

from app.ops import Op
from app.lm.models import ChatCompletion, ChatCompletionCreate
from app.services import lm


class Arena(Op[ChatCompletionCreate, ChatCompletion]):
    openai_api_key: str
    mistral_api_key: str
    anthropic_api_key: str

    def __init__(self, openai_api_key: str, mistral_api_key: str, anthropic_api_key: str):
        super().__init__(name="lm_arena", openai_api_key=openai_api_key, mistral_api_key=mistral_api_key, anthropic_api_key=anthropic_api_key)
        self.arena = lm.Arena(openai_api_key=openai_api_key, mistral_api_key=mistral_api_key, anthropic_api_key=anthropic_api_key)

    def call(self, input: ChatCompletionCreate) -> ChatCompletion:
        return self.arena.call(input)