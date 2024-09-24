import os
from dotenv import load_dotenv
load_dotenv()
import transformers
from huggingface_hub import get_inference_endpoint

endpoint = get_inference_endpoint("hf-inference", namespace="sarus-tech")

# print(endpoint.client.text_generation(prompt="The capital of France is", details=False, do_sample=True, max_new_tokens=100, temperature=1))

resp = chat_completion = endpoint.client.text_generation(
	prompt='''<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Cutting Knowledge Date: December 2023
Today Date: 23 July 2024

You are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>

What is the capital of France?<|eot_id|><|start_header_id|>assistant<|end_header_id|>

I am not sure, it is one of the following''',
)

print(resp)