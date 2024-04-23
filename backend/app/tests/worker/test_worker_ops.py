from app.worker import evaluate

from app.ops.utils import var
from app.ops.lm import Chat
from app.lm.models import ChatCompletionCreate, Message

def test_evaluate(language_models_api_keys):
    lm = Chat(api_keys=language_models_api_keys)
    comp = lm(var("chat_completion_create", ChatCompletionCreate(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France? Give it a score between 0 and 10. Do the same with London.")
        ]
    )))
    imediate_result = evaluate(comp)
    deferred_result = evaluate.delay(comp)
    print(f"\nimediate_result = {imediate_result.choices[0].message.content}")
    print(f"\ndeferred_result = {deferred_result.get().choices[0].message.content}")