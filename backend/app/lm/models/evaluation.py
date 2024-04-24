from pydantic import BaseModel


class Evaluation(BaseModel):
    identifier: str
    score: float
