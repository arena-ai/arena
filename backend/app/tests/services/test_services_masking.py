import os
from anyio import run
from app.services.masking import Analyzer, AnalyzerRequest

def test_analyzer() -> None:
    client = Analyzer()
    response = run(client.analyze, AnalyzerRequest(
        text="Hello I am Henry Smith and my account IBAN is FR123456789456456456.",
        language="EN",
        ))
    print(f"\n{response}")
