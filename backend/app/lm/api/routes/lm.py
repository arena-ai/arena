from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.lm.models import ChatCompletion, CreateChatCompletion, CreateChatCompletionOpenAI

from openai import OpenAI
from mistralai.client import MistralClient
from anthropic import Anthropic

router = APIRouter()


@router.post("/openai/chat/completions", response_model=ChatCompletion)
def openai_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: CreateChatCompletionOpenAI
) -> Any:
    """
    OpenAI integration
    """
    openai_api_key = crud.get_setting(session=session, setting_name="OPENAI_API_KEY", owner_id=current_user.id)
    client = OpenAI(api_key=openai_api_key.content)
    chat_completion = client.chat.completions.create(**chat_completion_in.model_dump(exclude_none=True))
    return ChatCompletion.from_openai(chat_completion)


@router.post("/mistral/chat/completions", response_model=ChatCompletion)
def mistral_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: CreateChatCompletion
) -> Any:
    """
    Mistral integration
    """
    mistral_api_key = crud.get_setting(session=session, setting_name="MISTRAL_API_KEY", owner_id=current_user.id)
    client = MistralClient(api_key=mistral_api_key.content)
    chat_completion = client.chat(**chat_completion_in.model_dump(exclude_none=True))
    return ChatCompletion.from_mistral(chat_completion)


@router.post("/anthropic/v1/messages", response_model=ChatCompletion)
def mistral_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: CreateChatCompletion
) -> Any:
    """
    Anthropic integration
    """
    anthropic_api_key = crud.get_setting(session=session, setting_name="ANTHROPIC_API_KEY", owner_id=current_user.id)
    client = Anthropic(api_key=anthropic_api_key.content)
    message = client.messages.create(**chat_completion_in.model_dump(exclude_none=True))
    return ChatCompletion.from_anthropic(message)