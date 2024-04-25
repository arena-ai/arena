import re

from app.ops import Op
from app.lm.models import LanguageModelsApiKeys, ChatCompletionResponse, ChatCompletionRequest, Message, openai, mistral, anthropic
from app.services import lm


class OpenAI(Op[tuple[str, openai.ChatCompletionRequest], openai.ChatCompletionResponse]):
    name: str = "openai"

    async def call(self, api_key: str, input: openai.ChatCompletionRequest) -> openai.ChatCompletionResponse:
        service = lm.OpenAI(api_key=api_key)
        return await service.openai_chat_completion(input)


class Mistral(Op[tuple[str, mistral.ChatCompletionRequest], mistral.ChatCompletionResponse]):
    name: str = "mistral"

    async def call(self, api_key: str, input: mistral.ChatCompletionRequest) -> mistral.ChatCompletionResponse:
        service = lm.Mistral(api_key=api_key)
        return await service.mistral_chat_completion(input)


class Anthropic(Op[tuple[str, anthropic.ChatCompletionRequest], anthropic.ChatCompletionResponse]):
    name: str = "anthropic"

    async def call(self, api_key: str, input: anthropic.ChatCompletionRequest) -> anthropic.ChatCompletionResponse:
        service = lm.Anthropic(api_key=api_key)
        return await service.anthropic_chat_completion(input)


class Chat(Op[tuple[LanguageModelsApiKeys, ChatCompletionRequest], ChatCompletionResponse]):
    name: str = "chat"

    async def call(self, api_keys: LanguageModelsApiKeys, input: ChatCompletionRequest) -> ChatCompletionResponse:
        service = lm.LanguageModels(api_keys=api_keys)
        return await service.chat_completion(input)


class Judge(Op[tuple[LanguageModelsApiKeys, ChatCompletionRequest, ChatCompletionResponse], float]):
    """Implements a simple LLM-as-a-judge as in https://arxiv.org/pdf/2306.05685.pdf
    """
    name: str = "judge"
    reference_model: str = "gpt-4-turbo"
    judge_model: str = "gpt-4-turbo"
    
    @staticmethod
    def find_float(text: str) -> float:
        matches = re.search(r"\d+\.\d+", text)
        if matches:
            return min(1, max(0, float(matches.group())))
        else:
            return 0.0
    
    async def call(self, api_keys: LanguageModelsApiKeys, request: ChatCompletionRequest, response: ChatCompletionResponse) -> float:
        service = lm.LanguageModels(api_keys=api_keys)
        reference_request = request.model_copy()
        reference_request.model = self.reference_model
        reference_response = await service.chat_completion(reference_request)
        judge_request = ChatCompletionRequest(
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
        judge_response = await service.chat_completion(judge_request)
        return self.find_float(judge_response.choices[0].message.content)
