from pydantic import BaseModel


class Score(BaseModel):
    value: float


class Evaluation(BaseModel):
    identifier: str
    score: Score

