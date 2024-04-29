from pydantic import BaseModel, computed_field


class Value(BaseModel):
    @computed_field
    @property
    def type(self) -> str:
        return self.__class__.__name__


class Score(Value):
    value: float


class Evaluation(BaseModel):
    identifier: str
    value: Score

