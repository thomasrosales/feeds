FROM python:3.9-slim-bullseye as python

ARG SYNC_ARGS

RUN mkdir /app \
    && mkdir /app/scripts \
    && mkdir /app/feeds_for_sendcloud \
    && mkdir -p /app/config

COPY . /app
COPY ./docker/scripts /app/scripts

WORKDIR /app

RUN pip install poetry \
    && apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && poetry install ${SYNC_ARGS}

RUN chmod +rwx ./scripts/entrypoint.sh \
	&& chmod +rwx ./scripts/start.sh \
	&& chmod +rwx ./scripts/celery.sh \
	&& chmod +rwx ./scripts/celery_beat.sh \
	&& chmod +rwx ./scripts/flower.sh

ENTRYPOINT ["./scripts/entrypoint.sh"]
