from typing import TypeVar, Generic, Mapping
from abc import ABC, abstractmethod

from anyio import create_task_group
from sqlmodel import Session

from app.api.deps import CurrentUser, SessionDep
from app.models import UserOut
from app.lm.models import (
    ChatCompletionResponse,
    ChatCompletionRequest,
    LMConfig,
)
import app.lm.models.openai as openai_models
import app.lm.models.mistral as mistral_models
import app.lm.models.anthropic as anthropic_models
from app.services import Request, Response
from app.ops import tup, Computation
from app.ops.settings import (
    openai_api_key,
    mistral_api_key,
    anthropic_api_key,
    language_models_api_keys,
    lm_config,
)
from app.ops.events import (
    log_request,
    LogRequest,
    log_response,
    create_event_identifier,
    log_lm_judge_evaluation,
    log_lm_config,
)
from app.ops.lm import (
    openai,
    openai_request,
    mistral,
    mistral_request,
    anthropic,
    anthropic_request,
    chat,
    chat_request,
    judge,
)
from app.ops.masking import masking, replace_masking
from app.ops.session import session, user, event
from app.worker import evaluate

Req = TypeVar("Req")
Resp = TypeVar("Resp")


class ChatCompletionHandler(ABC, Generic[Req, Resp]):
    def __init__(
        self,
        session_dep: SessionDep,
        current_user: CurrentUser,
        chat_completion_request: Mapping,
    ):
        self.session = session_dep
        self.user = current_user
        self.chat_completion_request = self.validate_chat_completion_request(
            chat_completion_request
        )

    @abstractmethod
    def validate_chat_completion_request(
        self, chat_completion_request: Mapping
    ) -> Req:
        pass

    @abstractmethod
    def arena_request(self) -> Request[Req]:
        pass

    def config(
        self, ses: Computation[Session], usr: Computation[UserOut]
    ) -> Computation[LMConfig]:
        return lm_config(ses, usr)

    @abstractmethod
    def lm_request(self) -> Computation[Request[Req]]:
        pass

    @abstractmethod
    def lm_response(
        self,
        ses: Computation[Session],
        usr: Computation[UserOut],
        request: Request[Req],
    ) -> Computation[Response[Resp]]:
        pass


    async def process_request(self) -> Resp:
        ses = session()
        usr = user(ses, self.user.id)
        # Arena request
        arena_request = self.arena_request()
        arena_request_event = log_request(ses, usr, None, arena_request)
        # We need the config now
        config = await self.config(ses, usr).evaluate(session=self.session)
        config_event = log_lm_config(ses, usr, arena_request_event, config)
        # Build the request
        lm_request = await self.lm_request().evaluate(session=self.session)
        print('messagges_prompt',lm_request.content.messages[0])
        print('messagges_doc',lm_request.content.messages[1])
        lm_request_event = arena_request_event
        mapping_list = []   
        # Do the masking
        if config.pii_removal:  # TODO an IF op could be added to build conditional delayed computations if needed
            if config.pii_removal == "masking":
                async with create_task_group() as tg:
                    for message in lm_request.content.messages:
                        async def set_content(message=message):
                            message.content = await masking(message.content).evaluate(session=self.session)
                        tg.start_soon(set_content)
            if config.pii_removal == "replace":
                async with create_task_group() as tg:
                    for message in lm_request.content.messages:
                        async def set_content(message=message):
                            message.content, _ = await replace_masking(message.content).evaluate(session=self.session)
                            print("mapping", _)
                            print("message.content", message.content)
                            mapping_list.append(_)
                        tg.start_soon(set_content)
            # Log the request event
            lm_request_event = LogRequest(name="modified_request")(ses, usr, arena_request_event, lm_request)
        # compute the response
        lm_response = self.lm_response(ses, usr, lm_request)
        lm_response_event = log_response(
            ses, usr, arena_request_event, lm_response
        )
        chat_completion_response = lm_response.content
        event_identifier = create_event_identifier(
            ses, usr, arena_request_event, chat_completion_response.id
        )
        # Evaluate before post-processing
        (
            arena_request_event,
            config_event,
            lm_request_event,
            lm_response_event,
            event_identifier,
            chat_completion_response,
        ) = await tup(
            arena_request_event,
            config_event,
            lm_request_event,
            lm_response_event,
            event_identifier,
            chat_completion_response,
        ).evaluate(session=self.session)
        # post-process the (request, response) pair

        if  config.pii_removal == "replace":
            chat_completion_data = chat_completion_response.choices[0].message.content
#should I pass the entire mapping_list to replace_back, or is there a consistent position (like first or second) for the mapping of the response?
            chat_completion_with_real_entities = replace_back(chat_completion_data, mapping_list[1])

        if config.judge_evaluation:
            judge_score = judge(
                language_models_api_keys(ses, usr),
                arena_request.content
                if config.judge_with_pii
                else lm_request.content,
                chat_completion_response,
            )
            judge_score_event = log_lm_judge_evaluation(
                ses, usr, event(ses, arena_request_event.id), judge_score
            )
            evaluate.delay(judge_score.then(judge_score_event))
        return chat_completion_with_real_entities

def replace_back(text: str, mapping: list[dict[str,str]]) -> str:
        for fake_entity, real_entity in mapping.items():
            print("text",text)
            text = text.replace(real_entity, fake_entity)
            print("text",text)
        return text

class OpenAIHandler(
    ChatCompletionHandler[
        openai_models.ChatCompletionRequest,
        openai_models.ChatCompletionResponse,
    ]
):
    def validate_chat_completion_request(
        self, chat_completion_request: Mapping
    ) -> openai_models.ChatCompletionRequest:
        return openai_models.ChatCompletionRequest.model_validate(
            chat_completion_request
        )

    def arena_request(self) -> Request[openai_models.ChatCompletionRequest]:
        return Request(
            method="POST",
            url="/openai/chat/completions",
            content=self.chat_completion_request.model_copy(deep=True),
        )

    def lm_request(
        self,
    ) -> Computation[Request[openai_models.ChatCompletionRequest]]:
        return openai_request(
            self.chat_completion_request.model_copy(deep=True)
        )

    def lm_response(
        self,
        ses: Computation[Session],
        usr: Computation[UserOut],
        request: Request[openai_models.ChatCompletionRequest],
    ) -> Computation[Response[openai_models.ChatCompletionResponse]]:
        return openai(openai_api_key(ses, usr), request.content)


class MistralHandler(
    ChatCompletionHandler[
        mistral_models.ChatCompletionRequest,
        mistral_models.ChatCompletionResponse,
    ]
):
    def validate_chat_completion_request(
        self, chat_completion_request: Mapping
    ) -> mistral_models.ChatCompletionRequest:
        return mistral_models.ChatCompletionRequest.model_validate(
            chat_completion_request
        )

    def arena_request(self) -> Request[mistral_models.ChatCompletionRequest]:
        return Request(
            method="POST",
            url="/mistral/v1/chat/completions",
            content=self.chat_completion_request.model_copy(deep=True),
        )

    def lm_request(
        self,
    ) -> Computation[Request[mistral_models.ChatCompletionRequest]]:
        return mistral_request(
            self.chat_completion_request.model_copy(deep=True)
        )

    def lm_response(
        self,
        ses: Computation[Session],
        usr: Computation[UserOut],
        request: Request[mistral_models.ChatCompletionRequest],
    ) -> Computation[Response[mistral_models.ChatCompletionResponse]]:
        return mistral(mistral_api_key(ses, usr), request.content)


class AnthropicHandler(
    ChatCompletionHandler[
        anthropic_models.ChatCompletionRequest,
        anthropic_models.ChatCompletionResponse,
    ]
):
    def validate_chat_completion_request(
        self, chat_completion_request: Mapping
    ) -> anthropic_models.ChatCompletionRequest:
        return anthropic_models.ChatCompletionRequest.model_validate(
            chat_completion_request
        )

    def arena_request(self) -> Request[anthropic_models.ChatCompletionRequest]:
        return Request(
            method="POST",
            url="/anthropic/v1/messages",
            content=self.chat_completion_request.model_copy(deep=True),
        )

    def lm_request(
        self,
    ) -> Computation[Request[anthropic_models.ChatCompletionRequest]]:
        return anthropic_request(
            self.chat_completion_request.model_copy(deep=True)
        )

    def lm_response(
        self,
        ses: Computation[Session],
        usr: Computation[UserOut],
        request: Request[anthropic_models.ChatCompletionRequest],
    ) -> Computation[Response[anthropic_models.ChatCompletionResponse]]:
        return anthropic(anthropic_api_key(ses, usr), request.content)


class ArenaHandler(
    ChatCompletionHandler[ChatCompletionRequest, ChatCompletionResponse]
):
    def validate_chat_completion_request(
        self, chat_completion_request: Mapping
    ) -> ChatCompletionRequest:
        return ChatCompletionRequest.model_validate(chat_completion_request)

    def arena_request(self) -> Request[ChatCompletionRequest]:
        return Request(
            method="POST",
            url="/chat/completions",
            content=self.chat_completion_request.model_copy(deep=True),
        )

    def config(
        self, ses: Computation[Session], usr: Computation[UserOut]
    ) -> Computation[LMConfig]:
        return lm_config(
            ses, usr, override=self.chat_completion_request.lm_config
        )

    def lm_request(self) -> Computation[Request[ChatCompletionRequest]]:
        return chat_request(self.chat_completion_request.model_copy(deep=True))

    def lm_response(
        self,
        ses: Computation[Session],
        usr: Computation[UserOut],
        request: Request[ChatCompletionRequest],
    ) -> Computation[Response[ChatCompletionResponse]]:
        return chat(language_models_api_keys(ses, usr), request.content)
