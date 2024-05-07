from datetime import datetime
from pydantic import BaseModel
from arena.models.chat_completion import (
    LMApiKeys,
    Function, FunctionDefinition,
    ChatCompletionToolParam, Message, ResponseFormat, ChatCompletionRequest,
    TopLogprob, TokenLogprob, ChoiceLogprobs, Choice, CompletionUsage, ChatCompletionResponse,
    )
from arena.models.evaluation import Evaluation, Score
from arena.models.settings import LMConfig
import arena.models.openai as oai
import arena.models.mistral as mis
import arena.models.anthropic as ant


class EventOut(BaseModel):
    id: int
    timestamp: datetime
    name: str
    content: str
    owner_id: int
    parent_id: int | None = None


class ChatCompletionRequestEventResponse(BaseModel):
    request: ChatCompletionRequest | oai.ChatCompletionRequest | mis.ChatCompletionRequest | ant.ChatCompletionRequest | None = None
    request_event_id: int
    response: ChatCompletionResponse | oai.ChatCompletionResponse | mis.ChatCompletionResponse | ant.ChatCompletionResponse