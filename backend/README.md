# Todo Backend (Flask JSON API)

Flask + SQLAlchemy + SQLite JSON API for the todo SPA.

## Layout

```
backend/
  app/
    __init__.py       # create_app() factory
    extensions.py     # db (SQLAlchemy) instance
    models/
      todo.py         # Todo model
    routes/
      todos.py        # /api/todos blueprint (stubbed with TODOs)
  config.py           # DevelopmentConfig / ProductionConfig
  wsgi.py             # entry point: `flask --app wsgi run`
  pyproject.toml
```

## Run locally

```bash
cd backend
uv sync
uv run flask --app wsgi run --debug
# API listens on http://127.0.0.1:5000
```

## Endpoints

Base URL: `/api/todos`

| Method | Path                | Body                                 | Success | Errors     | Status |
|--------|---------------------|--------------------------------------|---------|------------|--------|
| GET    | `/api/todos`        | —                                    | 200     | 500        | done   |
| POST   | `/api/todos`        | `{ "title": "string", "due_at"?: str }` | 201  | 400        | TODO   |
| GET    | `/api/todos/<id>`   | —                                    | 200     | 404        | TODO   |
| PATCH  | `/api/todos/<id>`   | `{ "title"?: str, "completed"?: bool, "due_at"?: str|null }` | 200  | 400, 404   | TODO   |
| DELETE | `/api/todos/<id>`   | —                                    | 204     | 404        | TODO   |

### Todo shape

```json
{
  "id": 1,
  "title": "Buy milk",
  "completed": false,
  "due_at": null,
  "created_at": "2026-08-06T10:00:00",
  "updated_at": "2026-08-06T10:00:00"
}
```

### Error shape

```json
{ "error": "human readable message" }
```

## Environment

Copy `.env.example` to `.env` and adjust. Supported vars:

- `DATABASE_URL` — SQLAlchemy URL (default `sqlite:///todo.db` under `instance/`).
- `CORS_ORIGINS` — comma-separated allowed origins (default `http://localhost:5173`).

## What's left to implement

Open [app/routes/todos.py](app/routes/todos.py) — each stubbed handler currently returns `501 not implemented` and has a numbered `TODO` list describing exactly what to write.
