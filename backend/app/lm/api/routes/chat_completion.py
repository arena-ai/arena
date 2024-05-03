from typing import Mapping, Any

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app import models
from app.lm.models import ChatCompletionResponse, ChatCompletionRequest
import app.lm.models.openai as oai
import app.lm.models.mistral as mis
import app.lm.models.anthropic as ant
from app.services import Request, Response
from app.ops import cst, tup
from app.ops.settings import openai_api_key, mistral_api_key, anthropic_api_key, language_models_api_keys
from app.ops.events import log_request, log_response, event_identifier, lm_judge_evaluation, user_evaluation
from app.ops.lm import openai, openai_request, mistral, mistral_request, anthropic, anthropic_request, chat, chat_request, judge
from app.ops.masking import masking, replace_masking
from app.ops.session import session, user, event
from app.worker import evaluate


router = APIRouter()


@router.post("/openai/chat/completions", response_model=oai.ChatCompletionResponse)
async def openai_chat_completion(
    session_dep: SessionDep, current_user: CurrentUser, chat_completion_request: Mapping
) -> oai.ChatCompletionResponse:
    """
    OpenAI integration
    """
    sess = session()
    usr = user(sess, current_user.id)
    input = oai.ChatCompletionRequest.model_validate(chat_completion_request)
    request = openai_request(input)
    request_event = log_request(sess, usr, None, request)
    response = openai(openai_api_key(sess, usr), input)
    response_event = log_response(sess, usr, request_event, response)
    output = response.content
    event_id = event_identifier(sess, usr, request_event, output.id)
    return await request_event.then(response_event).then(event_id).then(output).evaluate(session=session_dep)


@router.post("/mistral/v1/chat/completions", response_model=mis.ChatCompletionResponse)
async def mistral_chat_completion(
    session_dep: SessionDep, current_user: CurrentUser, chat_completion_request: Mapping
) -> mis.ChatCompletionResponse:
    """
    Mistral integration
    """
    sess = session()
    usr = user(sess, current_user.id)
    input = mis.ChatCompletionRequest.model_validate(chat_completion_request)
    request = mistral_request(input)
    request_event = log_request(sess, usr, None, request)
    response = mistral(mistral_api_key(sess, usr), input)
    response_event = log_response(sess, usr, request_event, response)
    output = response.content
    event_id = event_identifier(sess, usr, request_event, output.id)
    return await request_event.then(response_event).then(event_id).then(output).evaluate(session=session_dep)


@router.post("/anthropic/v1/messages", response_model=ant.ChatCompletionResponse)
async def anthropic_chat_completion(
    session_dep: SessionDep, current_user: CurrentUser, chat_completion_request: Mapping
) -> ant.ChatCompletionResponse:
    """
    Anthropic integration
    """
    sess = session()
    usr = user(sess, current_user.id)
    input = ant.ChatCompletionRequest.model_validate(chat_completion_request)
    request = anthropic_request(input)
    request_event = log_request(sess, usr, None, request)
    response = anthropic(anthropic_api_key(sess, usr), input)
    response_event = log_response(sess, usr, request_event, response)
    output = response.content
    event_id = event_identifier(sess, usr, request_event, output.id)
    return await request_event.then(response_event).then(event_id).then(output).evaluate(session=session_dep)


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_request: ChatCompletionRequest
) -> ChatCompletionResponse:
    """
    Abstract version
    """
    sess = session()
    usr = user(sess, current_user.id)
    chat_completion_request = ChatCompletionRequest.model_validate(chat_completion_request)
    if chat_completion_request.arena_parameters and chat_completion_request.arena_parameters.pii_removal:# TODO This should be asynchronously launched
        if chat_completion_request.arena_parameters.pii_removal == "masking":
            for message in chat_completion_request.messages:
                message.content = await masking(message.content).evaluate()
        if chat_completion_request.arena_parameters.pii_removal == "replace":
            for message in chat_completion_request.messages:
                message.content, _ = await replace_masking(message.content).evaluate()
    request = chat_request(chat_completion_request)
    request_event = log_request(sess, usr, None, request)
    api_keys = language_models_api_keys(sess, usr)
    response = chat(api_keys, chat_completion_request)
    response_event = log_response(sess, usr, request_event, response)
    chat_completion_response = response.content
    event_id = event_identifier(sess, usr, request_event, chat_completion_response.id)

    # Only the output has to be computed now
    request_event, chat_completion_response = await response_event.then(event_id).then(tup(request_event, chat_completion_response)).evaluate(session=session)
    # Everything else can be delayed
    request_event = event(sess, request_event.id)
    delayed_computation = request_event.then(chat_completion_response)
    # Optionally judge the result
    if chat_completion_request.arena_parameters and chat_completion_request.arena_parameters.judge_evaluation:
        judge_score = judge(api_keys, chat_completion_request, chat_completion_response)
        judge_score_event = lm_judge_evaluation(sess, usr, request_event, judge_score)
        delayed_computation = delayed_computation.then(judge_score).then(judge_score_event)
    evaluate.delay(delayed_computation)
    return chat_completion_response


@router.post("/chat/completions/request", response_model=models.Event)
async def chat_completion_request(
    session: SessionDep, current_user: CurrentUser, chat_completion_request: ChatCompletionRequest
) -> models.Event:
    sess = session()
    usr = user(sess, current_user.id)
    chat_completion_request = ChatCompletionRequest.model_validate(chat_completion_request)
    request = chat_request(chat_completion_request)
    request_event = log_request(sess, usr, None, request)
    return await request_event.evaluate(session=session)


@router.post("/chat/completions/response/{request_event_id}", response_model=models.Event)
async def chat_completion_response(
    session: SessionDep, current_user: CurrentUser, request_event: models.Event, chat_completion_response: ChatCompletionResponse
) -> models.Event:
    sess = session()
    usr = user(sess, current_user.id)
    chat_completion_request = Request.model_validate_json(request_event.content)
    response = Response(status_code=200, headers={}, content=chat_completion_response)
    response_event = log_response(sess, usr, request_event, response)
    api_keys = language_models_api_keys(sess, usr)
    event_id = event_identifier(sess, usr, request_event, chat_completion_response.id)
    # Everything can be delayed
    computation = event_id
    # Optionally judge the result
    if chat_completion_request.arena_parameters and chat_completion_request.arena_parameters.judge_evaluation:
        judge_score = judge(api_keys, chat_completion_request, chat_completion_response)
        judge_score_event = lm_judge_evaluation(sess, usr, request_event, judge_score)
        computation = computation.then(judge_score).then(judge_score_event)
    computation = computation.then(response_event)
    return await computation.evaluate(session=session)
