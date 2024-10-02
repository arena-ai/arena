from pydantic import BaseModel
from faker import Faker
fake = Faker()
import numpy as np
import matplotlib.pyplot as plt
from hf_inference.inference import LanguageModel

class TreatmentData(BaseModel):
    name: str
    treatment: bool
    measurement: float

    @classmethod
    def generate_random_instance(cls) -> 'TreatmentData':
        name = fake.name()
        treatment = np.random.choice([False, True], p=[0.9, 0.1])
        measurement = np.random.gamma(1, 10) if treatment else np.random.gamma(10, 1)
        return TreatmentData(name=name, treatment=treatment, measurement=measurement)

    @classmethod
    def generate(cls, size: int) -> list['TreatmentData']:
        return [TreatmentData.generate_random_instance() for _ in range(size)]
    
    def describe(self, language_model: LanguageModel) -> str:
        pass

