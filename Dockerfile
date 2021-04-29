FROM python:3.8.5-slim-buster

ARG ENV

RUN pip3 install poetry

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false \
    && poetry install $(test "$ENV" == production && echo "--no-dev") --no-interaction --no-ansi

COPY . /app