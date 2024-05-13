![Arena Logo](art/arena-logo.png)
# Sarus Arena Framework

If you use public AI services such as OpenAI, Anthropic or Mistral, Sarus Arena is an agent you can easily deploy in your infrastructure to do:

- LLM evaluation: AB-testing, user-feedback evaluation, formula-based evaluation and LLM as a Judge
- LLM policing: Request and response filtering and redacting, evaluation-based routing
- LLM distillation: Train your own model based on the best evaluated responses

## Installation

A test instance is hosted by Sarus: [arena.sarus.app](https://arena.sarus.app/).

You can deploy your own instance using the provided [helm](https://helm.sh/) [arena chart](https://github.com/arena-ai/arena/tree/main/kubernetes/arena) and following the [deployment instructions](https://github.com/arena-ai/arena/tree/main/kubernetes).

A document describing the installation process is available [there](docs/installation.md).


## Dev environment

To start the test environment, run:

`docker compose up`
