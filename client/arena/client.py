from httpx import Client


class Client:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url