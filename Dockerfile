# ---- Frontend build ----
FROM node:22-alpine AS frontend

WORKDIR /build

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

# Same-origin in prod: /api routes are served by Flask itself.
ENV VITE_API_URL=/api
RUN npm run build


# ---- Backend + serve ----
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

COPY backend/ ./

COPY --from=frontend /build/dist ./static

ENV PATH="/app/.venv/bin:$PATH" \
    STATIC_ROOT=/app/static \
    APP_CONFIG=config.ProductionConfig

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--access-logfile", "-", "wsgi:app"]
