from typing import Mapping, Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.lm.models import ChatCompletion, ChatCompletionCreate

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion as ChatCompletionOpenAI
from openai.types.chat.completion_create_params import CompletionCreateParams as ChatCompletionCreateOpenAI

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatCompletionResponse as ChatCompletionMistral

from anthropic import Anthropic
from anthropic.types import MessageCreateParams as ChatCompletionCreateAnthropic, Message as ChatCompletionAnthropic


router = APIRouter()


@router.post("/openai/chat/completions", response_model=ChatCompletionOpenAI)
def openai_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: Mapping
) -> ChatCompletionOpenAI:
    """
    OpenAI integration
    """
    openai_api_key = crud.get_setting(session=session, setting_name="OPENAI_API_KEY", owner_id=current_user.id)
    client = OpenAI(api_key=openai_api_key.content)
    return client.chat.completions.create(**chat_completion_in)


@router.post("/mistral/v1/chat/completions", response_model=ChatCompletionMistral)
def mistral_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: Mapping
) -> ChatCompletionMistral:
    """
    Mistral integration
    """
    mistral_api_key = crud.get_setting(session=session, setting_name="MISTRAL_API_KEY", owner_id=current_user.id)
    client = MistralClient(api_key=mistral_api_key.content)
    return client.chat(**chat_completion_in)


@router.post("/anthropic/v1/messages", response_model=ChatCompletionAnthropic)
def anthropic_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: Mapping
) -> ChatCompletionAnthropic:
    """
    Anthropic integration
    """
    anthropic_api_key = crud.get_setting(session=session, setting_name="ANTHROPIC_API_KEY", owner_id=current_user.id)
    client = Anthropic(api_key=anthropic_api_key.content)
    return client.messages.create(**chat_completion_in)


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
            client = OpenAI(api_key=openai_api_key.content)
            return client.chat.completions.create(**chat_completion_in.model_dump(exclude_none=True))
        # case 
        case "claude-3-opus-20240229" | "claude-3-sonnet-20240229" | "claude-3-haiku-20240307" | "claude-2.1" | "claude-2.0" | "claude-instant-1.2":
            anthropic_api_key = crud.get_setting(session=session, setting_name="ANTHROPIC_API_KEY", owner_id=current_user.id)
            client = Anthropic(api_key=anthropic_api_key.content)
            return client.messages.create(**chat_completion_in.model_dump(exclude_none=True))
