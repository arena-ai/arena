from typing import Any
import httpx
from arena.models import ChatCompletionRequest, ChatCompletionResponse

BASE_URL = "https://arena.sarus.app/api/v1"

class Client:
    def __init__(self, user: str | None = None, password: str | None = None, api_key: str | None = None, base_url: str = BASE_URL):
        self.user = user
        self.password = password
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = httpx.Timeout(30., read=None)
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
                    "username": "admin@sarus.tech",
                    "password": "EToqWBv5j9yjZTa",
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
        with httpx.Client() as client:
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
        with httpx.Client() as client:
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