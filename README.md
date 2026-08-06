# Todo App

A small full-stack todo app.

- **Backend** — Flask + SQLAlchemy + SQLite ([backend/](backend/))
- **Frontend** — React 19 + Vite ([frontend/](frontend/))

## Quick start (Docker, recommended)

```bash
docker compose up --build
# open http://localhost:8080
```

## Local development

**Backend** (port `5001`):

```bash
cd backend
uv sync
uv run flask --app wsgi run --debug --port 5001
uv run pytest      # 16 tests
```

**Frontend** (port `5173`):

```bash
cd frontend
npm install
npm run dev
```

See [backend/README.md](backend/README.md) for the API contract.

## Project layout

```
backend/    Flask JSON API (app factory + blueprints)
frontend/   React SPA (Vite + plain CSS)
docker-compose.yml
.github/rules/   Coding standards for backend, frontend, DB
```
