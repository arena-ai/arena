from typing import Mapping, Any

from fastapi import APIRouter
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.lm.models import LanguageModelsApiKeys, ChatCompletion, ChatCompletionCreate, openai, mistral, anthropic
from app.services.lm import (
    OpenAI,
    Mistral,
    Anthropic,
    LanguageModels,
)


router = APIRouter()


@router.post("/openai/chat/completions", response_model=openai.ChatCompletion)
async def openai_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: Mapping
) -> openai.ChatCompletion:
    """
    OpenAI integration
    """
    openai_api_key = crud.get_setting(session=session, setting_name="OPENAI_API_KEY", owner_id=current_user.id)
    return await OpenAI(api_key=openai_api_key.content).openai_chat_completion(ccc=openai.ChatCompletionCreate.model_validate(chat_completion_in))


@router.post("/mistral/v1/chat/completions", response_model=mistral.ChatCompletion)
async def mistral_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: Mapping
) -> mistral.ChatCompletion:
    """
    Mistral integration
    """
    mistral_api_key = crud.get_setting(session=session, setting_name="MISTRAL_API_KEY", owner_id=current_user.id)
    return await Mistral(api_key=mistral_api_key.content).mistral_chat_completion(ccc=mistral.ChatCompletionCreate.model_validate(chat_completion_in))


@router.post("/anthropic/v1/messages", response_model=anthropic.ChatCompletion)
async def anthropic_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: Mapping
) -> anthropic.ChatCompletion:
    """
    Anthropic integration
    """
    anthropic_api_key = crud.get_setting(session=session, setting_name="ANTHROPIC_API_KEY", owner_id=current_user.id)
    return await Anthropic(api_key=anthropic_api_key.content).anthropic_chat_completion(ccc=anthropic.ChatCompletionCreate.model_validate(chat_completion_in))


@router.post("/chat/completions", response_model=ChatCompletion)
async def chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: ChatCompletionCreate
) -> ChatCompletion:
    """
    Abstract version
    """
    openai_api_key = crud.get_setting(session=session, setting_name="OPENAI_API_KEY", owner_id=current_user.id)
    mistral_api_key = crud.get_setting(session=session, setting_name="MISTRAL_API_KEY", owner_id=current_user.id)
    anthropic_api_key = crud.get_setting(session=session, setting_name="ANTHROPIC_API_KEY", owner_id=current_user.id)
    api_keys = LanguageModelsApiKeys(
        openai_api_key = None if openai_api_key is None else openai_api_key.content,
        mistral_api_key = None if mistral_api_key is None else mistral_api_key.content,
        anthropic_api_key = None if anthropic_api_key is None else anthropic_api_key.content,
    )
    return await LanguageModels(api_keys=api_keys).chat_completion(ccc=chat_completion_in)
