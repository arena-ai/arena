import os
from anyio import run
from app.services.masking import Analyzer, AnalyzerRequest, Anonymizer, AnonymizerRequest

def test_analyzer() -> None:
    client = Analyzer()
    response = run(client.analyze, AnalyzerRequest(
        text="Hello I am Henry Smith and my account IBAN is GB87 BARC 2065 8244 9716 55.",
        ))
    print(f"\n{response}")

# Uses: https://raw.githubusercontent.com/microsoft/presidio-research/master/presidio_evaluator/data_generator/raw_data/templates.txt
def test_anonymizer() -> None:
    analyzer = Analyzer()
    anonymizer = Anonymizer()
    print(anonymizer.url)
    text = """Hello I am Henry Smith and my account IBAN is GB87 BARC 2065 8244 9716 55."""
    analysis = run(analyzer.analyze, AnalyzerRequest(
        text=text,
        ))
    anonymous = run(anonymizer.anonymize, AnonymizerRequest(
        text=text, analyzer_results=analysis
        ))
    print(f"\n{anonymous}")