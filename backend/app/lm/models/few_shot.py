from pydantic import BaseModel

class DocFewShot(BaseModel):
    prompt: str
    doc_examples: list[(str, str)]
