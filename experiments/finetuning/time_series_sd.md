---
title: Quickly Generate Time-Series Synthetic Data with OpenAI's Fine-Tuning API
---

Yesterday, a friend mentioned that he's organizing a hackathon for students focused on machine learning.
He has some great data from a retailer and interesting questions about customer purchase patterns.
The challenge, however, is that he cannot disclose any personal data, and unfortunately for him high dimensional time-series data cannot be anonymized so easily.
Indeed the simplest approaches, such as pseudonymization, are dangerously weak when it comes to time-series, because a purchase trajectory is almost a signature.

In this situation, synthetic data can help.
Modern generative models can help us generate records with the same probability distribution as those of a given dataset.
In our case, we are talking about a high dimensional distribution in a time-series space, which can be challenging.

Because we are time-constrained and want to quickly come-up with something we tried to use a public LLM: OpenAI GPT-4 for the task.
In this post, we show on a public time-series dataset that few-shot learning is not so easy to get right for such a task.
But that, in contrast, fine-tuning is surprisingly useful.

# Few-Shot Learning from Time Series

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
        {"role": "system", "content": """You are a synthetic data generator,
you generate 10 rows similar to the user examples, but not equal.
You output the rows without more comment."""},
        {"role": "user", "content": "\n".join([json.dumps([round(1000*x)/1000 for x in series["target"][:100]]) for series in dataset["train"]][:10])},
]}
```
We submit this prompt and get 10 generated series.
Unfortunately, although not exactly equal, the generated series are almost identical to the ones we input.

![identical](/images/identical_2.png "Original and generated series are identical").

After several unsuccessful attempts and prompting strategies, some where the output format was not respected, some with shorter than expected series, some with totally random values, and because the length of the context forces me to select only a few example to teach GPT-4 to generate new examples, I realize few-shot learning may not be fit for the task.

It's time to get back to the good old gradient descent, I will test [OpenAI fine-tuning API](https://platform.openai.com/docs/guides/fine-tuning).

# Fine-Tuning GPT-3.5-turbo into a Specialized Time-Series Generator

Based on the same dataset ([hourly electricity consumption](https://huggingface.co/datasets/LeoTungAnh/electricity_hourly)), we generate a training split and a validation split suitable for the fine-tuning API.

```python
from typing import Any
import json

SYSTEM_PROMPT = "Given a meter ID, you return a series of hourly consumptions given as a json string."

def format(series: Any) -> str:
    return json.dumps({"messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps({"item_id": series["item_id"]})},
        {"role": "assistant", "content": json.dumps({"consumption": [round(1000*x)/1000 for x in series["target"][:100]]})}
    ]})+"\n"

with open(TRAIN_PATH, "w") as f:
    for series in dataset["train"]:
        f.write(format(series))

with open(TEST_PATH, "w") as f:
    for series in dataset["test"]:
        f.write(format(series))
```

We upload the files and launch the fine-tuning job.

```python
from openai import OpenAI

client = OpenAI()

with open(TRAIN_PATH, "rb") as f:
  train_file = client.files.create(file=f, purpose="fine-tune")

with open(TEST_PATH, "rb") as f:
  test_file = client.files.create(file=f, purpose="fine-tune")

fine_tuning_job = client.fine_tuning.jobs.create(
  training_file=train_file.id,
  hyperparameters={"batch_size": 2, "learning_rate_multiplier":2, "n_epochs": 10},
  validation_file=test_file.id,
  suffix="arena",
  model="gpt-3.5-turbo"
)

```
![loss](/images/loss.png "After a few epochs, the loss was slightly reduced").

We can then generate new series:

```python
def format_query(item_id: int) -> Any:
    return {"model": model, "temperature": 1.1, "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps({"item_id": f"MT_{item_id}"})},
    ]}

completion = client.chat.completions.create(**format_query(10))

print(completion.choices[0].message)
```

## We can check that the generated series are all rather different from the series from the training set

By comparing each generated series to its closest element in the training dataset (closest in the $l^2$-norm sense), we show that all the generated series are original (rather far from their closest element in the training set).

<!-- ![close](/images/closest_1.png "Series are close but rather different"). -->
![close](/images/closest_2.png "Series are close but rather different").

## Nevertheless the generated data mimics most of the statistics of the training dataset

By computing basic statistics (mean, median, some percentiles) and some cross-correlations we show the generated series have a distribution relatively close to that of the original data.

![means](/images/means.png "Means are close").
![percentiles](/images/percentiles.png "Percentiles are close").
![cross corr](/images/cross_corr.png "Cross correlations are close").

# Conclusion 