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
In this post, we show that few-shot learning is not so easy to get right for such a task.
But that, in contrast, fine-tuning is surprisingly useful.