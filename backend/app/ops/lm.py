import re

from app.lm.models import LMApiKeys, ChatCompletionResponse, ChatCompletionRequest, Message, Score
import app.lm.models.openai as openai_models
import app.lm.models.mistral as mistral_models
import app.lm.models.anthropic as anthropic_models
from app.services import Request, Response
import app.services.lm as slm
from app.ops import Op


class OpenAI(Op[tuple[str, openai_models.ChatCompletionRequest], Response[openai_models.ChatCompletionResponse]]):
    async def call(self, api_key: str, input: openai_models.ChatCompletionRequest) -> Response[openai_models.ChatCompletionResponse]:
        return await slm.OpenAI(api_key=api_key).openai_chat_completion(input)

class OpenAIRequest(Op[openai_models.ChatCompletionRequest, Request[openai_models.ChatCompletionRequest]]):
    async def call(self, input: openai_models.ChatCompletionRequest) -> Request[openai_models.ChatCompletionRequest]:
        return slm.OpenAI().request(input)

# instances
openai = OpenAI()
openai_request = OpenAIRequest()

class Mistral(Op[tuple[str, mistral_models.ChatCompletionRequest], Response[mistral_models.ChatCompletionResponse]]):
    async def call(self, api_key: str, input: mistral_models.ChatCompletionRequest) -> Response[mistral_models.ChatCompletionResponse]:
        return await slm.Mistral(api_key=api_key).mistral_chat_completion(input)

class MistralRequest(Op[mistral_models.ChatCompletionRequest, Request[mistral_models.ChatCompletionRequest]]):
    async def call(self, input: mistral_models.ChatCompletionRequest) -> Request[mistral_models.ChatCompletionRequest]:
        return slm.Mistral().request(input)

# instances
mistral = Mistral()
mistral_request = MistralRequest()

class Anthropic(Op[tuple[str, anthropic_models.ChatCompletionRequest], Response[anthropic_models.ChatCompletionResponse]]):
    async def call(self, api_key: str, input: anthropic_models.ChatCompletionRequest) -> Response[anthropic_models.ChatCompletionResponse]:
        return await slm.Anthropic(api_key=api_key).anthropic_chat_completion(input)

class AnthropicRequest(Op[anthropic_models.ChatCompletionRequest, Request[anthropic_models.ChatCompletionRequest]]):
    async def call(self, input: anthropic_models.ChatCompletionRequest) -> Request[anthropic_models.ChatCompletionRequest]:
        return slm.Anthropic().request(input)

# instances
anthropic = Anthropic()
anthropic_request = AnthropicRequest()

class Chat(Op[tuple[LMApiKeys, ChatCompletionRequest], Response[ChatCompletionResponse]]):
    async def call(self, api_keys: LMApiKeys, input: ChatCompletionRequest) -> Response[ChatCompletionResponse]:
        return await slm.LanguageModels(api_keys=api_keys).chat_completion(input)

class ChatRequest(Op[ChatCompletionRequest, Request[ChatCompletionRequest]]):
    async def call(self, input: ChatCompletionRequest) -> Request[ChatCompletionRequest]:
        return slm.LanguageModels(api_keys=LMApiKeys(openai_api_key="", mistral_api_key="", anthropic_api_key="")).request(input)

# instances
chat = Chat()
chat_request = ChatRequest()

class Judge(Op[tuple[LMApiKeys, ChatCompletionRequest, ChatCompletionResponse], Score]):
    """Implements a simple LLM-as-a-judge as in https://arxiv.org/pdf/2306.05685.pdf
    """
    name: str = "judge"
    reference_model: str = "gpt-4o"
    judge_model: str = "gpt-4o"
    
    @staticmethod
    def find_float(text: str) -> float:
        matches = re.search(r"\d+\.\d+", text)
        if matches:
            return min(1, max(0, float(matches.group())))
        else:
            return 0.0
    
    async def call(self, api_keys: LMApiKeys, request: ChatCompletionRequest, response: ChatCompletionResponse) -> Score:
        service = slm.LanguageModels(api_keys=api_keys)
        reference_request = request.model_copy()
        reference_request.model = self.reference_model
        reference_request.temperature = 0
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
        return Score(value=self.find_float(judge_response.content.choices[0].message.content))

judge = Judge()
