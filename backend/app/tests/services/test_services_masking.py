import os
from anyio import run
from app.services.masking import Analyzer, AnalyzerRequest, Anonymizer, AnonymizerRequest, Anonymizers, Replace, Redact, Mask, Hash, Encrypt, Keep

TEXT = """Hello I am Henry Smith and my account IBAN is GB87 BARC 2065 8244 9716 55, John Dean should have my phone number: +1-202-688-5500."""

def test_analyzer() -> None:
    client = Analyzer()
    response = run(client.analyze, AnalyzerRequest(
        text=TEXT,
        ))
    print(f"\n{response}")

# Uses: https://raw.githubusercontent.com/microsoft/presidio-research/master/presidio_evaluator/data_generator/raw_data/templates.txt
def test_anonymizer() -> None:
    analyzer = Analyzer()
    anonymizer = Anonymizer()
    print(anonymizer.url)
    analysis = run(analyzer.analyze, AnalyzerRequest(
        text=TEXT,
        ))
    anonymous = run(anonymizer.anonymize, AnonymizerRequest(
        text=TEXT,
        anonymizers=Anonymizers(
            PERSON=Keep(),
            DEFAULT=Replace(),
        ),
        analyzer_results=analysis,
        ))
    print(f"\n{anonymous}")