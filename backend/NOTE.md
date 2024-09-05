# Arena backend

## Testing the backend

First launch the stack with: `docker compose up`
or `docker compose up -d` to run it in the background

To run the full stack (with all profiles, presidio, milvus etc) you have to run `docker compose --profile "*" up` 

Then run the tests with: `docker compose exec backend bash /app/tests-start.sh`

In case you need to init the DB: `docker compose exec backend bash /app/prestart.sh`

Or if you want to run a specific test: `docker compose exec backend bash /app/specific-tests-start.sh app/tests/api/routes/test_events.py::test_create_event`

## Testing some aspects of the backend

It can be costly to run the full stack in docker compose. You can run parts of the stack using profiles: `docker compose --profile milvus up`

Then run for example `docker compose exec backend bash /app/specific-tests-start.sh /app/tests/services/test_services_object_store.py`

## The backend is pushed to github container registry (ghcr.io)

The backend image is built and pushed to ghcr.io, see in `.github/workflows/publish-backend-docker-image.yml`.
