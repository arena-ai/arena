#! /usr/bin/env bash

# Let the DB start
python /app/app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB and object Store
python /app/app/initial_data.py

# Migrate the response template from the old to the new formalison
python /app/app/migrations/response_templates.py

