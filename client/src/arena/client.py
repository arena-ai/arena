from typing import Any, Type, Literal
import httpx
import mistralai.client
from arena.models import ChatCompletionRequest, ChatCompletionResponse, Evaluation, Score
import openai
import mistralai
import anthropic

BASE_URL = "https://arena.sarus.app/api/v1"

class Client:
    def __init__(self, user: str | None = None, password: str | None = None, api_key: str | None = None, base_url: str = BASE_URL):
        self.user = user
        self.password = password
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = 30.0
        if not self.api_key:
            self.login()
    
    def login(self):
        assert(self.user and self.password)
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                url = f"{self.base_url}/login/access-token",
                headers =  {
                    "accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data = {
                    "grant_type": "",
                    "username": self.user,
                    "password": self.password,
                    "scope": "",
                    "client_id": "",
                    "client_secret": "",
                },
            )
        self.api_key = resp.json()['access_token']
    
    def openai_api_key(self, api_key: str):
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

    def chat_completions(self, **kwargs: Any) -> ChatCompletionResponse:
        req = ChatCompletionRequest.model_validate(kwargs).model_dump(mode="json", exclude_unset=True, exclude_none=True)
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
    
    def evaluation(self, identifier: str, score: float) -> int:
        req = Evaluation(identifier=identifier, value=Score(value=score)).model_dump(mode="json", exclude_unset=True, exclude_none=True)
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
        if not hasattr(client, "_arena_decorated_"):
            client._arena_decorated_ = True
            if client == openai.OpenAI:
                self.decorate_openai(client)
            elif client == mistralai.client.MistralClient:
                self.decorate_mistral(client)
            elif client == anthropic.Anthropic:
                self.decorate_anthropic(client)

    def decorate_openai(self, client: Type[openai.OpenAI], mode: Literal['proxy', 'instrument'] = 'proxy'):
        arena = self
        openai_init = client.__init__
        def init(self, *args: Any, **kwargs: Any):
            openai_init(self, *args, **kwargs)
            arena.openai_api_key(self.api_key)
            self.api_key = arena.api_key
            self.base_url = f"{arena.base_url}/lm/openai"
        client.__init__ = init
    
    def decorate_mistral(self, client: Type[openai.OpenAI], mode: Literal['proxy', 'instrument'] = 'proxy'):
        arena = self
        openai_init = client.__init__
        def init(self, *args: Any, **kwargs: Any):
            openai_init(self, *args, **kwargs)
            arena.mistral_api_key(self.api_key)
            self.api_key = arena.api_key
            self.base_url = f"{arena.base_url}/lm/mistral"
        client.__init__ = init
    
    def decorate_anthropic(self, client: Type[openai.OpenAI], mode: Literal['proxy', 'instrument'] = 'proxy'):
        arena = self
        openai_init = client.__init__
        def init(self, *args: Any, **kwargs: Any):
            openai_init(self, *args, **kwargs)
            arena.anthropic_api_key(self.api_key)
            self.api_key = arena.api_key
            self.base_url = f"{arena.base_url}/lm/anthropic"
        client.__init__ = init
