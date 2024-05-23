import os
from random import randint
from dotenv import load_dotenv
# Load .env
load_dotenv()
from arena.models import Choice, Message
from arena import Client, LMConfig, ChatCompletionRequest, ChatCompletionResponse, ChatCompletionRequestEventResponse

BASE_URL = "http://localhost/api/v1"
# BASE_URL = "https://arena.sarus.app/api/v1"

def test_chat():
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")

    # Connect to arena
    client = Client(username=user, password=password, base_url=BASE_URL)
    
    # Set the credentials
    client.openai_api_key(os.getenv("ARENA_OPENAI_API_KEY"))

    # Run a query
    resp = client.chat_completions(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ])
    assert(resp.choices[0].message.role == "assistant")
    print(f"\n{resp.choices[0].message.content}")

    # Mistral
    client.mistral_api_key(os.getenv("ARENA_MISTRAL_API_KEY"))
    resp = client.chat_completions(model="mistral-small", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ])
    assert(resp.choices[0].message.role == "assistant")
    print(f"\n{resp.choices[0].message.content}")

    # Anthropic
    client.anthropic_api_key(os.getenv("ARENA_ANTHROPIC_API_KEY"))
    resp = client.chat_completions(model="claude-2.0", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
    ], max_tokens=500)
    assert(resp.choices[0].message.role == "assistant")
    print(f"\n{resp.choices[0].message.content}")


def test_judge():
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")

    # Connect to arena
    client = Client(username=user, password=password, base_url=BASE_URL)
    
    # Set the credentials
    client.openai_api_key(os.getenv("ARENA_OPENAI_API_KEY"))

    # Run a query
    resp = client.chat_completions(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
        ], lm_config={
            "judge_evaluation": True,
        })
    assert(resp.choices[0].message.role == "assistant")
    print(f"\n{resp.choices[0].message.content}")

    # Mistral
    client.mistral_api_key(os.getenv("ARENA_MISTRAL_API_KEY"))
    resp = client.chat_completions(model="mistral-small", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
        ], lm_config={
            "judge_evaluation": True,
        })
    assert(resp.choices[0].message.role == "assistant")
    print(f"\n{resp.choices[0].message.content}")

    # Anthropic
    client.anthropic_api_key(os.getenv("ARENA_ANTHROPIC_API_KEY"))
    resp = client.chat_completions(model="claude-2.0", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
        ], max_tokens=500, lm_config={
            "judge_evaluation": True,
        })
    assert(resp.choices[0].message.role == "assistant")
    print(f"\n{resp.choices[0].message.content}")


def test_user_eval():
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")

    # Connect to arena
    client = Client(username=user, password=password, base_url=BASE_URL)
    
    # Set the credentials
    client.openai_api_key(os.getenv("ARENA_OPENAI_API_KEY"))

    # Run a query
    resp = client.chat_completions(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the fastest animal on earth?"},
        ], lm_config={
            "judge_evaluation": True,
        })
    print(client.evaluation(resp.id, 0.5))


def test_instruments():
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")

    # Connect to arena
    client = Client(username=user, password=password, base_url=BASE_URL)
    
    # Set the credentials
    client.openai_api_key(os.getenv("ARENA_OPENAI_API_KEY"))
    client.lm_config(LMConfig(judge_evaluation=True))

    req = ChatCompletionRequest(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"What are instrumental variables in statistics? ({randint(0, 100)})"},
        ])

    # Run a query but with instruments
    event = client.chat_completions_request(**req.model_dump(mode="json", exclude_none=True))
    
    resp = ChatCompletionResponse(id=f"abcd1234-{randint(0, 10000)}", model="gpt-3.5-turbo", choices=[Choice(index=0, message=Message(role="assistant", content="This is a dummy response"))])
    client.chat_completions_response(**ChatCompletionRequestEventResponse(request=req, request_event_id=event.id, response=resp).model_dump(mode="json", exclude_none=True))


def test_download_events():
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")

    # Connect to arena
    client = Client(username=user, password=password, base_url=BASE_URL)

    client.lm_config(lm_config=LMConfig(pii_removal=None, judge_evaluation=False, judge_with_pii=False))
    
    # Set the credentials
    client.openai_api_key(os.getenv("ARENA_OPENAI_API_KEY"))

    # Run a queries and evaluations
    for _ in range(5):
        resp = client.chat_completions(model="gpt-3.5-turbo", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the fastest animal on earth?"},
            ])
        client.evaluation(resp.id, 0.5)

    data = client.download_events()
    print(data)


def test_events():
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")

    # Connect to arena
    client = Client(username=user, password=password, base_url=BASE_URL)

    client.lm_config(lm_config=LMConfig(pii_removal=None, judge_evaluation=False, judge_with_pii=False))
    
    # Set the credentials
    client.openai_api_key(os.getenv("ARENA_OPENAI_API_KEY"))

    # Run a queries and evaluations
    for _ in range(5):
        resp = client.chat_completions(model="gpt-3.5-turbo", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the fastest animal on earth?"},
            ])
        client.evaluation(resp.id, 0.5)

    data = client.events()
    print(data[0])


def test_create_event():
    user = os.getenv("FIRST_SUPERUSER")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD")

    # Connect to arena
    client = Client(username=user, password=password, base_url=BASE_URL)

    client.lm_config(lm_config=LMConfig(pii_removal=None, judge_evaluation=False, judge_with_pii=False))
    
    # Set the credentials
    client.openai_api_key(os.getenv("ARENA_OPENAI_API_KEY"))

    client.event("testing", '["BAM"]', None, "abcd")

    data = client.events()
    print(data[0])