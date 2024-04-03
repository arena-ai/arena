from app.lm.models import Choice, FinishReason, ChatCompletionMessage

def test_finish_reason() -> None:
    c = Choice.model_validate({
        "finish_reason": FinishReason.stop,
        "index": 0,
        "message": ChatCompletionMessage()
    })
    assert c.finish_reason == "stop"

