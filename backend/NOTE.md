# Arena backend

## Testing the backend

First launch the stack with: `docker compose --profile "*" up`
or `docker compose --profile "*" up -d` to run it in the background

To run the full stack (with all profiles, presidio, milvus etc) you have to run `docker compose --profile "*" up` 

Then run the tests with: `docker compose exec backend bash /app/tests-start.sh`

In case you need to init the DB: `docker compose exec backend bash /app/prestart.sh`

Or if you want to run a specific test: `docker compose exec backend bash /app/specific-tests-start.sh app/tests/api/routes/test_events.py::test_create_event`

## Testing some aspects of the backend

It can be costly to run the full stack in docker compose. You can run parts of the stack using profiles: `docker compose --profile milvus up`

Then run for example `docker compose exec backend bash /app/specific-tests-start.sh app/tests/services/test_services_object_store.py`

## The backend is pushed to github container registry (ghcr.io)

The backend image is built and pushed to ghcr.io, see in `.github/workflows/publish-backend-docker-image.yml`.

## Migrations

As during local development your app directory is mounted as a volume inside the container, you can also run the migrations with `alembic` commands inside the container and the migration code will be in your app directory (instead of being only inside the container). So you can add it to your git repository.

Make sure you create a "revision" of your models and that you "upgrade" your database with that revision every time you change them. As this is what will update the tables in your database. Otherwise, your application will have errors.

* Start an interactive session in the backend container:

```console
$ docker compose exec backend bash
```

* Alembic is already configured to import your SQLModel models from `./backend/app/models.py`.

* After changing a model (for example, adding a column), inside the container, create a revision, e.g.:

```console
$ alembic revision --autogenerate -m "Add column last_name to User model"
```

* Commit to the git repository the files generated in the alembic directory.

* After creating the revision, run the migration in the database (this is what will actually change the database):

```console
$ alembic upgrade head