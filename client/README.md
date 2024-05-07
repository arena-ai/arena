# Client

## Run tests

Run `poetry install; poetry shell`

Then (e.g.):

`pytest -s tests/test_client.py::test_user_eval`

FAILED tests/test_anthropic.py::test_chat - AttributeError: 'Anthropic' object has no attribute 'chat'
FAILED tests/test_anthropic.py::test_instrumented_chat - AttributeError: 'Anthropic' object has no attribute 'chat'
FAILED tests/test_mistral.py::test_chat - AttributeError: 'function' object has no attribute 'completions'
FAILED tests/test_mistral.py::test_instrumented_chat - AttributeError: 'MistralClient' object has no attribute 'api_key'