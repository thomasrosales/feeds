FROM python:3.9-slim-bullseye AS python

ARG SYNC_ARGS

FROM python AS base

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
	&& chmod +rwx ./scripts/flower.sh \
    && chmod +rwx ./scripts/test.sh

ENTRYPOINT ["./scripts/entrypoint.sh"]


FROM base AS testing
ENV DATABASE_URL=sqlite:///db.sqlite
ENV CELERY_BROKER_URL=""
ENV SQLLITE=True
COPY --from=base /app .
WORKDIR /app
ENTRYPOINT ["./scripts/test.sh"]
