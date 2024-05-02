from typing import Mapping, Any

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app import models
from app.lm.models import ChatCompletionResponse, ChatCompletionRequest, openai, mistral, anthropic
from app.services import Request, Response
from app.ops import cst, tup
from app.ops.settings import openai_api_key, mistral_api_key, anthropic_api_key, language_models_api_keys
from app.ops.events import LogRequest, LogResponse, EventIdentifier, LMJudgeEvaluation, UserEvaluation
from app.ops.lm import OpenAI, OpenAIRequest, Mistral, MistralRequest, Anthropic, AnthropicRequest, Chat, ChatRequest, Judge
from app.ops.masking import Masking, ReplaceMasking
from app.ops.session import Session, User, Event
from app.worker import evaluate


router = APIRouter()


@router.post("/openai/chat/completions", response_model=openai.ChatCompletionResponse)
async def openai_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_request: Mapping
) -> openai.ChatCompletionResponse:
    """
    OpenAI integration
    """
    sess = Session()()
    user = User()(sess, current_user.id)
    input = openai.ChatCompletionRequest.model_validate(chat_completion_request)
    request = OpenAIRequest()(input)
    request_event = LogRequest()(sess, user, None, request)
    response = OpenAI()(openai_api_key(sess, user), input)
    response_event = LogResponse()(sess, user, request_event, response)
    output = response.content
    event_identifier = EventIdentifier()(sess, user, request_event, output.id)
    return await request_event.then(response_event).then(event_identifier).then(output).evaluate(session=session)


@router.post("/mistral/v1/chat/completions", response_model=mistral.ChatCompletionResponse)
async def mistral_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_request: Mapping
) -> mistral.ChatCompletionResponse:
    """
    Mistral integration
    """
    sess = Session()()
    user = User()(sess, current_user.id)
    input = mistral.ChatCompletionRequest.model_validate(chat_completion_request)
    request = MistralRequest()(input)
    request_event = LogRequest()(sess, user, None, request)
    response = Mistral()(mistral_api_key(sess, user), input)
    response_event = LogResponse()(sess, user, request_event, response)
    output = response.content
    event_identifier = EventIdentifier()(sess, user, request_event, output.id)
    return await request_event.then(response_event).then(event_identifier).then(output).evaluate(session=session)


@router.post("/anthropic/v1/messages", response_model=anthropic.ChatCompletionResponse)
async def anthropic_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_request: Mapping
) -> anthropic.ChatCompletionResponse:
    """
    Anthropic integration
    """
    sess = Session()()
    user = User()(sess, current_user.id)
    input = anthropic.ChatCompletionRequest.model_validate(chat_completion_request)
    request = AnthropicRequest()(input)
    request_event = LogRequest()(session, user, None, request)
    response = Anthropic()(anthropic_api_key(session, user), input)
    response_event = LogResponse()(session, user, request_event, response)
    output = response.content
    event_identifier = EventIdentifier()(session, user, request_event, output.id)
    return await request_event.then(response_event).then(event_identifier).then(output).evaluate(session=session)


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_request: ChatCompletionRequest
) -> ChatCompletionResponse:
    """
    Abstract version
    """
    sess = Session()()
    user = User()(sess, current_user.id)
    chat_completion_request = ChatCompletionRequest.model_validate(chat_completion_request)
    if chat_completion_request.arena_parameters and chat_completion_request.arena_parameters.pii_removal:# TODO This should be asynchronously launched
        if chat_completion_request.arena_parameters.pii_removal == "masking":
            for message in chat_completion_request.messages:
                message.content = await Masking()(message.content).evaluate()
        if chat_completion_request.arena_parameters.pii_removal == "replace":
            for message in chat_completion_request.messages:
                message.content, _ = await ReplaceMasking()(message.content).evaluate()
    request = ChatRequest()(chat_completion_request)
    request_event = LogRequest()(sess, user, None, request)
    api_keys = language_models_api_keys(sess, user)
    response = Chat()(api_keys, chat_completion_request)
    response_event = LogResponse()(sess, user, request_event, response)
    chat_completion_response = response.content
    event_identifier = EventIdentifier()(sess, user, request_event, chat_completion_response.id)

    # Only the output has to be computed now
    request_event, chat_completion_response = await response_event.then(event_identifier).then(tup(request_event, chat_completion_response)).evaluate(session=session)
    # Everything else can be delayed
    request_event = Event()(sess, request_event.id)
    delayed_computation = request_event.then(chat_completion_response)
    # Optionally judge the result
    if chat_completion_request.arena_parameters and chat_completion_request.arena_parameters.judge_evaluation:
        judge_score = Judge()(api_keys, chat_completion_request, chat_completion_response)
        judge_score_event = LMJudgeEvaluation()(sess, user, request_event, judge_score)
        delayed_computation = delayed_computation.then(judge_score).then(judge_score_event)
    evaluate.delay(delayed_computation)
    return chat_completion_response


@router.post("/chat/completions/request", response_model=models.Event)
async def chat_completion_request(
    session: SessionDep, current_user: CurrentUser, chat_completion_request: ChatCompletionRequest
) -> models.Event:
    sess = Session()()
    user = User()(sess, current_user.id)
    chat_completion_request = ChatCompletionRequest.model_validate(chat_completion_request)
    request = ChatRequest()(chat_completion_request)
    request_event = LogRequest()(sess, user, None, request)
    return await request_event.evaluate(session=session)


@router.post("/chat/completions/response/{request_event_id}", response_model=models.Event)
async def chat_completion_response(
    session: SessionDep, current_user: CurrentUser, request_event: models.Event, chat_completion_response: ChatCompletionResponse
) -> models.Event:
    sess = Session()()
    user = User()(sess, current_user.id)
    chat_completion_request = Request.model_validate_json(request_event.content)
    response = Response(status_code=200, headers={}, content=chat_completion_response)
    response_event = LogResponse()(sess, user, request_event, response)
    api_keys = language_models_api_keys(sess, user)
    event_identifier = EventIdentifier()(sess, user, request_event, chat_completion_response.id)
    # Everything can be delayed
    computation = event_identifier
    # Optionally judge the result
    if chat_completion_request.arena_parameters and chat_completion_request.arena_parameters.judge_evaluation:
        judge_score = Judge()(api_keys, chat_completion_request, chat_completion_response)
        judge_score_event = LMJudgeEvaluation()(sess, user, request_event, judge_score)
        computation = computation.then(judge_score).then(judge_score_event)
    computation = computation.then(response_event)
    return await computation.evaluate(session=session)
