#!/usr/bin/env bash
# docker/entrypoint.sh

echo "Waiting for Postgres…"
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USERNAME"; do
  sleep 1
done

echo "Postgres is up – running migrations"
python manage.py migrate --noinput

exec "$@"
