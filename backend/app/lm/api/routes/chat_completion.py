from typing import Mapping, TypeVar, Generic
from anyio import create_task_group
from abc import ABC, abstractmethod

from fastapi import APIRouter
from sqlmodel import Session

from app.api.deps import CurrentUser, SessionDep
from app.models import UserOut, EventOut
from app.lm.models import ChatCompletionResponse, ChatCompletionRequest, LMConfig, ChatCompletionRequestEventResponse
import app.lm.models.openai as oai
import app.lm.models.mistral as mis
import app.lm.models.anthropic as ant
from app.services import Request, Response
from app.ops import cst, tup, Computation
from app.ops.settings import openai_api_key, mistral_api_key, anthropic_api_key, language_models_api_keys, lm_config
from app.ops.events import log_request, LogRequest, log_response, create_event_identifier, log_lm_judge_evaluation
from app.ops.lm import openai, openai_request, mistral, mistral_request, anthropic, anthropic_request, chat, chat_request, judge
from app.ops.masking import masking, replace_masking
from app.ops.session import session, user, event
from app.worker import evaluate


router = APIRouter()

Req = TypeVar("Req")
Resp = TypeVar("Resp")

class ChatCompletionHandler(ABC, Generic[Req, Resp]):
    def __init__(self, session_dep: SessionDep, current_user: CurrentUser, chat_completion_request: Mapping):
        self.session = session_dep
        self.user = current_user
        self.chat_completion_request = self.validate_chat_completion_request(chat_completion_request)
    
    @abstractmethod
    def validate_chat_completion_request(self, chat_completion_request: Mapping) -> Req:
        pass
    
    @abstractmethod
    def arena_request(self) -> Request[Req]:
        pass

    def config(self, ses: Computation[Session], usr: Computation[UserOut]) -> Computation[LMConfig]:
        return lm_config(ses, usr)

    @abstractmethod
    def lm_request(self) -> Computation[Request[Req]]:
        pass
    
    @abstractmethod
    def lm_response(self, ses: Computation[Session], usr: Computation[UserOut], request: Request[Req]) -> Computation[Response[Resp]]:
        pass

    async def process_request(self) -> Resp:
        ses = session()
        usr = user(ses, self.user.id)
        # We need the config now
        config = await self.config(ses, usr).evaluate(session=self.session)
        arena_request = self.arena_request()
        arena_request_event = log_request(ses, usr, None, arena_request)
        # Build the request
        lm_request = await self.lm_request().evaluate(session=self.session)
        lm_request_event = arena_request_event
        # Do the masking
        if config.pii_removal:# TODO an IF op could be added to build conditional delayed computations if needed
            if config.pii_removal == "masking":
                async with create_task_group() as tg:
                    for message in lm_request.content.messages:
                        async def set_content():
                            message.content = await masking(message.content).evaluate(session=self.session)
                        tg.start_soon(set_content)
            if config.pii_removal == "replace":
                async with create_task_group() as tg:
                    for message in lm_request.content.messages:
                        async def set_content():
                            message.content, _ = await replace_masking(message.content).evaluate(session=self.session)
                        tg.start_soon(set_content)
            # Log the request event
            lm_request_event = LogRequest(name="modified_request")(ses, usr, arena_request_event, lm_request)
        # compute the response
        lm_response = self.lm_response(ses, usr, lm_request)
        lm_response_event = log_response(ses, usr, arena_request_event, lm_response)
        chat_completion_response = lm_response.content
        event_identifier = create_event_identifier(ses, usr, arena_request_event, chat_completion_response.id)
        # Evaluate before post-processing
        arena_request_event, lm_request_event, lm_response_event, event_identifier, chat_completion_response = await tup(arena_request_event, lm_request_event, lm_response_event, event_identifier, chat_completion_response).evaluate(session=self.session)
        # post-process the (request, response) pair
        if config.judge_evaluation:
            judge_score = judge(language_models_api_keys(ses, usr), self.chat_completion_request, chat_completion_response)
            judge_score_event = log_lm_judge_evaluation(ses, usr, event(ses, arena_request_event.id), judge_score)
            evaluate.delay(judge_score.then(judge_score_event))
        return chat_completion_response


class OpenAIHandler(ChatCompletionHandler[oai.ChatCompletionRequest, oai.ChatCompletionResponse]):
    def validate_chat_completion_request(self, chat_completion_request: Mapping) -> oai.ChatCompletionRequest:
        return oai.ChatCompletionRequest.model_validate(chat_completion_request)
    
    def arena_request(self) -> Request[oai.ChatCompletionRequest]:
        return Request(
            method="POST",
            url="/openai/chat/completions",
            content=self.chat_completion_request
        )
    
    def lm_request(self) -> Computation[Request[oai.ChatCompletionRequest]]:
        return openai_request(self.chat_completion_request.model_copy())

    def lm_response(self, ses: Computation[Session], usr: Computation[UserOut], request: Request[oai.ChatCompletionRequest]) -> Computation[Response[oai.ChatCompletionResponse]]:
        return openai(openai_api_key(ses, usr), request.content)

@router.post("/openai/chat/completions", response_model=oai.ChatCompletionResponse)
async def openai_chat_completion(
    session_dep: SessionDep, current_user: CurrentUser, chat_completion_request: Mapping
) -> oai.ChatCompletionResponse:
    """
    OpenAI integration
    """
    return await OpenAIHandler(session_dep, current_user, chat_completion_request).process_request()


class MistralHandler(ChatCompletionHandler[mis.ChatCompletionRequest, mis.ChatCompletionResponse]):
    def validate_chat_completion_request(self, chat_completion_request: Mapping) -> mis.ChatCompletionRequest:
        return mis.ChatCompletionRequest.model_validate(chat_completion_request)
    
    def arena_request(self) -> Request[mis.ChatCompletionRequest]:
        return Request(
            method="POST",
            url="/mistral/v1/chat/completions",
            content=self.chat_completion_request
        )
    
    def lm_request(self) -> Computation[Request[mis.ChatCompletionRequest]]:
        return mistral_request(self.chat_completion_request.model_copy())

    def lm_response(self, ses: Computation[Session], usr: Computation[UserOut], request: Request[mis.ChatCompletionRequest]) -> Computation[Response[mis.ChatCompletionResponse]]:
        return mistral(mistral_api_key(ses, usr), request.content)

@router.post("/mistral/v1/chat/completions", response_model=mis.ChatCompletionResponse)
async def mistral_chat_completion(
    session_dep: SessionDep, current_user: CurrentUser, chat_completion_request: Mapping
) -> mis.ChatCompletionResponse:
    """
    Mistral integration
    """
    return await MistralHandler(session_dep, current_user, chat_completion_request).process_request()


class AnthropicHandler(ChatCompletionHandler[ant.ChatCompletionRequest, ant.ChatCompletionResponse]):
    def validate_chat_completion_request(self, chat_completion_request: Mapping) -> ant.ChatCompletionRequest:
        return ant.ChatCompletionRequest.model_validate(chat_completion_request)
    
    def arena_request(self) -> Request[ant.ChatCompletionRequest]:
        return Request(
            method="POST",
            url="/anthropic/v1/messages",
            content=self.chat_completion_request
        )
    
    def lm_request(self) -> Computation[Request[ant.ChatCompletionRequest]]:
        return anthropic_request(self.chat_completion_request.model_copy())

    def lm_response(self, ses: Computation[Session], usr: Computation[UserOut], request: Request[ant.ChatCompletionRequest]) -> Computation[Response[ant.ChatCompletionResponse]]:
        return anthropic(anthropic_api_key(ses, usr), request.content)

@router.post("/anthropic/v1/messages", response_model=ant.ChatCompletionResponse)
async def anthropic_chat_completion(
    session_dep: SessionDep, current_user: CurrentUser, chat_completion_request: Mapping
) -> ant.ChatCompletionResponse:
    """
    Anthropic integration
    """
    return await AnthropicHandler(session_dep, current_user, chat_completion_request).process_request()


class ArenaHandler(ChatCompletionHandler[ChatCompletionRequest, ChatCompletionResponse]):
    def validate_chat_completion_request(self, chat_completion_request: Mapping) -> ChatCompletionRequest:
        return ChatCompletionRequest.model_validate(chat_completion_request)
    
    def arena_request(self) -> Request[ChatCompletionRequest]:
        return Request(
            method="POST",
            url="/chat/completions",
            content=self.chat_completion_request
        )

    def config(self, ses: Computation[Session], usr: Computation[UserOut]) -> Computation[LMConfig]:
        return lm_config(ses, usr, override=self.chat_completion_request.lm_config)
    
    def lm_request(self) -> Computation[Request[ChatCompletionRequest]]:
        return chat_request(self.chat_completion_request.model_copy())

    def lm_response(self, ses: Computation[Session], usr: Computation[UserOut], request: Request[ChatCompletionRequest]) -> Computation[Response[ChatCompletionResponse]]:
        return chat(language_models_api_keys(ses, usr), request.content)

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(
    session_dep: SessionDep, current_user: CurrentUser, chat_completion_request: ChatCompletionRequest
) -> ChatCompletionResponse:
    """
    Abstract version
    """
    return await ArenaHandler(session_dep, current_user, chat_completion_request).process_request()


@router.post("/chat/completions/request", response_model=EventOut)
async def chat_completion_request(
    session_dep: SessionDep, current_user: CurrentUser, chat_completion_request: ChatCompletionRequest
) -> EventOut:
    ses = session()
    usr = user(ses, current_user.id)
    chat_completion_request = ChatCompletionRequest.model_validate(chat_completion_request)
    lm_request = chat_request(chat_completion_request)
    lm_request_event = log_request(ses, usr, None, lm_request)
    return await lm_request_event.evaluate(session=session_dep)


@router.post("/chat/completions/response", response_model=EventOut)
async def chat_completion_response(
    session_dep: SessionDep, current_user: CurrentUser, chat_completion_request_event_response: ChatCompletionRequestEventResponse
) -> EventOut:
    ses = session()
    usr = user(ses, current_user.id)
    request_event = event(ses, chat_completion_request_event_response.request_event_id)
    config = await lm_config(ses, usr).evaluate(session=session_dep)
    lm_response = Response(status_code=200, headers={}, content=chat_completion_request_event_response.response)
    lm_response_event = log_response(ses, usr, request_event, lm_response)
    event_identifier = create_event_identifier(ses, usr, request_event, chat_completion_request_event_response.response.id)
    # Evaluate before post-processing
    lm_response_event, event_identifier = await tup(lm_response_event, event_identifier).evaluate(session=session_dep)
    # post-process the (request, response) pair
    if config.judge_evaluation:
        judge_score = judge(language_models_api_keys(ses, usr), chat_completion_request_event_response.request, chat_completion_request_event_response.response)
        judge_score_event = log_lm_judge_evaluation(ses, usr, request_event, judge_score)
        evaluate.delay(judge_score.then(judge_score_event))
    return lm_response_event
