import os
from time import time
from rich import print
from dotenv import load_dotenv
from openai import OpenAI
from arena.client import Client
from arena.models import LMConfig
# Load .env
load_dotenv()

BASE_URL = "http://localhost/api/v1"
# BASE_URL = "https://arena.sarus.app/api/v1"

print("\n[bold red]Decorated OpenAI chat completion")

print("\n[bold blue]Login")
username = "ng@sarus.tech"
password = "password"
try:
    arena = Client(username=username, password=password, base_url=BASE_URL)
except:
    print("\n[bold blue]Create the user")
    Client.user_open(email=username, password=password, full_name="Test", base_url=BASE_URL)
    arena = Client(username=username, password=password, base_url=BASE_URL)

print("\n[bold blue]Decorate openai client")
arena.decorate(OpenAI, mode='proxy')
arena.lm_config(lm_config=LMConfig(pii_removal="masking", judge_evaluation=True))
t = time()

print("\n[bold blue]Run the experiment")
# Everything is unchanged then
api_key = os.getenv("ARENA_OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Alice invited Bob for lunch. Bob will sit next to Alice. How many people are having lunch with Alice?"},
])
print(f"resp = {resp.choices[0].message.content} ({time()-t})")