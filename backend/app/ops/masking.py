from typing import Mapping
from pydantic import Field, ConfigDict
from faker import Faker
from app.services.masking import (
    Analyzer,
    AnalyzerRequest,
    Anonymizer,
    AnonymizerRequest,
    Anonymizers,
    Replace,
    Keep,
)
from app.ops import Op


class Masking(Op[str, str]):
    async def call(self, input: str) -> str:
        analyzer = Analyzer()
        anonymizer = Anonymizer()
        analysis = await analyzer.analyze(AnalyzerRequest(text=input))
        anonymized = await anonymizer.anonymize(
            AnonymizerRequest(
                text=input,
                anonymizers=Anonymizers(DEFAULT=Replace()),
                analyzer_results=analysis,
            )
        )
        return anonymized.text


masking = Masking()


class ReplaceMasking(Op[str, tuple[str, Mapping[str, str]]]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    fake: Faker = Field(exclude=True, default_factory=lambda: Faker())

    def replace_person(self, person: str, salt: str = "") -> str:
        self.fake.seed_instance(hash(person + salt))
        return self.fake.name()

    def replace_phone_number(self, phone_number: str, salt: str = "") -> str:
        self.fake.seed_instance(hash(phone_number + salt))
        return self.fake.phone_number()

    def replace_address(self, address: str, salt: str = "") -> str:
        self.fake.seed_instance(hash(address + salt))
        return self.fake.address()

    def replace_credit_card(self, credit_card: str, salt: str = "") -> str:
        self.fake.seed_instance(hash(credit_card + salt))
        return self.fake.credit_card_number()

    def replace_email_address(self, email_address: str, salt: str = "") -> str:
        self.fake.seed_instance(hash(email_address + salt))
        return self.fake.email()

    def replace_iban_code(self, iban_code: str, salt: str = "") -> str:
        self.fake.seed_instance(hash(iban_code + salt))
        return self.fake.iban()

    async def call(self, input: str) -> tuple[str, Mapping[str, str]]:
        analyzer = Analyzer()
        anonymizer = Anonymizer()
        #Passing only the relevant entities to the analyzer so the model searches for these specifically.
        entities = ["LOCATION","PERSON"]
        analysis = await analyzer.analyze(AnalyzerRequest(text=input, entities=entities))
        anonymized = await anonymizer.anonymize(AnonymizerRequest(
            text=input,
            anonymizers=Anonymizers(
                PERSON=Keep(),
                LOCATION=Keep(),
                EMAIL_ADDRESS=Keep()                                   
                ),
                analyzer_results=analysis,
            )
        )
        mapping = {}
        for item in anonymized.items:
            # Compute a replacement value
            if item.entity_type == "PERSON":
                replacement = self.replace_person(item.text, input)
            elif item.entity_type == "LOCATION":
                replacement = self.replace_address(item.text, input)
  
            mapping[replacement] = item.text
            anonymized.text = f"{anonymized.text[:item.start]}{replacement}{anonymized.text[item.end:]}"   
        return (anonymized.text, mapping)


replace_masking = ReplaceMasking()
