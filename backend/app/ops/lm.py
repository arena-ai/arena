from functools import cached_property

from app.ops import Op
from app.lm.models import ChatCompletion, ChatCompletionCreate
from app.services import lm


class Arena(Op[ChatCompletionCreate, ChatCompletion]):
    name: str = "arena"
    openai_api_key: str
    mistral_api_key: str
    anthropic_api_key: str

    @cached_property
    def service(self) -> lm.Arena:
        return lm.Arena(
            openai_api_key=self.openai_api_key,
            mistral_api_key=self.mistral_api_key,
            anthropic_api_key=self.anthropic_api_key,
        )

    async def call(self, input: ChatCompletionCreate) -> ChatCompletion:
        return await self.service.chat_completion(input)
