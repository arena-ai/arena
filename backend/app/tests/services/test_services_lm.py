import os
from anyio import run
from app.services.lm import OpenAI

def test_openai(chat_completion_create_openai) -> None:
    openai_client = OpenAI(api_key=os.getenv("ARENA_OPENAI_API_KEY"))
    print(openai_client.headers)
    response = run(openai_client.openai_chat_completion, chat_completion_create_openai)
    print(response)