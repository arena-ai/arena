from functools import cached_property

from app.ops import Op
from app.lm.models import LanguageModelsApiKeys, ChatCompletion, ChatCompletionCreate, Message
from app.services import lm



class Chat(Op[ChatCompletionCreate, ChatCompletion]):
    name: str = "arena"
    api_keys: LanguageModelsApiKeys

    @cached_property
    def service(self) -> lm.LanguageModels:
        return lm.LanguageModels(api_keys=self.api_keys)

    async def call(self, input: ChatCompletionCreate) -> ChatCompletion:
        return await self.service.chat_completion(input)


class Judge(Op[ChatCompletion, str]):
    """Implements a simple LLM-as-a-judge as in https://arxiv.org/pdf/2306.05685.pdf
    """
    name: str = "score"
