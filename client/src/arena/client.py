import httpx
from arena.models import ChatCompletionRequest, ChatCompletionResponse

BASE_URL = "https://arena.sarus.app/api/v1"

class Client:
    def __init__(self, user: str | None, password: str | None, api_key: str | None, base_url: str = BASE_URL):
        self.user = user
        self.password = password
        self.api_key = api_key
        self.base_url = base_url
    
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
        self.api_key = resp.json()

    def chat_completion(self, req: ChatCompletionRequest) -> ChatCompletionResponse:
        with httpx.Client() as client:
            resp = client.post(
                url = f"{self.base_url}/chat/completion",
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                },
                content=req,
            )
        return resp