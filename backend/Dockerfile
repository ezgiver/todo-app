FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN pip install --no-cache-dir uv

WORKDIR /app

# Install deps first (cached) — copy lockfiles only.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

ENV PATH="/app/.venv/bin:$PATH" \
    FLASK_APP=wsgi.py

EXPOSE 5001

# Werkzeug is fine for this small app; swap for gunicorn if you outgrow it.
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5001"]
