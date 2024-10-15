from pydantic import BaseModel
from app.lm.models.chat_completion import (
    LMApiKeys,
    Function,
    FunctionDefinition,
    ChatCompletionToolParam,
    Message,
    ResponseFormatBase,
    ResponseFormat,
    ChatCompletionRequest,
    TopLogprob,
    TokenLogprob,
    ChoiceLogprobs,
    Choice,
    CompletionUsage,
    ChatCompletionResponse,
)
from app.lm.models.evaluation import Evaluation, Score
from app.lm.models.settings import LMConfig
import app.lm.models.openai as openai_models
import app.lm.models.mistral as mistral_models
import app.lm.models.anthropic as anthropic_models


class ChatCompletionRequestEventResponse(BaseModel):
    request: (
        ChatCompletionRequest
        | openai_models.ChatCompletionRequest
        | mistral_models.ChatCompletionRequest
        | anthropic_models.ChatCompletionRequest
        | None
    ) = None
    request_event_id: int
    response: (
        ChatCompletionResponse
        | openai_models.ChatCompletionResponse
        | mistral_models.ChatCompletionResponse
        | anthropic_models.ChatCompletionResponse
    )
