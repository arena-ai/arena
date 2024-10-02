# Ideas

Compute similarity distance with LLMs, using summed-log-probs of the completion of:
```
Produce a test similar to this one "<Text A>"
---
"<Text B>"
```

Or by computing the log-prob of the token expressing the similarity vs absense of similarity

```
Are these text similar?
"<Text A>"
"<Text B>"
---
Yes
```

```
Are these text similar?
"<Text A>"
"<Text B>"
---
No
```