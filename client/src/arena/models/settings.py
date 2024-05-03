from typing import Literal
from pydantic import BaseModel

# A LM config setting
class LMConfig(BaseModel):
    pii_removal: Literal["masking", "replace"] | None = None
    judge_evaluation: bool = False
