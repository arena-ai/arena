from typing import Any
import os
import random
# from functools import cached_property
from faker import Faker
from time import time
from rich import print
from dotenv import load_dotenv
from openai import OpenAI
from arena.client import Client
from arena.models import LMConfig, ChatCompletionRequest, Message, openai, mistral, anthropic
# Load .env
load_dotenv()

BASE_URL = "https://arena.sarus.app/api/v1"
# BASE_URL = "http://localhost/api/v1"

class Generator:
    def __init__(self) -> None:
        self.fake = Faker()

    def model(self) -> str:
        # return random.choice(openai.MODELS+mistral.MODELS+anthropic.MODELS)
        return random.choice(["gpt-4o", "gpt-3.5-turbo", "mistral-small", "claude-2.1"])
    
    def chat_completion_request(self) -> dict[str, Any]:
        name = self.fake.name_female()
        return ChatCompletionRequest(
            model=self.model(),
            messages=[
                Message(role='system', content='You write messages based on some content.'),
                Message(role='user', content=f'"{name}" wants to buy our product, we want to invite {name} to a last quick demo and discuss pricing before the contract is signed.'),
            ],
            temperature=0.8,
            max_tokens=1000,
        ).model_dump(mode='json', exclude_none=True)


generator = Generator()

print("\n[bold blue]Login")
username = "ng@sarus.tech"
password = "password"
try:
    arena = Client(username=username, password=password, base_url=BASE_URL)
except:
    print("\n[bold blue]Create the user")
    Client.user_open(email=username, password=password, full_name="Test", base_url=BASE_URL)
    arena = Client(username=username, password=password, base_url=BASE_URL)

arena.api_keys(
    os.getenv("ARENA_OPENAI_API_KEY"),
    os.getenv("ARENA_MISTRAL_API_KEY"),
    os.getenv("ARENA_ANTHROPIC_API_KEY"),
    )

print("\n[bold blue]Activate masking")
arena.lm_config(lm_config=LMConfig(pii_removal="masking", judge_evaluation=True, judge_with_pii=False))

print("\n[bold blue]Run experiments with masking")
for i in range(20):
    t = time()
    print(i)
    req = generator.chat_completion_request()
    print(f"request = {req}")
    resp = arena.chat_completions(**req)
    print(f"resp = {resp.choices[0].message.content} ({time()-t})")

print("\n[bold blue]Activate replacement")
arena.lm_config(lm_config=LMConfig(pii_removal="replace", judge_evaluation=True))

print("\n[bold blue]Run experiments with replacement")
for i in range(20):
    t = time()
    print(i)
    req = generator.chat_completion_request()
    print(f"request = {req}")
    resp = arena.chat_completions(**req)
    print(f"resp = {resp.choices[0].message.content} ({time()-t})")
