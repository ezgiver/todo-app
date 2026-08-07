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
uv run pytest      # 30 tests
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
render.yaml              Render deployment config (Blueprint)
.github/workflows/ci.yml GitHub Actions CI
.github/rules/           Coding standards for backend, frontend, DB
```

## Deploy (Render, free tier)

Auto-deploys on merge to `main`. Free tier is fully free — no credit card, no surprises.

**Tradeoffs of the free plan:**
- Service **spins down after 15 min idle**; first request after that takes ~30–60 s to wake up.
- **Ephemeral filesystem** — the SQLite DB resets on every redeploy and after long idle. Fine for a demo; not for real data.

**One-time setup:**

1. Sign up at https://render.com (GitHub sign-in works, no card required).
2. Dashboard → **New +** → **Blueprint** → select `ezgiver/todo-app` → **Apply**.
3. Render reads [render.yaml](render.yaml) and [Dockerfile](Dockerfile), builds, and deploys.
4. **Set `SECRET_KEY` as a Render secret** (dashboard → service → Environment) — the app refuses to start without it. Generate one with:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
5. Live URL will be `https://todo-app-ezgiver.onrender.com` (Render will suggest a suffix if the name is taken).

**Every future push to `main` auto-deploys.** Watch progress at https://dashboard.render.com.

**Upgrading later (if you want persistence):** add a paid disk in `render.yaml` (`plan: starter` + `disk:` block) or move `DATABASE_URL` to Render's free Postgres.
