from typing import Mapping, Any

from fastapi import APIRouter
from sqlmodel import Session, func, select

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.models import User, Event, EventCreate
from app.lm.models import LanguageModelsApiKeys, ChatCompletionResponse, ChatCompletionRequest, openai, mistral, anthropic
from app.ops.settings import openai_api_key, mistral_api_key, anthropic_api_key, language_models_api_keys
from app.ops.events import LogRequest, LogResponse, EventIdentifier
from app.ops.lm import OpenAI, OpenAIRequest, Mistral, MistralRequest, Anthropic, AnthropicRequest, Chat, ChatRequest, Judge


router = APIRouter()


@router.post("/openai/chat/completions", response_model=openai.ChatCompletionResponse)
async def openai_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_request: Mapping
) -> openai.ChatCompletionResponse:
    """
    OpenAI integration
    """
    input = openai.ChatCompletionRequest.model_validate(chat_completion_request)
    request = OpenAIRequest()(input)
    request_event = LogRequest()(session, current_user, None, request)
    response = OpenAI()(openai_api_key(session, current_user), input)
    response_event = LogResponse()(session, current_user, request_event, response)
    output = response.content
    event_identifier = EventIdentifier()(session, current_user, request_event, output.id)
    return await request_event.then(response_event).then(event_identifier).then(output).evaluate()


@router.post("/mistral/v1/chat/completions", response_model=mistral.ChatCompletionResponse)
async def mistral_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_request: Mapping
) -> mistral.ChatCompletionResponse:
    """
    Mistral integration
    """
    input = mistral.ChatCompletionRequest.model_validate(chat_completion_request)
    request = MistralRequest()(input)
    request_event = LogRequest()(session, current_user, None, request)
    response = Mistral()(mistral_api_key(session, current_user), input)
    response_event = LogResponse()(session, current_user, request_event, response)
    output = response.content
    event_identifier = EventIdentifier()(session, current_user, request_event, output.id)
    return await request_event.then(response_event).then(event_identifier).then(output).evaluate()


@router.post("/anthropic/v1/messages", response_model=anthropic.ChatCompletionResponse)
async def anthropic_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_request: Mapping
) -> anthropic.ChatCompletionResponse:
    """
    Anthropic integration
    """
    input = anthropic.ChatCompletionRequest.model_validate(chat_completion_request)
    request = AnthropicRequest()(input)
    request_event = LogRequest()(session, current_user, None, request)
    response = Anthropic()(anthropic_api_key(session, current_user), input)
    response_event = LogResponse()(session, current_user, request_event, response)
    output = response.content
    event_identifier = EventIdentifier()(session, current_user, request_event, output.id)
    return await request_event.then(response_event).then(event_identifier).then(output).evaluate()


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_request: ChatCompletionRequest
) -> ChatCompletionResponse:
    """
    Abstract version
    """
    input = ChatCompletionRequest.model_validate(chat_completion_request)
    request = ChatRequest()(input)
    request_event = LogRequest()(session, current_user, None, request)
    response = Chat()(language_models_api_keys(session, current_user), input)
    response_event = LogResponse()(session, current_user, request_event, response)
    output = response.content
    event_identifier = EventIdentifier()(session, current_user, request_event, output.id)
    return await request_event.then(response_event).then(event_identifier).then(output).evaluate()


@router.post("/chat/completions/request", response_model=Event)
async def chat_completion_request(
    session: SessionDep, current_user: CurrentUser, chat_completion_request: ChatCompletionRequest
) -> Event:
    input = ChatCompletionRequest.model_validate(chat_completion_request)
    request = ChatRequest()(input)
    request_event = LogRequest()(session, current_user, None, request)
    return await request_event.evaluate()


@router.post("/chat/completions/response/{request_event_id}", response_model=Event)
async def chat_completion_response(
    session: SessionDep, current_user: CurrentUser, request_event: Event, chat_completion_response: ChatCompletionResponse
) -> Event:
    response_event = LogResponse()(session, current_user, request_event, chat_completion_response)
    return await response_event.evaluate()