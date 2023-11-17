#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

postgres_ready() {
poetry run python << END
import environ
import psycopg2
import sys
env = environ.Env()
db = env.db()

try:
    psycopg2.connect(
        dbname=db['NAME'],
        user=db['USER'],
        password=db['PASSWORD'],
        host=db['HOST'],
        port=db['PORT'],
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}
until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'

exec "$@"

