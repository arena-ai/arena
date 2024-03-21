FROM python:3.10-slim-bookworm

WORKDIR /app/

# Install Poetry
RUN pip install poetry

# Configure poetry
RUN poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry install --no-root --only main

ENV PYTHONPATH=/app

COPY ./scripts/ /app/

COPY ./alembic.ini /app/

COPY ./prestart.sh /app/

COPY ./tests-start.sh /app/

COPY ./app /app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]