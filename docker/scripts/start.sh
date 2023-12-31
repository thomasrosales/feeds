#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

poetry run python manage.py migrate --no-input
poetry run python manage.py collectstatic --noinput
poetry run python manage.py create_user_feeds_for_testing_purpose
poetry run gunicorn config.wsgi --bind 0.0.0.0:8000
