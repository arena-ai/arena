from pydantic import BaseModel
from app.lm.models.chat_completion import (
    LMApiKeys,
    Function, FunctionDefinition,
    ChatCompletionToolParam, Message, ResponseFormat, ChatCompletionRequest,
    TopLogprob, TokenLogprob, ChoiceLogprobs, Choice, CompletionUsage, ChatCompletionResponse,
    )
from app.lm.models.evaluation import Evaluation, Score
from app.lm.models.settings import LMConfig
import app.lm.models.openai as oai
import app.lm.models.mistral as mis
import app.lm.models.anthropic as ant


class ChatCompletionRequestEventResponse(BaseModel):
    request: ChatCompletionRequest | oai.ChatCompletionRequest | mis.ChatCompletionRequest | ant.ChatCompletionRequest | None = None
    request_event_id: int
    response: ChatCompletionResponse | oai.ChatCompletionResponse | mis.ChatCompletionResponse | ant.ChatCompletionResponse
