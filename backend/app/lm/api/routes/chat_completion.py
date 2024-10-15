from typing import Mapping

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.models import EventOut
from app.lm.models import (
    ChatCompletionResponse,
    ChatCompletionRequest,
    ChatCompletionRequestEventResponse,
)
import app.lm.models.openai as openai_models
import app.lm.models.mistral as mistral_models
import app.lm.models.anthropic as anthropic_models
from app.services import Response
from app.lm.handlers import (
    OpenAIHandler,
    MistralHandler,
    AnthropicHandler,
    ArenaHandler,
)
from app.ops import tup
from app.ops.settings import language_models_api_keys, lm_config
from app.ops.events import (
    log_request,
    log_response,
    create_event_identifier,
    log_lm_judge_evaluation,
    log_lm_config,
)
from app.ops.lm import chat_request, judge
from app.ops.session import session, user, event
from app.worker import evaluate


router = APIRouter()


@router.post(
    "/openai/chat/completions",
    response_model=openai_models.ChatCompletionResponse,
)
async def openai_chat_completion(
    session_dep: SessionDep,
    current_user: CurrentUser,
    chat_completion_request: Mapping,
) -> openai_models.ChatCompletionResponse:
    """
    OpenAI integration
    """
    return await OpenAIHandler(
        session_dep, current_user, chat_completion_request
    ).process_request()


@router.post(
    "/mistral/v1/chat/completions",
    response_model=mistral_models.ChatCompletionResponse,
)
async def mistral_chat_completion(
    session_dep: SessionDep,
    current_user: CurrentUser,
    chat_completion_request: Mapping,
) -> mistral_models.ChatCompletionResponse:
    """
    Mistral integration
    """
    return await MistralHandler(
        session_dep, current_user, chat_completion_request
    ).process_request()


@router.post(
    "/anthropic/v1/messages",
    response_model=anthropic_models.ChatCompletionResponse,
)
async def anthropic_chat_completion(
    session_dep: SessionDep,
    current_user: CurrentUser,
    chat_completion_request: Mapping,
) -> anthropic_models.ChatCompletionResponse:
    """
    Anthropic integration
    """
    return await AnthropicHandler(
        session_dep, current_user, chat_completion_request
    ).process_request()


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(
    session_dep: SessionDep,
    current_user: CurrentUser,
    chat_completion_request: Mapping,
) -> ChatCompletionResponse:
    """
    Abstract version
    """
    return await ArenaHandler(
        session_dep, current_user, chat_completion_request
    ).process_request()


@router.post("/chat/completions/request", response_model=EventOut)
async def chat_completion_request(
    session_dep: SessionDep,
    current_user: CurrentUser,
    chat_completion_request: Mapping,
) -> EventOut:
    ses = session()
    usr = user(ses, current_user.id)
    chat_completion_request = ChatCompletionRequest.model_validate(
        chat_completion_request
    )
    lm_request = chat_request(chat_completion_request)
    lm_request_event = log_request(ses, usr, None, lm_request)
    return await lm_request_event.evaluate(session=session_dep)


@router.post("/chat/completions/response", response_model=EventOut)
async def chat_completion_response(
    session_dep: SessionDep,
    current_user: CurrentUser,
    chat_completion_request_event_response: ChatCompletionRequestEventResponse,
) -> EventOut:
    ses = session()
    usr = user(ses, current_user.id)
    request_event = event(
        ses, chat_completion_request_event_response.request_event_id
    )
    config = await lm_config(ses, usr).evaluate(session=session_dep)
    config_event = log_lm_config(ses, usr, request_event, config)
    lm_response = Response(
        status_code=200,
        headers={},
        content=chat_completion_request_event_response.response,
    )
    lm_response_event = log_response(ses, usr, request_event, lm_response)
    event_identifier = create_event_identifier(
        ses,
        usr,
        request_event,
        chat_completion_request_event_response.response.id,
    )
    # Evaluate before post-processing
    config_event, lm_response_event, event_identifier = await tup(
        config_event, lm_response_event, event_identifier
    ).evaluate(session=session_dep)
    # post-process the (request, response) pair
    if config.judge_evaluation:
        judge_score = judge(
            language_models_api_keys(ses, usr),
            chat_completion_request_event_response.request,
            chat_completion_request_event_response.response,
        )
        judge_score_event = log_lm_judge_evaluation(
            ses, usr, request_event, judge_score
        )
        evaluate.delay(judge_score.then(judge_score_event))
    return lm_response_event
