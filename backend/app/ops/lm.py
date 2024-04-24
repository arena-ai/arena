from functools import cached_property
import re

from app.ops import Op
from app.lm.models import LanguageModelsApiKeys, ChatCompletion, ChatCompletionCreate, Message
from app.services import lm


class Chat(Op[ChatCompletionCreate, ChatCompletion]):
    name: str = "chat"
    api_keys: LanguageModelsApiKeys

    @cached_property
    def service(self) -> lm.LanguageModels:
        return lm.LanguageModels(api_keys=self.api_keys)

    async def call(self, input: ChatCompletionCreate) -> ChatCompletion:
        return await self.service.chat_completion(input)


class Judge(Op[tuple[ChatCompletionCreate, ChatCompletion], float]):
    """Implements a simple LLM-as-a-judge as in https://arxiv.org/pdf/2306.05685.pdf
    """
    name: str = "judge"
    api_keys: LanguageModelsApiKeys
    reference_model: str = "gpt-4-turbo"
    judge_model: str = "gpt-4-turbo"

    @cached_property
    def service(self) -> lm.LanguageModels:
        return lm.LanguageModels(api_keys=self.api_keys)
    
    @staticmethod
    def find_float(text: str) -> float:
        matches = re.search(r"\d+\.\d+", text)
        if matches:
            return min(1, max(0, float(matches.group())))
        else:
            return 0.0
    
    async def call(self, request: ChatCompletionCreate, response: ChatCompletion) -> float:
        reference_request = request.model_copy()
        reference_request.model = self.reference_model
        reference_response = await self.service.chat_completion(reference_request)
        judge_request = ChatCompletionCreate(
            model=self.judge_model,
            messages=[
                Message(role="system", content=f"""You will be given [User request] [Assistant response] pairs.
Please act as an impartial judge and evaluate the quality of the responses provided by
assistants by returning a score between 0.00 and 1.00 (with many decimals to avoid ties).
Your evaluation should consider factors such as the helpfulness, relevance, accuracy, depth, creativity,
and level of detail of their responses."""),
                Message(role="user", content=f"""[User request]
{next((msg.content for msg in reference_request.messages if msg.role=="user"), "What?")}

[Assistant response]
{reference_response.choices[0].message.content}"""),
                Message(role="assistant", content="0.7989"),
                Message(role="user", content=f"""[User request]
{next((msg.content for msg in request.messages if msg.role=="user"), "What?")}

[Assistant response]
{response.choices[0].message.content}"""),
            ]
        )
        judge_response = await self.service.chat_completion(judge_request)
        return self.find_float(judge_response.choices[0].message.content)
