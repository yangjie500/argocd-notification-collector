# syntax=docker/dockerfile:1.7

FROM cgr.dev/chainguard/python:latest-dev AS build

USER root
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV PATH="/app/.venv/bin:${PATH}"
ENV UV_PYTHON_DOWNLOADS=never
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md LICENSE /app/
COPY src /app/src
COPY .git /app/.git

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-dev --python /usr/bin/python

RUN chmod -R a+rX /app/.venv \
    && chmod -R a+rx /app/.venv/bin

FROM cgr.dev/chainguard/python:latest-dev AS debug

USER root
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
COPY --from=build /app /app
COPY pyproject.toml uv.lock README.md LICENSE /app/
COPY src /app/src

ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN uv pip install debugpy \
    && uv pip install -e .

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["while true; do sleep 30; done"]

FROM cgr.dev/chainguard/python:latest-dev AS runtime

USER root
RUN apk add --no-cache bash

WORKDIR /app

COPY --from=build --chown=65532:0 /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

USER 65532

EXPOSE 8000

ENTRYPOINT ["event-collector"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8000"]
