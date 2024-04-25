from typing import Mapping, Any

from fastapi import APIRouter
from sqlmodel import Session, func, select

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.models import User, Event, EventCreate
from app.lm.models import LanguageModelsApiKeys, ChatCompletion, ChatCompletionCreate, openai, mistral, anthropic
from app.ops.settings import openai_api_key, mistral_api_key, anthropic_api_key, language_models_api_keys
from app.ops.events import BuildRequest, LogRequest, BuildResponse, LogResponse
from app.ops.lm import OpenAI, Mistral, Anthropic, Chat, Judge


router = APIRouter()


@router.post("/openai/chat/completions", response_model=openai.ChatCompletion)
async def openai_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: Mapping
) -> openai.ChatCompletion:
    """
    OpenAI integration
    """
    return await OpenAI()(openai_api_key(session, current_user), openai.ChatCompletionCreate.model_validate(chat_completion_in)).evaluate()


@router.post("/mistral/v1/chat/completions", response_model=mistral.ChatCompletion)
async def mistral_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: Mapping
) -> mistral.ChatCompletion:
    """
    Mistral integration
    """
    return await Mistral()(mistral_api_key(session, current_user), mistral.ChatCompletionCreate.model_validate(chat_completion_in)).evaluate()


@router.post("/anthropic/v1/messages", response_model=anthropic.ChatCompletion)
async def anthropic_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: Mapping
) -> anthropic.ChatCompletion:
    """
    Anthropic integration
    """
    return await Anthropic()(anthropic_api_key(session, current_user), anthropic.ChatCompletionCreate.model_validate(chat_completion_in)).evaluate()


async def chat_completion_request_event(session: Session, current_user: User, chat_completion_create: ChatCompletionCreate) -> Event:
    # Create a request event
    event_create = EventCreate(name="chat_completion_request", content=chat_completion_create.model_dump_json(), parent_id=None)
    event = crud.create_event(session=session, event_in=event_create, owner_id=current_user.id)
    return event


async def chat_completion_response_event(session: Session, current_user: User, request_event_id: int, chat_completion: ChatCompletion) -> Event:
    # Add the native identifier to the parent event
    crud.create_event_identifier(session=session, event_identifier=chat_completion.id, event_id=request_event_id)
    # Create a response event
    event_create = EventCreate(name="chat_completion_response", content=chat_completion.model_dump_json(), parent_id=request_event_id)
    event = crud.create_event(session=session, event_in=event_create, owner_id=current_user.id)
    return event


@router.post("/chat/completions", response_model=ChatCompletion)
async def chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: ChatCompletionCreate
) -> ChatCompletion:
    """
    Abstract version
    """
    response = Chat()(language_models_api_keys(session, current_user), ChatCompletionCreate.model_validate(chat_completion_in))
    return await response.evaluate()


@router.post("/chat/completions/request", response_model=Event)
async def chat_completion_request(
    session: SessionDep, current_user: CurrentUser, chat_completion_create: ChatCompletionCreate
) -> Event:
    return await chat_completion_request_event(session, current_user, chat_completion_create)


@router.post("/chat/completions/response/{request_event_id}", response_model=Event)
async def chat_completion_response(
    session: SessionDep, current_user: CurrentUser, request_event_id: int, chat_completion: ChatCompletion
) -> Event:
    return await chat_completion_response_event(session, current_user, request_event_id, chat_completion)