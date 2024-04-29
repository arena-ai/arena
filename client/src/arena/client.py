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
        if not self.api_key:
            self.login()
    
    def login(self):
        assert(self.user and self.password)
        with httpx.Client() as client:
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

    def chat_completions(self, **kwargs: Any) -> ChatCompletionResponse:
        req = ChatCompletionRequest.model_validate(kwargs).model_dump(mode="json", exclude_unset=True, exclude_none=True)
        print(f"\nDEBUG {req}")
        with httpx.Client() as client:
            resp = client.post(
                url = f"{self.base_url}/lm/chat/completions",
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=req,
            )
        return resp