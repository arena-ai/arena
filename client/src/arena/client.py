from typing import Any, Type, Literal
import httpx
import mistralai.client
from arena.models import ChatCompletionRequest, ChatCompletionResponse, Evaluation, Score, LMConfig, EventOut, ChatCompletionRequestEventResponse
import arena.models.openai as oai
import arena.models.mistral as mis
import arena.models.anthropic as ant
import openai
import mistralai
import anthropic

BASE_URL = "https://arena.sarus.app/api/v1"

class Client:
    def __init__(self, username: str | None = None, password: str | None = None, api_key: str | None = None, base_url: str = BASE_URL):
        self.username = username
        self.password = password
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = 30.0
        if not self.api_key:
            self.login()
    
    
    def login(self):
        """Used internally to get a connection token from a user and a password"""
        assert(self.username and self.password)
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                url = f"{self.base_url}/login/access-token",
                headers =  {
                    "accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data = {
                    "grant_type": "",
                    "username": self.username,
                    "password": self.password,
                    "scope": "",
                    "client_id": "",
                    "client_secret": "",
                },
            )
        self.api_key = resp.json()['access_token']
    

    def user(self, email: str, password: str, full_name: str | None = None):
        """Create a new user"""
        with httpx.Client(timeout=self.timeout) as client:
            client.post(
                url = f"{self.base_url}/users/open",
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "email": email,
                    "password": password,
                    "full_name": full_name
                },
            )

    @staticmethod
    def user_open(email: str, password: str, full_name: str | None = None,  base_url=BASE_URL):
        """Create a new user"""
        with httpx.Client() as client:
            client.post(
                url = f"{base_url}/users/open",
                json={
                    "email": email,
                    "password": password,
                    "full_name": full_name
                },
            )


    def openai_api_key(self, api_key: str):
        """Set the OpenAI API token"""
        with httpx.Client(timeout=self.timeout) as client:
            client.post(
                url = f"{self.base_url}/settings/",
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "name": "OPENAI_API_KEY",
                    "content": api_key
                },
            )
    

    def mistral_api_key(self, api_key: str):
        """Set the Mistral API token"""
        with httpx.Client(timeout=self.timeout) as client:
            client.post(
                url = f"{self.base_url}/settings/",
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "name": "MISTRAL_API_KEY",
                    "content": api_key
                },
            )
    

    def anthropic_api_key(self, api_key: str):
        """Set the Anthropic API token"""
        with httpx.Client(timeout=self.timeout) as client:
            client.post(
                url = f"{self.base_url}/settings/",
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "name": "ANTHROPIC_API_KEY",
                    "content": api_key
                },
            )
    

    def api_keys(self, openai_api_key: str, mistral_api_key: str, anthropic_api_key: str):
        """Set all API tokens"""
        self.openai_api_key(openai_api_key)
        self.mistral_api_key(mistral_api_key)
        self.anthropic_api_key(anthropic_api_key)


    def lm_config(self, lm_config: LMConfig):
        """Set LM config"""
        with httpx.Client(timeout=self.timeout) as client:
            client.post(
                url = f"{self.base_url}/settings/",
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "name": "LM_CONFIG",
                    "content": lm_config.model_dump_json()
                },
            )


    def chat_completions(self, **kwargs: Any) -> ChatCompletionResponse:
        """Abstract chat completion"""
        req = ChatCompletionRequest.model_validate(kwargs).model_dump(mode="json", exclude_none=True)
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                url = f"{self.base_url}/lm/chat/completions",
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=req,
            )
        if resp.status_code == 200:
            return ChatCompletionResponse.model_validate(resp.json())
        else:
            raise RuntimeError(resp)
    
    def chat_completions_request(self, **kwargs: Any) -> EventOut:
        req = ChatCompletionRequest.model_validate(kwargs).model_dump(mode="json", exclude_none=True)
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                url = f"{self.base_url}/lm/chat/completions/request",
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=req,
            )
        if resp.status_code == 200:
            return EventOut.model_validate(resp.json())
        else:
            raise RuntimeError(resp)
    

    def chat_completions_response(self, **kwargs: Any) -> EventOut:
        req = ChatCompletionRequestEventResponse.model_validate(kwargs).model_dump(mode="json", exclude_none=True)
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                url = f"{self.base_url}/lm/chat/completions/response",
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=req,
            )
        if resp.status_code == 200:
            return EventOut.model_validate(resp.json())
        else:
            raise RuntimeError(resp)


    def evaluation(self, identifier: str, score: float) -> int:
        """Evaluate the response"""
        req = Evaluation(identifier=identifier, value=Score(value=score)).model_dump(mode="json", exclude_none=True)
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                url = f"{self.base_url}/lm/evaluation",
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=req,
            )
        if resp.status_code == 200:
            return resp.json()["id"]
        else:
            raise RuntimeError(resp)
    

    def decorate(self, client: Type, mode: Literal['proxy', 'instrument'] = 'proxy'):
        """Decorate the client"""
        if not hasattr(client, "_arena_decorated_"):
            client._arena_decorated_ = mode
            if client == openai.OpenAI:
                if mode == 'proxy':
                    self.decorate_openai_proxy(client)
                elif mode == 'instrument':
                    self.decorate_openai_instrument(client)
            elif client == mistralai.client.MistralClient:
                if mode == 'proxy':
                    self.decorate_mistral_proxy(client)
                elif mode == 'instrument':
                    self.decorate_mistral_instrument(client)
            elif client == anthropic.Anthropic:
                if mode == 'proxy':
                    self.decorate_anthropic_proxy(client)
                elif mode == 'instrument':
                    self.decorate_anthropic_instrument(client)


    def decorate_openai_proxy(self, client: Type[openai.OpenAI]):
        """Decorate openai client in proxy mode"""
        arena = self
        openai_init = client.__init__
        def init(self, *args: Any, **kwargs: Any):
            openai_init(self, *args, **kwargs)
            arena.openai_api_key(self.api_key)
            self.api_key = arena.api_key
            self.base_url = f"{arena.base_url}/lm/openai"
        client.__init__ = init
    

    def decorate_mistral_proxy(self, client: Type[mistralai.client.MistralClient]):
        """Decorate mistral client in proxy mode"""
        arena = self
        mistral_init = client.__init__
        def init(self, *args: Any, **kwargs: Any):
            mistral_init(self, *args, **kwargs)
            arena.mistral_api_key(self.api_key)
            self.api_key = arena.api_key
            self.base_url = f"{arena.base_url}/lm/mistral"
        client.__init__ = init
    

    def decorate_anthropic_proxy(self, client: Type[anthropic.Anthropic]):
        """Decorate anthropic client in proxy mode"""
        arena = self
        anthropic_init = client.__init__
        def init(self, *args: Any, **kwargs: Any):
            anthropic_init(self, *args, **kwargs)
            arena.anthropic_api_key(self.api_key)
            self.api_key = arena.api_key
            self.base_url = f"{arena.base_url}/lm/anthropic"
        client.__init__ = init
    

    def decorate_openai_instrument(self, client: Type[openai.OpenAI]):
        """Decorate openai client in instrument mode"""
        arena = self
        openai_init = client.__init__
        def init(self, *args: Any, **kwargs: Any):
            openai_init(self, *args, **kwargs)
            instance_create = self.chat.completions.create
            def chat_completion(*args: Any, **kwargs: Any):
                result = instance_create(*args, **kwargs)
                request = oai.ChatCompletionRequest(*args, **kwargs)
                request_event = arena.chat_completions_request(**request.model_dump(mode="json", exclude_none=True))
                response = oai.ChatCompletionResponse.model_validate(result.model_dump())
                arena.chat_completions_response(request=request, request_event_id=request_event.id, response=response)
                return result
            self.chat.completions.create = chat_completion
        client.__init__ = init
    

    def decorate_mistral_instrument(self, client: Type[mistralai.client.MistralClient]):
        """Decorate mistral client in instrument mode"""
        arena = self
        mistral_init = client.__init__
        def init(self, *args: Any, **kwargs: Any):
            mistral_init(self, *args, **kwargs)
            instance_chat = self.chat
            def chat_completion(*args: Any, **kwargs: Any):
                result = instance_chat(*args, **kwargs)
                request = mis.ChatCompletionRequest(*args, **kwargs)
                request_event = arena.chat_completions_request(**request.model_dump(mode="json", exclude_none=True))
                response = mis.ChatCompletionResponse.model_validate_json(result.model_dump_json())
                arena.chat_completions_response(request=request, request_event_id=request_event.id, response=response)
                return result
            self.chat = chat_completion
        client.__init__ = init
    

    def decorate_anthropic_instrument(self, client: Type[anthropic.Anthropic]):
        """Decorate anthropic client in instrument mode"""
        arena = self
        anthropic_init = client.__init__
        def init(self, *args: Any, **kwargs: Any):
            anthropic_init(self, *args, **kwargs)
            instance_create = self.messages.create
            def chat_completion(*args: Any, **kwargs: Any):
                result = instance_create(*args, **kwargs)
                request = ant.ChatCompletionRequest(*args, **kwargs)
                request_event = arena.chat_completions_request(**request.model_dump(mode="json", exclude_none=True))
                response = ant.ChatCompletionResponse.model_validate(result.model_dump())
                arena.chat_completions_response(request=request, request_event_id=request_event.id, response=response)
                return result
            self.messages.create = chat_completion
        client.__init__ = init
