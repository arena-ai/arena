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
from arena.models import LMConfig, ChatCompletionRequest, Message
# Load .env
load_dotenv()

# BASE_URL = "https://arena.sarus.app/api/v1"
BASE_URL = "http://localhost/api/v1"

class Generator:
    def __init__(self) -> None:
        self.fake = Faker()

    def model(self) -> str:
        return random.choice([
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "mistral-large-latest", "mistral-medium", "mistral-medium-latest", "mistral-small", "mistral-small-latest", "mistral-tiny",
            "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-2.1", "claude-2.0",
        ])

    def participants(self, n_max: int=7) -> list[str]:
        return [self.fake.name() for _ in range(random.randint(1, n_max))]

    def fact(self, participants: list[str]):
        if len(participants) == 1:
            return random.choice([
                f"{participants[0]} is in a pretty good mood today.",
                f"{participants[0]} was late for a meeting.",
            ])
        elif len(participants) == 2:
            return random.choice([
                f"{participants[0]} talked to {participants[1]}.",
                f"{participants[0]} invited {participants[1]}.",
                f"{participants[0]} was seated just next to {participants[1]}.",
            ])
        else:
            return random.choice([
                f"They where all present the other day: {', '.join(participants[:-1])} and {participants[-1]}.",
                f"{participants[0]} invited his friends: {', '.join(participants[1:-1])} and {participants[-1]}.",
            ])
        
    def facts(self, n_max: int=5) -> str:
        participants = self.participants()
        return [self.fact(random.sample(participants, random.randint(1, len(participants)))) for _ in range(random.randint(1, n_max))]
    
    def chat_completion_request(self) -> dict[str, Any]:
        facts = '\n '.join(self.facts())
        return ChatCompletionRequest(
            model=self.model(),
            messages=[
                Message(role='system', content='You are a helpful assistant.'),
                Message(role='user', content=f'In the following story:\n"{facts}"\nCan you tell how many people are involved?'),
            ],
            temperature=1.2,
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
arena.lm_config(lm_config=LMConfig(pii_removal="masking", judge_evaluation=True))

print("\n[bold blue]Run experiments with masking")
for i in range(50):
    t = time()
    print(i)
    req = generator.chat_completion_request()
    print(f"request = {req}")
    resp = arena.chat_completions(**req)
    print(f"resp = {resp.choices[0].message.content} ({time()-t})")

print("\n[bold blue]Activate replacement")
arena.lm_config(lm_config=LMConfig(pii_removal="replace", judge_evaluation=True))

print("\n[bold blue]Run experiments with replacement")
for i in range(50):
    t = time()
    print(i)
    req = generator.chat_completion_request()
    print(f"request = {req}")
    resp = arena.chat_completions(**req)
    print(f"resp = {resp.choices[0].message.content} ({time()-t})")