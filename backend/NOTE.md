# Arena backend

## Testing the backend

First launch the stack with: `docker compose up`
or `docker compose up -d` to run it in the background

Then run the tests with: `docker compose exec backend bash /app/tests-start.sh`

In case you need to init the DB: `docker compose exec backend bash /app/prestart.sh`

Or if you want to run a specific test: `docker compose exec backend bash /app/specific-tests-start.sh app/tests/api/routes/test_events.py::test_create_event`
