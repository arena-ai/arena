from app.ops import Op
from app.lm.models import ChatCompletion, ChatCompletionCreate
from app.lm import services


class Arena(Op[ChatCompletionCreate, ChatCompletion]):
    service: services.Arena

    def call(self, input: ChatCompletionCreate) -> ChatCompletion:
        return service