from sqlmodel import Session
from anyio import run

from app.ops.masking import Masking, ReplaceMasking

TEXT = """Hello I am Henry Smith and my account IBAN is GB87 BARC 2065 8244 9716 55, John Dean should have my phone number: +1-202-688-5500."""

def test_masking() -> None:
    masking = Masking()
    text = TEXT
    result = masking(text)
    print(f"Computation = {result}")
    print(run(result.evaluate))


def test_replace_masking() -> None:
    synth_masking = ReplaceMasking()
    text = TEXT
    result = synth_masking(text)
    print(f"Computation = {result}")
    print(run(result.evaluate))