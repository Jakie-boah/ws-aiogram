FROM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y curl \
    && curl -Ls https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/opt/venv

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen

FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:/root/.local/bin:$PATH"