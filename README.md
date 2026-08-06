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
Dockerfile               Production image (builds frontend + serves via Flask)
docker-compose.yml       Local dev orchestration
fly.toml                 Fly.io deployment config
.github/workflows/ci.yml GitHub Actions CI
.github/rules/           Coding standards for backend, frontend, DB
```

## Deploy (Fly.io)

Auto-deploys on merge to `main` via Fly's GitHub integration.

**One-time setup:**

1. Create the app on https://fly.io/dashboard → **Launch from GitHub** → select `ezgiver/todo-app`.
2. Fly reads [fly.toml](fly.toml) and [Dockerfile](Dockerfile), creates the volume (1 GB), and does the first deploy.
3. If the app name `todo-app-ezgiver` is taken, Fly prompts for a new one — update `app = ...` and `CORS_ORIGINS` in [fly.toml](fly.toml) accordingly.

**Every future push to `main` auto-deploys.**

Local diagnostics (optional, needs `brew install flyctl`):

```bash
fly logs                # tail production logs
fly status              # machine + volume status
fly ssh console         # shell into the running container
```
