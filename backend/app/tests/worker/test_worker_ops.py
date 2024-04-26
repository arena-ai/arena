from app.worker import evaluate

from app.ops.lm import Chat
from app.lm.models import ChatCompletionRequest, Message

def test_evaluate(language_models_api_keys):
    lm = Chat()
    comp = lm(language_models_api_keys, ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is the capital of France? Give it a score strictly between 0 and 10. Do the same with London.")
        ]
    )).content
    immediate_result = evaluate(comp)
    deferred_result = evaluate.delay(comp)
    print(f"\immediate_result = {immediate_result.choices[0].message.content}")
    print(f"\ndeferred_result = {deferred_result.get().choices[0].message.content}")