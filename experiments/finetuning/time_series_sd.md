---
title: Quickly Generate Time-Series Synthetic Data with OpenAI's Fine-Tuning API
---

Yesterday, a friend mentioned that he's organizing a hackathon for students focused on machine learning.
He has some great data from a retailer and interesting questions about customer purchase patterns.
The challenge, however, is that he cannot disclose any personal data, and unfortunately for him high dimensional
time-series data cannot be anonymized so easily.
Indeed the simplest approaches, such as pseudonymization, are dangerously weak when it comes to time-series, because a purchase trajectory is almost a signature.

In this situation, synthetic data can help.
Modern generative models can help us generate records with the same probability distribution as those of a given dataset.
In our case, we are talking about a high dimensional distribution in a time-series space, which can be challenging.

Because we are time-constrained and want to quickly come-up with something we tried to use a public LLM: OpenAI GPT-4 for the task.
In this post, we show on a similar dataset that few-shot learning is not so easy to get right for such a task.
But that, in contrast, fine-tuning is surprisingly useful.

# Few-Shot Learning from a Thousand Time Series

To test different approaches, we build a time-series dataset from a public dataset of [hourly electricity consumption](https://huggingface.co/datasets/LeoTungAnh/electricity_hourly).

```python
import json
from datasets import load_dataset

dataset = load_dataset("LeoTungAnh/electricity_hourly")

with open("few_shots.jsonl", "w") as f:
    for series in dataset["train"]:
        f.write(json.dumps([round(1000*x)/1000 for x in series["target"][:100]])+"\n")
```
We then build a prompt with 10 examples:
```python
prompt = {"model": "gpt-4-turbo", "temperature": 0.8, "max_tokens": 4096, "messages": [
        {"role": "system", "content": """You are a synthetic data generator, you generate 10 rows similar to the user examples, but not equal.
You output the rows without more comment."""},
        {"role": "user", "content": "\n".join([json.dumps([round(1000*x)/1000 for x in series["target"][:100]]) for series in dataset["train"]][:10])},
]}
```
We submit this prompt and get 10 generated series.
Unfortunately, although not exactly equal, the generated series are almost identical to the ones we 