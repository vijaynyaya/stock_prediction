FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

ADD . /app

RUN uv sync

EXPOSE 8000

ENTRYPOINT [ "uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]