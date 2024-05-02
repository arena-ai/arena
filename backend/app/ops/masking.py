from typing import Mapping
from faker import Faker
from app.lm.models import LanguageModelsApiKeys, ChatCompletionResponse, ChatCompletionRequest, Message, openai, mistral, anthropic, Score
from app.services.masking import Analyzer, AnalyzerRequest, Anonymizer, AnonymizerRequest, Anonymizers, Replace, Redact, Mask, Hash, Encrypt, Keep
from app.ops import Op


class Masking(Op[str, str]):
    async def call(self, input: str) -> str:
        analyzer = Analyzer()
        anonymizer = Anonymizer()
        analysis = await analyzer.analyze(AnalyzerRequest(text=input))
        anonymized = await anonymizer.anonymize(AnonymizerRequest(
            text=input,
            anonymizers=Anonymizers(DEFAULT=Replace()),
            analyzer_results=analysis,
        ))
        return anonymized.text


class ReplaceMasking(Op[str, tuple[str, Mapping[str, str]]]):
    fake = Faker()

    def replace_person(self, person: str) -> str:
        self.fake.seed_instance(hash(person))
        return self.fake.name()

    async def call(self, input: str) -> str:
        analyzer = Analyzer()
        anonymizer = Anonymizer()
        analysis = await analyzer.analyze(AnalyzerRequest(text=input))
        anonymized = await anonymizer.anonymize(AnonymizerRequest(
            text=input,
            anonymizers=Anonymizers(
                PERSON=Keep(),
                DEFAULT=Replace()
                ),
            analyzer_results=analysis,
        ))
        mapping = {}
        for item in anonymized.items:
            if item.entity_type == "PERSON":
                # Compute a replacement value
                replacement = self.replace_person(item.text)
                # keeps track of the replacement
                mapping[replacement] = item.text
                anonymized.text = f"{anonymized.text[:item.start]}{replacement}{anonymized.text[item.end:]}"
        return anonymized.text, mapping