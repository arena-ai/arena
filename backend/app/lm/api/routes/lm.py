from typing import Mapping, Any

from fastapi import APIRouter
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.lm.models import ChatCompletion, ChatCompletionCreate, openai
from app.services.lm import (
    OpenAI,
    Mistral,
    Anthropic,
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
    return await OpenAI(api_key=openai_api_key.content).chat_completion(ccc=chat_completion_in)


@router.post("/mistral/v1/chat/completions", response_model=ChatCompletionMistral)
def mistral_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: Mapping
) -> ChatCompletionMistral:
    """
    Mistral integration
    """
    mistral_api_key = crud.get_setting(session=session, setting_name="MISTRAL_API_KEY", owner_id=current_user.id)
    return Mistral(api_key=mistral_api_key.content).native(ccc=chat_completion_in)



@router.post("/anthropic/v1/messages", response_model=ChatCompletionAnthropic)
def anthropic_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: Mapping
) -> ChatCompletionAnthropic:
    """
    Anthropic integration
    """
    anthropic_api_key = crud.get_setting(session=session, setting_name="ANTHROPIC_API_KEY", owner_id=current_user.id)
    return Anthropic(api_key=anthropic_api_key.content).native(ccc=chat_completion_in)


@router.post("/chat/completions", response_model=ChatCompletion)
def chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: ChatCompletionCreate
) -> ChatCompletion:
    """
    Abstract version
    """
    match chat_completion_in.model:
        case "gpt-4-0125-preview" | "gpt-4-turbo-preview" | "gpt-4-1106-preview" | "gpt-4-vision-preview" | "gpt-4" | "gpt-4-0314" | "gpt-4-0613" | "gpt-4-32k" | "gpt-4-32k-0314" | "gpt-4-32k-0613" | "gpt-3.5-turbo" | "gpt-3.5-turbo-16k" | "gpt-3.5-turbo-0301" | "gpt-3.5-turbo-0613" | "gpt-3.5-turbo-1106" | "gpt-3.5-turbo-0125" | "gpt-3.5-turbo-16k-0613":
            openai_api_key = crud.get_setting(session=session, setting_name="OPENAI_API_KEY", owner_id=current_user.id)
            response = OpenAI(api_key=openai_api_key.content).call(ccc=chat_completion_in)
        case "mistral-embed" | "mistral-large-2402" | "mistral-large-latest" | "mistral-medium" | "mistral-medium-2312" | "mistral-medium-latest" | "mistral-small" | "mistral-small-2312" | "mistral-small-2402" | "mistral-small-latest" | "mistral-tiny" | "mistral-tiny-2312" | "open-mistral-7b" | "open-mixtral-8x7b":
            mistral_api_key = crud.get_setting(session=session, setting_name="MISTRAL_API_KEY", owner_id=current_user.id)
            response =  Mistral(api_key=mistral_api_key.content).call(ccc=chat_completion_in)
        case "claude-3-opus-20240229" | "claude-3-sonnet-20240229" | "claude-3-haiku-20240307" | "claude-2.1" | "claude-2.0" | "claude-instant-1.2":
            anthropic_api_key = crud.get_setting(session=session, setting_name="ANTHROPIC_API_KEY", owner_id=current_user.id)
            response = Anthropic(api_key=anthropic_api_key.content).call(ccc=chat_completion_in)
    return response