from typing import Literal
import os
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
import transformers
from huggingface_hub import get_inference_endpoint, InferenceEndpoint

class Message(BaseModel):
	role: Literal["system", "user", "assistant"]
	content: str

	def __repr__(self) -> str:
		return f"""<|start_header_id|>{self.role}<|end_header_id|>{self.content}<|eot_id|>"""

class LanguageModel(BaseModel):
	name: str
	namespace: str = "sarus-tech"
	
	def _inference_endpoint(self) -> InferenceEndpoint:
		return get_inference_endpoint(self.name, namespace=self.namespace)

	def generate(self, prompt: str) -> str:
		return self._inference_endpoint().client.text_generation(prompt)

lm = LanguageModel(name="hf-inference")

resp = lm.generate('''<|begin_of_text|><|start_header_id|>system<|end_header_id|>

# Cutting Knowledge Date: December 2023
# Today Date: 23 July 2024

# You are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>

# What is the capital of France?<|eot_id|><|start_header_id|>assistant<|end_header_id|>

# I am not sure, it is one of the following'''
)

print(resp)