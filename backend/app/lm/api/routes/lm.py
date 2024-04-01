from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.lm.models import ChatCompletion, CreateChatCompletion

from openai import OpenAI

router = APIRouter()


@router.post("/openai/chat/completions", response_model=ChatCompletion)
def openai_chat_completion(
    session: SessionDep, current_user: CurrentUser, chat_completion_in: CreateChatCompletion
) -> Any:
    """
    OpenAI integration
    """
    openai_api_key = crud.get_setting(session=session, setting_name="OPENAI_API_KEY")
    client = OpenAI(api_key=openai_api_key)
    chat_completion = client.chat.completions(completions=CreateChatCompletion)
    return ChatCompletion.model_validate(chat_completion)

