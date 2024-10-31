from anyio import run

from app.ops.masking import Masking, ReplaceMasking


def test_masking(text_with_pii) -> None:
    masking = Masking()
    text = text_with_pii
    result = masking(text)
    print(f"Computation = {result}")
    print(run(result.evaluate))


def test_replace_masking(text_with_pii) -> None:
    synth_masking = ReplaceMasking()
    text = text_with_pii
    result = synth_masking(text)
    print(f"Computation = {result}")
    print(run(result.evaluate))
