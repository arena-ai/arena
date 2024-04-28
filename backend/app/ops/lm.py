import re

from app.lm.models import LanguageModelsApiKeys, ChatCompletionResponse, ChatCompletionRequest, Message, openai, mistral, anthropic
from app.services import lm, Request, Response
from app.ops import Op
from app.ops.events import LogRequest, LogResponse

class OpenAI(Op[tuple[str, openai.ChatCompletionRequest], Response[openai.ChatCompletionResponse]]):
    async def call(self, api_key: str, input: openai.ChatCompletionRequest) -> Response[openai.ChatCompletionResponse]:
        return await lm.OpenAI(api_key=api_key).openai_chat_completion(input)

class OpenAIRequest(Op[openai.ChatCompletionRequest, Request[openai.ChatCompletionRequest]]):
    async def call(self, input: openai.ChatCompletionRequest) -> Request[openai.ChatCompletionRequest]:
        return lm.OpenAI().request(input)


class Mistral(Op[tuple[str, mistral.ChatCompletionRequest], Response[mistral.ChatCompletionResponse]]):
    async def call(self, api_key: str, input: mistral.ChatCompletionRequest) -> Response[mistral.ChatCompletionResponse]:
        return await lm.Mistral(api_key=api_key).mistral_chat_completion(input)

class MistralRequest(Op[mistral.ChatCompletionRequest, Request[mistral.ChatCompletionRequest]]):
    async def call(self, input: mistral.ChatCompletionRequest) -> Request[mistral.ChatCompletionRequest]:
        return lm.Mistral().request(input)

class Anthropic(Op[tuple[str, anthropic.ChatCompletionRequest], Response[anthropic.ChatCompletionResponse]]):
    async def call(self, api_key: str, input: anthropic.ChatCompletionRequest) -> Response[anthropic.ChatCompletionResponse]:
        return await lm.Anthropic(api_key=api_key).anthropic_chat_completion(input)

class AnthropicRequest(Op[anthropic.ChatCompletionRequest, Request[anthropic.ChatCompletionRequest]]):
    async def call(self, input: anthropic.ChatCompletionRequest) -> Request[anthropic.ChatCompletionRequest]:
        return lm.Anthropic().request(input)


class Chat(Op[tuple[LanguageModelsApiKeys, ChatCompletionRequest], Response[ChatCompletionResponse]]):
    async def call(self, api_keys: LanguageModelsApiKeys, input: ChatCompletionRequest) -> Response[ChatCompletionResponse]:
        return await lm.LanguageModels(api_keys=api_keys).chat_completion(input)

class ChatRequest(Op[ChatCompletionRequest, Request[ChatCompletionRequest]]):
    async def call(self, input: ChatCompletionRequest) -> Request[ChatCompletionRequest]:
        return lm.LanguageModels(api_keys=LanguageModelsApiKeys(openai_api_key="", mistral_api_key="", anthropic_api_key="")).request(input)


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
{reference_response.content.choices[0].message.content}"""),
                Message(role="assistant", content="0.7989"),
                Message(role="user", content=f"""[User request]
{next((msg.content for msg in request.messages if msg.role=="user"), "What?")}

[Assistant response]
{response.choices[0].message.content}"""),
            ]
        )
        judge_response = await service.chat_completion(judge_request)
        return self.find_float(judge_response.content.choices[0].message.content)
