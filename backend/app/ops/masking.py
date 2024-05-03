from typing import Mapping
from pydantic import Field, ConfigDict
from faker import Faker
from app.lm.models import LMApiKeys, ChatCompletionResponse, ChatCompletionRequest, Message, openai, mistral, anthropic, Score
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

masking = Masking()

class ReplaceMasking(Op[str, tuple[str, Mapping[str, str]]]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    fake: Faker = Field(exclude=True, default_factory=lambda: Faker())

    def replace_person(self, person: str) -> str:
        self.fake.seed_instance(hash(person))
        return self.fake.name()

    def replace_phone_number(self, phone_number: str) -> str:
        self.fake.seed_instance(hash(phone_number))
        return self.fake.phone_number()

    def replace_address(self, phone_number: str) -> str:
        self.fake.seed_instance(hash(phone_number))
        return self.fake.address()

    def replace_credit_card(self, phone_number: str) -> str:
        self.fake.seed_instance(hash(phone_number))
        return self.fake.credit_card_number()

    def replace_email_address(self, phone_number: str) -> str:
        self.fake.seed_instance(hash(phone_number))
        return self.fake.email()

    def replace_iban_code(self, phone_number: str) -> str:
        self.fake.seed_instance(hash(phone_number))
        return self.fake.iban()

    async def call(self, input: str) -> tuple[str, Mapping[str, str]]:
        analyzer = Analyzer()
        anonymizer = Anonymizer()
        analysis = await analyzer.analyze(AnalyzerRequest(text=input))
        anonymized = await anonymizer.anonymize(AnonymizerRequest(
            text=input,
            anonymizers=Anonymizers(
                PERSON=Keep(),
                PHONE_NUMBER=Keep(),
                LOCATION=Keep(),
                CREDIT_CARD=Keep(),
                EMAIL_ADDRESS=Keep(),
                IBAN_CODE=Keep(),
                DEFAULT=Replace()
                ),
            analyzer_results=analysis,
        ))
        mapping = {}
        for item in anonymized.items:
            # Compute a replacement value
            if item.entity_type == "PERSON":
                replacement = self.replace_person(item.text)
            elif item.entity_type == "PHONE_NUMBER":
                replacement = self.replace_person(item.text)
            elif item.entity_type == "LOCATION":
                replacement = self.replace_address(item.text)
            elif item.entity_type == "CREDIT_CARD":
                replacement = self.replace_credit_card(item.text)
            elif item.entity_type == "EMAIL_ADDRESS":
                replacement = self.replace_email_address(item.text)
            elif item.entity_type == "IBAN_CODE":
                replacement = self.replace_iban_code(item.text)
            else:
                replacement = item.text
            # keeps track of the replacement
            if replacement != item.text:
                mapping[replacement] = item.text
            anonymized.text = f"{anonymized.text[:item.start]}{replacement}{anonymized.text[item.end:]}"
        return (anonymized.text, mapping)

replace_masking = ReplaceMasking()